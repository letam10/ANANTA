const finiteNumber = (value, fallback) => Number.isFinite(value) ? value : fallback;

export class CoastBoundary {
  constructor({ minX = -120, maxX = 120, minZ = -80, maxZ = 80 } = {}) {
    this.minX = Math.min(finiteNumber(minX, -120), finiteNumber(maxX, 120));
    this.maxX = Math.max(finiteNumber(minX, -120), finiteNumber(maxX, 120));
    this.minZ = Math.min(finiteNumber(minZ, -80), finiteNumber(maxZ, 80));
    this.maxZ = Math.max(finiteNumber(minZ, -80), finiteNumber(maxZ, 80));
  }

  contains(x, z, margin = 0) {
    const safeMargin = Math.max(0, finiteNumber(margin, 0));
    return x >= this.minX + safeMargin && x <= this.maxX - safeMargin
      && z >= this.minZ + safeMargin && z <= this.maxZ - safeMargin;
  }

  clamp(x, z, margin = 0) {
    const safeMargin = Math.max(0, finiteNumber(margin, 0));
    return {
      x: Math.min(this.maxX - safeMargin, Math.max(this.minX + safeMargin, x)),
      z: Math.min(this.maxZ - safeMargin, Math.max(this.minZ + safeMargin, z)),
    };
  }

  distanceToShore(x, z) {
    return Math.min(
      Math.abs(x - this.minX),
      Math.abs(this.maxX - x),
      Math.abs(z - this.minZ),
      Math.abs(this.maxZ - z),
    );
  }

  toJSON() {
    return {
      minX: this.minX,
      maxX: this.maxX,
      minZ: this.minZ,
      maxZ: this.maxZ,
      coordinateSystem: "Three.js Y-up XZ horizontal",
    };
  }

  createPreview(THREE, { y = 0.08, color = 0xffa34d } = {}) {
    const points = [
      new THREE.Vector3(this.minX, y, this.minZ),
      new THREE.Vector3(this.maxX, y, this.minZ),
      new THREE.Vector3(this.maxX, y, this.maxZ),
      new THREE.Vector3(this.minX, y, this.maxZ),
    ];
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.9 });
    return new THREE.LineLoop(geometry, material);
  }
}
