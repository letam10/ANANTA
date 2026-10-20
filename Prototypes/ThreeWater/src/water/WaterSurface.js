import * as THREE from "three";
import { GEOMETRIC_STEEPNESS } from "./WaveField.js";
import { getWaterProfile, WATER_PROFILES } from "./WaterProfiles.js";

const MAX_WAVES = 4;
const PLANE_SEGMENTS = 160;
const DEFAULT_WAVE = [0, 1, 0, 12, 0.35, 0.2];

export const VISUAL_WATER_PRESET = WATER_PROFILES.low;

const vertexShader = `
uniform float time;
uniform vec4 waves[4];
uniform float waveSpeeds[4];
uniform float wavePhaseOffsets[4];
uniform float waveSteepness[4];
uniform float waveCount;
uniform float amplitudeScale;
uniform float steepnessScale;
uniform vec4 shoreFade;

varying vec3 vWorldPosition;
varying vec3 vNormal;
varying float vShoreDistance;
varying float vCrest;
varying float vSlope;
varying float vFolding;

void main() {
  vec3 displacedPosition = position;
  vec3 tangentX = vec3(1.0, 0.0, 0.0);
  vec3 tangentZ = vec3(0.0, 0.0, 1.0);
  float crest = 0.0;
  float slope = 0.0;
  float folding = 0.0;
  int activeWaves = int(clamp(waveCount + 0.5, 0.0, 4.0));
  bool hasBoundary = shoreFade.y > shoreFade.x && shoreFade.w > shoreFade.z;

  for (int index = 0; index < 4; index += 1) {
    if (index >= activeWaves) {
      continue;
    }

    vec4 wave = waves[index];
    vec2 direction = normalize(wave.xy);
    float amplitude = wave.z * amplitudeScale;
    float wavelength = max(wave.w, 0.0001);
    float frequency = 6.28318530718 / wavelength;
    float phase = 6.28318530718 * (
      dot(direction, position.xz) / wavelength
      - waveSpeeds[index] * time / wavelength
    ) + wavePhaseOffsets[index];
    float sine = sin(phase);
    float cosine = cos(phase);
    float steepness = clamp(waveSteepness[index] * steepnessScale, 0.0, 0.95);
    float q = steepness / max(
      frequency * max(abs(amplitude), 0.0001) * max(float(activeWaves), 1.0),
      0.0001
    );
    float lateral = q * amplitude * cosine;
    float slopeTerm = amplitude * frequency * cosine;
    float crestTerm = q * amplitude * frequency * sine;

    displacedPosition.x += direction.x * lateral;
    displacedPosition.z += direction.y * lateral;
    displacedPosition.y += amplitude * sine;

    tangentX += vec3(
      -direction.x * direction.x * crestTerm,
      direction.x * slopeTerm,
      -direction.x * direction.y * crestTerm
    );
    tangentZ += vec3(
      -direction.x * direction.y * crestTerm,
      direction.y * slopeTerm,
      -direction.y * direction.y * crestTerm
    );
    crest += max(sine, 0.0);
    slope += abs(slopeTerm);
    folding += max(crestTerm, 0.0);
  }

  vec3 normal = normalize(cross(tangentZ, tangentX));
  float shoreDistance = 1.0;
  if (hasBoundary) {
    float distanceX = min(
      displacedPosition.x - shoreFade.x,
      shoreFade.y - displacedPosition.x
    );
    float distanceZ = min(
      displacedPosition.z - shoreFade.z,
      shoreFade.w - displacedPosition.z
    );
    float distanceToEdge = min(distanceX, distanceZ);
    float fadeWidth = max(
      min(shoreFade.y - shoreFade.x, shoreFade.w - shoreFade.z) * 0.05,
      0.001
    );
    shoreDistance = clamp(distanceToEdge / fadeWidth, 0.0, 1.0);
  }

  vec4 worldPosition = modelMatrix * vec4(displacedPosition, 1.0);
  vWorldPosition = worldPosition.xyz;
  vNormal = normalize(mat3(modelMatrix) * normal);
  vShoreDistance = shoreDistance;
  vCrest = crest / max(float(activeWaves), 1.0);
  vSlope = clamp(slope * 2.6, 0.0, 1.0);
  vFolding = clamp(folding * 1.35, 0.0, 1.0);
  gl_Position = projectionMatrix * viewMatrix * worldPosition;
}
`;

const fragmentShader = `
uniform float time;
uniform vec3 sunDirection;
uniform vec3 deepColor;
uniform vec3 shallowColor;
uniform vec3 reflectionColor;
uniform vec3 foamColor;
uniform float detailStrength;
uniform float detailScale;
uniform float detailSpeed;
uniform float fresnelPower;
uniform float reflectionStrength;
uniform float specularStrength;
uniform float horizonStrength;
uniform float subsurfaceStrength;
uniform float crestFoamStrength;
uniform float foldingFoamStrength;
uniform float foamScale;

varying vec3 vWorldPosition;
varying vec3 vNormal;
varying float vShoreDistance;
varying float vCrest;
varying float vSlope;
varying float vFolding;

void main() {
  vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
  vec3 lightDirection = normalize(sunDirection);
  vec3 normal = normalize(vNormal);
  float detailPhaseA = dot(vWorldPosition.xz, vec2(0.84, 0.54)) * detailScale
    + time * detailSpeed;
  float detailPhaseB = dot(vWorldPosition.xz, vec2(-0.42, 0.91)) * detailScale * 1.73
    - time * detailSpeed * 0.71;
  vec2 detailSlope = vec2(
    cos(detailPhaseA) * 0.52 + cos(detailPhaseB) * 0.24,
    sin(detailPhaseA) * 0.35 + sin(detailPhaseB) * 0.31
  );
  normal = normalize(normal + vec3(
    detailSlope.x * detailStrength,
    0.0,
    detailSlope.y * detailStrength
  ));

  float ndl = max(dot(normal, lightDirection), 0.0);
  float diffuse = 0.5 + 0.5 * ndl;
  float ndv = max(dot(normal, viewDirection), 0.0);
  float fresnel = pow(1.0 - ndv, fresnelPower);
  vec3 halfDirection = normalize(lightDirection + viewDirection);
  float specular = pow(max(dot(normal, halfDirection), 0.0), 96.0);
  float shore = 1.0 - smoothstep(0.04, 0.98, vShoreDistance);
  vec3 baseWater = mix(shallowColor, deepColor, smoothstep(0.08, 0.9, vShoreDistance));
  vec3 color = baseWater * (0.62 + 0.38 * diffuse);
  float skyGradient = clamp(viewDirection.y * 0.5 + 0.5, 0.0, 1.0);
  vec3 skyReflection = mix(reflectionColor * 0.58, vec3(0.82, 0.95, 1.0), skyGradient);
  color += skyReflection * fresnel * reflectionStrength;
  color += shallowColor * pow(max(dot(-lightDirection, viewDirection), 0.0), 3.0)
    * subsurfaceStrength * (0.35 + shore * 0.65);
  color += skyReflection * pow(1.0 - ndv, 2.0) * horizonStrength;
  color += vec3(1.0) * specular * specularStrength;

  float crestFoam = smoothstep(0.52, 0.92, vCrest) * crestFoamStrength * foamScale;
  float foldingFoam = smoothstep(0.08, 0.62, vFolding) * foldingFoamStrength * foamScale;
  float foamNoise = 0.72 + 0.28 * sin(
    dot(vWorldPosition.xz, vec2(0.16, -0.11)) + time * 1.4
  );
  float foamLace = 0.5 + 0.5 * sin(
    dot(vWorldPosition.xz, vec2(0.33, -0.22)) - time * 1.9 + vCrest * 3.0
  );
  float shoreFoam = shore * (0.34 + foamNoise * 0.38);
  float foamMask = shoreFoam + (crestFoam + foldingFoam) * (0.78 + foamLace * 0.22);
  foamMask = clamp(foamMask, 0.0, 0.9);
  color = mix(color, foamColor, foamMask);
  gl_FragColor = vec4(color, 1.0);
}
`;

function finiteNumber(value, fallback) {
  return Number.isFinite(value) ? value : fallback;
}

function vector4FromValues(three, values) {
  if (typeof three.Vector4 === "function") {
    return new three.Vector4(values[0], values[1], values[2], values[3]);
  }
  return values.slice(0, 4);
}

function waveToUniform(wave, index) {
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
      steepness: finiteNumber(wave[6], GEOMETRIC_STEEPNESS[index] ?? 0.2),
    };
  }

  if (!wave || typeof wave !== "object") {
    return waveToUniform(DEFAULT_WAVE, index);
  }

  const direction = wave.direction || wave.dir || wave.vector || {};
  const directionX = Array.isArray(direction) ? direction[0] : direction.x;
  const directionZ = Array.isArray(direction)
    ? direction[1]
    : (direction.z === undefined ? direction.y : direction.z);

  return {
    vector: [
      finiteNumber(wave.directionX, finiteNumber(directionX, 0)),
      finiteNumber(wave.directionZ, finiteNumber(directionZ, 1)),
      finiteNumber(wave.amplitude, finiteNumber(wave.height, 0)),
      Math.max(finiteNumber(wave.wavelength, 12), 0.0001),
    ],
    speed: finiteNumber(wave.speed, finiteNumber(wave.phaseSpeed, 0.35)),
    phaseOffset: finiteNumber(wave.phaseOffset, 0),
    steepness: Math.max(
      0,
      Math.min(0.95, finiteNumber(wave.steepness, GEOMETRIC_STEEPNESS[index] ?? 0.2)),
    ),
  };
}

function getWaveUniforms(waveField) {
  const source = waveField && typeof waveField.getShaderWaveData === "function"
    ? waveField.getShaderWaveData()
    : [];
  const sourceWaves = Array.isArray(source) ? source.slice(0, MAX_WAVES) : [];
  const values = sourceWaves.map((wave, index) => waveToUniform(wave, index));

  while (values.length < MAX_WAVES) {
    values.push(waveToUniform(DEFAULT_WAVE, values.length));
  }

  return {
    values,
    phaseOffsets: values.map((item) => item.phaseOffset),
    steepness: values.map((item) => item.steepness),
    count: Math.min(Array.isArray(source) ? source.length : 0, MAX_WAVES),
  };
}

function boundaryToUniform(boundary) {
  if (!boundary || typeof boundary !== "object") {
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
    visualProfile = VISUAL_WATER_PRESET,
  } = {}) {
    const safeWidth = Math.max(finiteNumber(width, 1), 0.001);
    const safeDepth = Math.max(finiteNumber(depth, 1), 0.001);
    const waveData = getWaveUniforms(waveField);
    const boundaryData = boundaryToUniform(boundary);
    const geometry = new three.PlaneGeometry(
      safeWidth,
      safeDepth,
      PLANE_SEGMENTS,
      PLANE_SEGMENTS,
    );
    geometry.rotateX(-Math.PI / 2);

    const sunDirection = new three.Vector3(0.35, 0.9, 0.2);
    sunDirection.normalize();
    const material = new three.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        waves: {
          value: waveData.values.map((item) => vector4FromValues(three, item.vector)),
        },
        waveSpeeds: { value: waveData.values.map((item) => item.speed) },
        wavePhaseOffsets: { value: waveData.phaseOffsets },
        waveSteepness: { value: waveData.steepness },
        waveCount: { value: waveData.count },
        amplitudeScale: { value: 1 },
        steepnessScale: { value: 1 },
        sunDirection: { value: sunDirection },
        deepColor: { value: new three.Color(0.018, 0.13, 0.29) },
        shallowColor: { value: new three.Color(0.055, 0.39, 0.52) },
        reflectionColor: { value: new three.Color(0.34, 0.7, 0.88) },
        foamColor: { value: new three.Color(0.72, 0.94, 0.97) },
        detailStrength: { value: VISUAL_WATER_PRESET.detailStrength },
        detailScale: { value: VISUAL_WATER_PRESET.detailScale },
        detailSpeed: { value: VISUAL_WATER_PRESET.detailSpeed },
        fresnelPower: { value: VISUAL_WATER_PRESET.fresnelPower },
        reflectionStrength: { value: VISUAL_WATER_PRESET.reflectionStrength },
        specularStrength: { value: VISUAL_WATER_PRESET.specularStrength },
        horizonStrength: { value: VISUAL_WATER_PRESET.horizonStrength },
        subsurfaceStrength: { value: VISUAL_WATER_PRESET.subsurfaceStrength },
        crestFoamStrength: { value: VISUAL_WATER_PRESET.crestFoamStrength },
        foldingFoamStrength: { value: VISUAL_WATER_PRESET.foldingFoamStrength },
        foamScale: { value: 1 },
        shoreFade: { value: vector4FromValues(three, boundaryData) },
      },
      vertexShader,
      fragmentShader,
      transparent: false,
      depthWrite: true,
      side: three.DoubleSide,
    });

    this.object3D = new three.Mesh(geometry, material);
    this.object3D.name = "WaterSurface";
    this.geometry = geometry;
    this.material = material;
    this.uniforms = material.uniforms;
    this.profile = VISUAL_WATER_PRESET;
    this._disposed = false;
    this.setVisualProfile(visualProfile);
  }

  setVisualProfile(profile) {
    const profileId = typeof profile === "string" ? profile : profile?.id;
    const resolved = getWaterProfile(profileId);
    this.profile = resolved;
    this.uniforms.amplitudeScale.value = resolved.amplitudeScale;
    this.uniforms.steepnessScale.value = resolved.steepnessScale;
    this.uniforms.foamScale.value = resolved.foamScale;
    this.uniforms.detailStrength.value = resolved.detailStrength;
    this.uniforms.detailScale.value = resolved.detailScale;
    this.uniforms.detailSpeed.value = resolved.detailSpeed;
    this.uniforms.fresnelPower.value = resolved.fresnelPower;
    this.uniforms.reflectionStrength.value = resolved.reflectionStrength;
    this.uniforms.specularStrength.value = resolved.specularStrength;
    this.uniforms.horizonStrength.value = resolved.horizonStrength;
    this.uniforms.subsurfaceStrength.value = resolved.subsurfaceStrength;
    this.uniforms.crestFoamStrength.value = resolved.crestFoamStrength;
    this.uniforms.foldingFoamStrength.value = resolved.foldingFoamStrength;
    return this.profile;
  }

  getVisualProfile() {
    return this.profile || VISUAL_WATER_PRESET;
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
