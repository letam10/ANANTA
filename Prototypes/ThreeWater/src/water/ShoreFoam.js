import * as THREE from 'three';

const finiteNumber = (value, fallback) => Number.isFinite(value) ? value : fallback;

function boundaryBounds(boundary) {
  const minX = finiteNumber(boundary && boundary.minX, -120);
  const maxX = finiteNumber(boundary && boundary.maxX, 120);
  const minZ = finiteNumber(boundary && boundary.minZ, -80);
  const maxZ = finiteNumber(boundary && boundary.maxZ, 80);
  return {
    minX: Math.min(minX, maxX),
    maxX: Math.max(minX, maxX),
    minZ: Math.min(minZ, maxZ),
    maxZ: Math.max(minZ, maxZ),
  };
}

function vector4FromValues(three, values) {
  if (typeof three.Vector4 === 'function') {
    return new three.Vector4(values.minX, values.maxX, values.minZ, values.maxZ);
  }
  return [values.minX, values.maxX, values.minZ, values.maxZ];
}

/**
 * Mặt phẳng foam mỏng chạy dọc biên vùng nước.
 * Foam chỉ là lớp hiển thị, không tạo va chạm hay mô phỏng vật lý.
 */
export class ShoreFoam {
  constructor({
    THREE: three = THREE,
    boundary = {},
    width,
    depth,
    foamWidth,
    shorelineDepth,
  } = {}) {
    const bounds = boundaryBounds(boundary);
    const boundaryWidth = bounds.maxX - bounds.minX;
    const boundaryDepth = bounds.maxZ - bounds.minZ;
    const surfaceWidth = Number.isFinite(width) && width > 0 ? width : boundaryWidth;
    const surfaceDepth = Number.isFinite(depth) && depth > 0 ? depth : boundaryDepth;
    const safeWidth = Math.max(surfaceWidth, 0.001);
    const safeDepth = Math.max(surfaceDepth, 0.001);
    const defaultFoamWidth = Math.max(Math.min(safeWidth, safeDepth) * 0.08, 0.001);
    const safeFoamWidth = Math.max(finiteNumber(foamWidth, defaultFoamWidth), 0.001);
    const safeShorelineDepth = Math.max(
      finiteNumber(shorelineDepth, safeFoamWidth),
      0.001,
    );
    const centerX = (bounds.minX + bounds.maxX) * 0.5;
    const centerZ = (bounds.minZ + bounds.maxZ) * 0.5;

    // Geometry tạo một lần; khoảng cách tới boundary được tính trong fragment shader.
    const geometry = new three.PlaneGeometry(safeWidth, safeDepth, 1, 1);
    geometry.rotateX(-Math.PI * 0.5);
    const boundaryUniform = vector4FromValues(three, bounds);
    const material = new three.ShaderMaterial({
      uniforms: {
        uBoundary: {
          value: boundaryUniform,
        },
        uFoamWidth: {
          value: safeFoamWidth,
        },
        uShorelineDepth: {
          value: safeShorelineDepth,
        },
        uBandWidth: {
          value: safeFoamWidth,
        },
        uFoamColor: {
          value: new three.Color(0.84, 0.96, 1.0),
        },
        uTime: {
          value: 0,
        },
      },
      vertexShader: `
        varying vec3 vWorldPosition;

        void main() {
          vec4 worldPosition = modelMatrix * vec4(position, 1.0);
          vWorldPosition = worldPosition.xyz;
          gl_Position = projectionMatrix * viewMatrix * worldPosition;
        }
      `,
      fragmentShader: `
        uniform vec4 uBoundary;
        uniform float uFoamWidth;
        uniform float uShorelineDepth;
        uniform float uBandWidth;
        uniform vec3 uFoamColor;
        uniform float uTime;

        varying vec3 vWorldPosition;

        void main() {
          float distanceX = min(
            vWorldPosition.x - uBoundary.x,
            uBoundary.y - vWorldPosition.x
          );
          float distanceZ = min(
            vWorldPosition.z - uBoundary.z,
            uBoundary.w - vWorldPosition.z
          );
          float edgeDistance = max(min(distanceX, distanceZ), 0.0);
          float foamRange = max(max(uFoamWidth, uBandWidth), 0.001);
          float depthRange = max(uShorelineDepth, 0.001);
          float shorelineMask = 1.0 - smoothstep(0.0, depthRange, edgeDistance);
          float foamMask = 1.0 - smoothstep(0.0, foamRange, edgeDistance);

          float waveA = 0.5 + 0.5 * sin(
            (vWorldPosition.x + vWorldPosition.z) / foamRange + uTime * 1.35
          );
          float waveB = 0.5 + 0.5 * sin(
            (vWorldPosition.x - vWorldPosition.z) / foamRange * 1.7 - uTime * 1.05
          );
          float foam = foamMask * (0.48 + waveA * 0.28);
          foam += foamMask * shorelineMask * (0.18 + waveB * 0.18);
          float alpha = clamp(foam * 0.92, 0.0, 0.86);

          gl_FragColor = vec4(uFoamColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      side: three.DoubleSide,
    });

    this.boundary = boundary;
    this.foamWidth = safeFoamWidth;
    this.shorelineDepth = safeShorelineDepth;
    this.geometry = geometry;
    this.material = material;
    this.uniforms = material.uniforms;
    this.object3D = new three.Mesh(geometry, material);
    this.object3D.name = 'ShoreFoam';
    this.object3D.position.set(centerX, 0, centerZ);
    this.object3D.renderOrder = 10;
    this._disposed = false;
  }

  update(timeSeconds) {
    if (this._disposed) {
      return;
    }
    this.uniforms.uTime.value = finiteNumber(timeSeconds, 0);
  }

  setVisible(visible) {
    this.object3D.visible = Boolean(visible);
  }

  dispose() {
    if (this._disposed) {
      return;
    }
    if (this.geometry && typeof this.geometry.dispose === 'function') {
      this.geometry.dispose();
    }
    if (this.material && typeof this.material.dispose === 'function') {
      this.material.dispose();
    }
    this._disposed = true;
  }
}
