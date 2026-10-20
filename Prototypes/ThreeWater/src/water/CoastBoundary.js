const DEFAULT_BOUNDS = {
  minX: -120,
  maxX: 120,
  minZ: -80,
  maxZ: 80,
};

const EPSILON = 1e-6;

const finiteNumber = (value, fallback) => Number.isFinite(value) ? value : fallback;

function readPoint(point, index) {
  if (Array.isArray(point)) {
    return {
      x: finiteNumber(point[0], NaN),
      z: finiteNumber(point[1], NaN),
    };
  }

  if (!point || typeof point !== "object") {
    return { x: NaN, z: NaN };
  }

  return {
    x: finiteNumber(point.x, NaN),
    z: finiteNumber(point.z, finiteNumber(point.y, NaN)),
  };
}

function normalizePolygon(points) {
  if (!Array.isArray(points)) {
    return [];
  }

  const normalized = points.map(readPoint).filter((point) => (
    Number.isFinite(point.x) && Number.isFinite(point.z)
  ));
  if (normalized.length > 2) {
    const first = normalized[0];
    const last = normalized[normalized.length - 1];
    if (Math.abs(first.x - last.x) < EPSILON && Math.abs(first.z - last.z) < EPSILON) {
      normalized.pop();
    }
  }

  return normalized.length >= 3 ? normalized : [];
}

function polygonBounds(polygon) {
  return polygon.reduce((bounds, point) => ({
    minX: Math.min(bounds.minX, point.x),
    maxX: Math.max(bounds.maxX, point.x),
    minZ: Math.min(bounds.minZ, point.z),
    maxZ: Math.max(bounds.maxZ, point.z),
  }), {
    minX: Infinity,
    maxX: -Infinity,
    minZ: Infinity,
    maxZ: -Infinity,
  });
}

function pointOnSegment(x, z, start, end) {
  const cross = (x - start.x) * (end.z - start.z) - (z - start.z) * (end.x - start.x);
  if (Math.abs(cross) > EPSILON) {
    return false;
  }

  return x >= Math.min(start.x, end.x) - EPSILON
    && x <= Math.max(start.x, end.x) + EPSILON
    && z >= Math.min(start.z, end.z) - EPSILON
    && z <= Math.max(start.z, end.z) + EPSILON;
}

function pointInPolygon(x, z, polygon) {
  let inside = false;
  for (let index = 0; index < polygon.length; index += 1) {
    const start = polygon[index];
    const end = polygon[(index + 1) % polygon.length];
    if (pointOnSegment(x, z, start, end)) {
      return true;
    }

    const crossesRay = (start.z > z) !== (end.z > z);
    if (crossesRay) {
      const intersectionX = (end.x - start.x) * (z - start.z) / (end.z - start.z) + start.x;
      if (x < intersectionX) {
        inside = !inside;
      }
    }
  }

  return inside;
}

function distanceToSegment(x, z, start, end) {
  const deltaX = end.x - start.x;
  const deltaZ = end.z - start.z;
  const lengthSquared = deltaX * deltaX + deltaZ * deltaZ;
  if (lengthSquared < EPSILON) {
    return Math.hypot(x - start.x, z - start.z);
  }

  const ratio = Math.max(0, Math.min(1, ((x - start.x) * deltaX + (z - start.z) * deltaZ) / lengthSquared));
  return Math.hypot(x - (start.x + ratio * deltaX), z - (start.z + ratio * deltaZ));
}

function nearestPointOnPolygon(x, z, polygon) {
  let bestPoint = { x: polygon[0].x, z: polygon[0].z };
  let bestDistance = Infinity;
  for (let index = 0; index < polygon.length; index += 1) {
    const start = polygon[index];
    const end = polygon[(index + 1) % polygon.length];
    const deltaX = end.x - start.x;
    const deltaZ = end.z - start.z;
    const lengthSquared = deltaX * deltaX + deltaZ * deltaZ;
    const ratio = lengthSquared < EPSILON
      ? 0
      : Math.max(0, Math.min(1, ((x - start.x) * deltaX + (z - start.z) * deltaZ) / lengthSquared));
    const point = { x: start.x + ratio * deltaX, z: start.z + ratio * deltaZ };
    const distance = Math.hypot(x - point.x, z - point.z);
    if (distance < bestDistance) {
      bestDistance = distance;
      bestPoint = point;
    }
  }

  return bestPoint;
}

function polygonCentroid(polygon) {
  const result = polygon.reduce((sum, point) => ({ x: sum.x + point.x, z: sum.z + point.z }), { x: 0, z: 0 });
  return {
    x: result.x / polygon.length,
    z: result.z / polygon.length,
  };
}

function getPolygonOption(options) {
  if (Array.isArray(options.polygon)) {
    return options.polygon;
  }
  if (Array.isArray(options.points)) {
    return options.points;
  }
  if (Array.isArray(options.shape)) {
    return options.shape;
  }
  if (options.shape && typeof options.shape === "object") {
    return options.shape.points || options.shape.vertices;
  }
  return [];
}

function clampRange(value, minimum, maximum) {
  if (minimum > maximum) {
    return (minimum + maximum) * 0.5;
  }
  return Math.min(maximum, Math.max(minimum, value));
}

export class CoastBoundary {
  constructor(bounds = {}, positionalMaxX, positionalMinZ, positionalMaxZ) {
    const options = typeof bounds === "number"
      ? {
        minX: bounds,
        maxX: positionalMaxX,
        minZ: positionalMinZ,
        maxZ: positionalMaxZ,
      }
      : (bounds || {});
    // Spec box có thể kèm polygon để trao đổi; không bỏ qua kiểu đã khai báo.
    const explicitBox = options.type === "box" || options.shape === "box";
    const polygon = explicitBox ? [] : normalizePolygon(getPolygonOption(options));
    const derivedBounds = polygon.length ? polygonBounds(polygon) : DEFAULT_BOUNDS;
    const sourceMinX = finiteNumber(options.minX, derivedBounds.minX);
    const sourceMaxX = finiteNumber(options.maxX, derivedBounds.maxX);
    const sourceMinZ = finiteNumber(options.minZ, derivedBounds.minZ);
    const sourceMaxZ = finiteNumber(options.maxZ, derivedBounds.maxZ);

    this.minX = Math.min(sourceMinX, sourceMaxX);
    this.maxX = Math.max(sourceMinX, sourceMaxX);
    this.minZ = Math.min(sourceMinZ, sourceMaxZ);
    this.maxZ = Math.max(sourceMinZ, sourceMaxZ);
    this.shape = polygon.length ? "polygon" : "box";
    this.type = this.shape;
    this.polygon = polygon.length ? polygon : null;
    this.boatMargin = Math.max(0, finiteNumber(options.boatMargin, 0));
    this.bounds = {
      minX: this.minX,
      maxX: this.maxX,
      minZ: this.minZ,
      maxZ: this.maxZ,
    };
  }

  contains(x, z, margin = 0) {
    if (!Number.isFinite(x) || !Number.isFinite(z)) {
      return false;
    }

    const safeMargin = Math.max(0, finiteNumber(margin, 0));
    if (this.shape === "polygon") {
      return pointInPolygon(x, z, this.polygon)
        && this.distanceToShore(x, z) + EPSILON >= safeMargin;
    }

    return x >= this.minX + safeMargin && x <= this.maxX - safeMargin
      && z >= this.minZ + safeMargin && z <= this.maxZ - safeMargin;
  }

  clamp(x, z, margin = 0) {
    const safeMargin = Math.max(0, finiteNumber(margin, 0));
    const safeX = finiteNumber(x, (this.minX + this.maxX) * 0.5);
    const safeZ = finiteNumber(z, (this.minZ + this.maxZ) * 0.5);
    if (this.shape === "polygon") {
      if (this.contains(safeX, safeZ, safeMargin)) {
        return { x: safeX, z: safeZ };
      }

      const edgePoint = nearestPointOnPolygon(safeX, safeZ, this.polygon);
      if (safeMargin <= 0) {
        return edgePoint;
      }

      const centroid = polygonCentroid(this.polygon);
      const directionX = centroid.x - edgePoint.x;
      const directionZ = centroid.z - edgePoint.z;
      const directionLength = Math.hypot(directionX, directionZ);
      if (directionLength > EPSILON) {
        const insetPoint = {
          x: edgePoint.x + directionX / directionLength * safeMargin,
          z: edgePoint.z + directionZ / directionLength * safeMargin,
        };
        if (this.contains(insetPoint.x, insetPoint.z, safeMargin)) {
          return insetPoint;
        }
      }

      return edgePoint;
    }

    return {
      x: clampRange(safeX, this.minX + safeMargin, this.maxX - safeMargin),
      z: clampRange(safeZ, this.minZ + safeMargin, this.maxZ - safeMargin),
    };
  }

  clampPoint(point, margin = 0) {
    const source = Array.isArray(point)
      ? { x: point[0], z: point[1] }
      : (point || {});
    const result = this.clamp(source.x, source.z, margin);
    if (source && typeof source === "object" && !Array.isArray(point) && "y" in source) {
      result.y = source.y;
    }
    return result;
  }

  resolveCamera(point, margin = 0) {
    if (typeof point === "number") {
      return this.clamp(point, margin, arguments[2]);
    }
    return this.clampPoint(point, margin);
  }

  resolveBoat(point, margin = this.boatMargin) {
    return this.clampPoint(point, margin);
  }

  distanceToShore(x, z) {
    if (!Number.isFinite(x) || !Number.isFinite(z)) {
      return Infinity;
    }
    if (this.shape === "polygon") {
      return this.polygon.reduce((distance, start, index) => Math.min(
        distance,
        distanceToSegment(x, z, start, this.polygon[(index + 1) % this.polygon.length]),
      ), Infinity);
    }

    return Math.min(
      Math.abs(x - this.minX),
      Math.abs(this.maxX - x),
      Math.abs(z - this.minZ),
      Math.abs(this.maxZ - z),
    );
  }

  toJSON() {
    const result = {
      minX: this.minX,
      maxX: this.maxX,
      minZ: this.minZ,
      maxZ: this.maxZ,
      shape: this.shape,
      type: this.type,
      coordinateSystem: "Three.js Y-up XZ horizontal",
    };
    if (this.polygon) {
      result.polygon = this.polygon.map((point) => ({ x: point.x, z: point.z }));
    }
    return result;
  }

  createPreview(THREE, { y = 0.08, color = 0xffa34d } = {}) {
    const points = this.polygon || [
      { x: this.minX, z: this.minZ },
      { x: this.maxX, z: this.minZ },
      { x: this.maxX, z: this.maxZ },
      { x: this.minX, z: this.maxZ },
    ];
    const vectors = points.map((point) => new THREE.Vector3(point.x, y, point.z));
    const geometry = new THREE.BufferGeometry().setFromPoints(vectors);
    const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.9 });
    return new THREE.LineLoop(geometry, material);
  }
}
