import * as THREE from 'three';

const MAX_WAVES = 4;
const PLANE_SEGMENTS = 160;
const DEFAULT_WAVE = [0, 1, 0, 1, 0.35];

const vertexShader = `
uniform float time;
uniform vec4 waves[4];
uniform float waveSpeeds[4];
uniform float wavePhaseOffsets[4];
uniform float waveCount;
uniform vec4 shoreFade;

varying vec3 vWorldPosition;
varying vec3 vNormal;
varying float vShoreDistance;

void main() {
  vec3 displacedPosition = position;
  vec3 tangentX = vec3(1.0, 0.0, 0.0);
  vec3 tangentZ = vec3(0.0, 0.0, 1.0);
  float shoreDistance = 1.0;
  int activeWaves = int(clamp(waveCount + 0.5, 0.0, 4.0));
  bool hasBoundary = shoreFade.y > shoreFade.x && shoreFade.w > shoreFade.z;

  if (hasBoundary) {
    float distanceX = min(displacedPosition.x - shoreFade.x, shoreFade.y - displacedPosition.x);
    float distanceZ = min(displacedPosition.z - shoreFade.z, shoreFade.w - displacedPosition.z);
    float distanceToEdge = min(distanceX, distanceZ);
    float fadeWidth = max(min(shoreFade.y - shoreFade.x, shoreFade.w - shoreFade.z) * 0.05, 0.001);
    shoreDistance = clamp(distanceToEdge / fadeWidth, 0.0, 1.0);
  }

  for (int index = 0; index < 4; index += 1) {
    if (index >= activeWaves) {
      continue;
    }

    vec4 wave = waves[index];
    vec2 direction = wave.xy;
    direction /= max(length(direction), 0.0001);
    float amplitude = wave.z;
    float wavelength = max(wave.w, 0.0001);
    float frequency = 6.28318530718 / wavelength;
    float phase = 6.28318530718 * (
      dot(direction, displacedPosition.xz) / wavelength
      - waveSpeeds[index] * time / wavelength
    ) + wavePhaseOffsets[index];
    float sine = sin(phase);
    float cosine = cos(phase);

    displacedPosition.y += amplitude * sine;
    tangentX.y += amplitude * cosine * frequency * direction.x;
    tangentZ.y += amplitude * cosine * frequency * direction.y;
  }

  vec3 normal = normalize(cross(tangentZ, tangentX));
  vec4 worldPosition = modelMatrix * vec4(displacedPosition, 1.0);

  vWorldPosition = worldPosition.xyz;
  vNormal = normalize(mat3(modelMatrix) * normal);
  vShoreDistance = shoreDistance;
  gl_Position = projectionMatrix * viewMatrix * worldPosition;
}
`;

const fragmentShader = `
uniform vec3 sunDirection;
uniform vec3 baseColor;
uniform vec3 foamColor;
uniform vec4 shoreFade;

varying vec3 vWorldPosition;
varying vec3 vNormal;
varying float vShoreDistance;

void main() {
  vec3 normal = normalize(vNormal);
  vec3 lightDirection = normalize(sunDirection);
  vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
  float diffuse = 0.5 + 0.5 * max(dot(normal, lightDirection), 0.0);
  float fresnel = pow(1.0 - max(dot(normal, viewDirection), 0.0), 3.0);
  float shoreMask = smoothstep(0.0, 1.0, vShoreDistance);
  vec3 waterColor = baseColor * (0.68 + 0.32 * diffuse);
  vec3 color = mix(foamColor, waterColor, shoreMask);
  color += foamColor * fresnel * 0.18;
  gl_FragColor = vec4(color, 1.0);
}
`;

function finiteNumber(value, fallback) {
  return Number.isFinite(value) ? value : fallback;
}
function vector4FromValues(three, values) {
  if (typeof three.Vector4 === 'function') {
    return new three.Vector4(values[0], values[1], values[2], values[3]);
  }

  return values.slice(0, 4);
}

function waveToUniform(wave) {
  if (Array.isArray(wave)) {
    return {
      vector: [
        finiteNumber(wave[0], 0),
        finiteNumber(wave[1], 1),
        finiteNumber(wave[2], 0),
      Math.max(finiteNumber(wave[3], 12), 0.0001),
      ],
      speed: finiteNumber(wave[4], 0.35),
      phaseOffset: finiteNumber(wave[5], 0),
    };
  }

  if (!wave || typeof wave !== 'object') {
    return waveToUniform(DEFAULT_WAVE);
  }

  const direction = wave.direction || wave.dir || wave.vector || {};
  const directionX = Array.isArray(direction)
    ? direction[0]
    : direction.x;
  const directionZ = Array.isArray(direction)
    ? direction[1]
    : (direction.z === undefined ? direction.y : direction.z);
  const amplitude = finiteNumber(wave.amplitude, finiteNumber(wave.height, 0));
  const wavelength = finiteNumber(wave.wavelength, 12);
  const speed = finiteNumber(wave.speed, finiteNumber(wave.phaseSpeed, 0.35));
  const phaseOffset = finiteNumber(wave.phaseOffset, 0);

  return {
    vector: [
      finiteNumber(wave.directionX, finiteNumber(directionX, 0)),
      finiteNumber(wave.directionZ, finiteNumber(directionZ, 1)),
      amplitude,
      Math.max(wavelength, 0.0001),
    ],
    speed,
    phaseOffset,
  };
}

function getWaveUniforms(waveField) {
  const source = waveField && typeof waveField.getShaderWaveData === 'function'
    ? waveField.getShaderWaveData()
    : [];
  const sourceWaves = Array.isArray(source) ? source.slice(0, MAX_WAVES) : [];
  const values = sourceWaves.map(waveToUniform);

  while (values.length < MAX_WAVES) {
    values.push(waveToUniform(DEFAULT_WAVE));
  }

  return {
    values,
    phaseOffsets: values.map((item) => item.phaseOffset),
    count: Math.min(Array.isArray(source) ? source.length : 0, MAX_WAVES),
  };
}

function boundaryToUniform(boundary) {
  if (!boundary || typeof boundary !== 'object') {
    return [0, 0, 0, 0];
  }

  return [
    finiteNumber(boundary.minX, 0),
    finiteNumber(boundary.maxX, 0),
    finiteNumber(boundary.minZ, 0),
    finiteNumber(boundary.maxZ, 0),
  ];
}

export class WaterSurface {
  constructor({
    THREE: three = THREE,
    waveField,
    width = 1,
    depth = 1,
    boundary,
  } = {}) {
    const safeWidth = Math.max(finiteNumber(width, 1), 0.001);
    const safeDepth = Math.max(finiteNumber(depth, 1), 0.001);
    const waveData = getWaveUniforms(waveField);
    const boundaryData = boundaryToUniform(boundary);
    const geometry = new three.PlaneGeometry(safeWidth, safeDepth, PLANE_SEGMENTS, PLANE_SEGMENTS);
    const sunDirection = new three.Vector3(0.35, 0.9, 0.2);
    sunDirection.normalize();
    const material = new three.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        waves: { value: waveData.values.map((item) => vector4FromValues(three, item.vector)) },
        waveSpeeds: { value: waveData.values.map((item) => item.speed) },
        wavePhaseOffsets: { value: waveData.phaseOffsets },
        waveCount: { value: waveData.count },
        sunDirection: { value: sunDirection },
        baseColor: { value: new three.Color(0.035, 0.28, 0.55) },
        foamColor: { value: new three.Color(0.55, 0.85, 0.95) },
        shoreFade: { value: vector4FromValues(three, boundaryData) },
      },
      vertexShader,
      fragmentShader,
      transparent: false,
      depthWrite: true,
    });

    // Mặt phẳng mặc định nằm trên XY; xoay -90 độ để trục Y là chiều cao.
    geometry.rotateX(-Math.PI / 2);
    this.object3D = new three.Mesh(geometry, material);
    this.object3D.name = 'WaterSurface';
    this.geometry = geometry;
    this.material = material;
    this.uniforms = material.uniforms;
    this._disposed = false;
  }

  update(timeSeconds) {
    if (this._disposed) {
      return;
    }

    this.uniforms.time.value = finiteNumber(timeSeconds, 0);
  }

  dispose() {
    if (this._disposed) {
      return;
    }

    this.geometry.dispose();
    this.material.dispose();
    this._disposed = true;
  }
}
