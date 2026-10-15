import * as THREE from 'three';

/**
 * Mặt phẳng foam mỏng chạy dọc biên vùng nước.
 * Foam chỉ là lớp hiển thị, không tạo va chạm hay mô phỏng vật lý.
 */
export class ShoreFoam {
  constructor({ THREE: three = THREE, boundary, width, depth }) {
    const boundaryWidth = Math.abs(boundary.maxX - boundary.minX);
    const boundaryDepth = Math.abs(boundary.maxZ - boundary.minZ);
    const surfaceWidth = Number.isFinite(width) && width > 0 ? width : boundaryWidth;
    const surfaceDepth = Number.isFinite(depth) && depth > 0 ? depth : boundaryDepth;
    const safeWidth = Math.max(surfaceWidth, 0.001);
    const safeDepth = Math.max(surfaceDepth, 0.001);
    const shortestEdge = Math.min(safeWidth, safeDepth);
    const bandWidth = Math.max(shortestEdge * 0.08, 0.001);
    const centerX = (boundary.minX + boundary.maxX) * 0.5;
    const centerZ = (boundary.minZ + boundary.maxZ) * 0.5;

    // PlaneGeometry ban đầu nằm trên XY; xoay -90 độ để mặt foam nằm trên XZ, Y là trục đứng.
    const geometry = new three.PlaneGeometry(safeWidth, safeDepth, 1, 1);
    geometry.rotateX(-Math.PI * 0.5);

    const material = new three.ShaderMaterial({
      uniforms: {
        uBoundary: {
          value: new three.Vector4(
            boundary.minX,
            boundary.maxX,
            boundary.minZ,
            boundary.maxZ,
          ),
        },
        uBandWidth: {
          value: bandWidth,
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
        uniform float uBandWidth;
        uniform vec3 uFoamColor;
        uniform float uTime;

        varying vec3 vWorldPosition;

        void main() {
          // Boundary dùng X/Z của mặt nước; khoảng cách nhỏ nhất là cạnh bờ gần nhất.
          float distanceX = min(
            vWorldPosition.x - uBoundary.x,
            uBoundary.y - vWorldPosition.x
          );
          float distanceZ = min(
            vWorldPosition.z - uBoundary.z,
            uBoundary.w - vWorldPosition.z
          );
          float edgeDistance = max(min(distanceX, distanceZ), 0.0);
          float shoreFade = 1.0 - smoothstep(0.0, uBandWidth * 1.4, edgeDistance);

          float firstBand = 1.0 - smoothstep(0.0, uBandWidth * 0.52, edgeDistance);
          float secondBand = smoothstep(
            uBandWidth * 0.34,
            uBandWidth * 0.52,
            edgeDistance
          );
          secondBand *= 1.0 - smoothstep(
            uBandWidth * 0.82,
            uBandWidth * 1.12,
            edgeDistance
          );

          float waveA = 0.5 + 0.5 * sin(
            (vWorldPosition.x + vWorldPosition.z) / uBandWidth + uTime * 1.35
          );
          float waveB = 0.5 + 0.5 * sin(
            (vWorldPosition.x - vWorldPosition.z) / uBandWidth * 1.7 - uTime * 1.05
          );
          float foam = firstBand * (0.52 + waveA * 0.30);
          foam += secondBand * (0.24 + waveB * 0.24);
          float alpha = clamp(foam * shoreFade * 0.92, 0.0, 0.86);

          gl_FragColor = vec4(uFoamColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      side: three.DoubleSide,
    });

    this.geometry = geometry;
    this.material = material;
    this.object3D = new three.Mesh(geometry, material);
    this.object3D.position.set(centerX, 0, centerZ);
    this.object3D.renderOrder = 10;
    this._disposed = false;
  }

  update(timeSeconds) {
    if (this._disposed) {
      return;
    }
    this.material.uniforms.uTime.value = timeSeconds;
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
