const createPreset = (values) => Object.freeze({
  durationSeconds: 10,
  ...values,
});

export const SCENE_PRESETS = Object.freeze({
  coast: createPreset({
    id: "coast",
    cameraPosition: Object.freeze([560, 70, 300]),
    target: Object.freeze([640, 0, 120]),
    description: "Near-shore view across the coast, foam band, and open water.",
    expectedScale: 720,
  }),
  beach_boat: createPreset({
    id: "beach_boat",
    cameraPosition: Object.freeze([-100, 36, 100]),
    target: Object.freeze([-42, 0, -8]),
    description: "Beach-side view framed on the QA boat inside the water boundary.",
    expectedScale: 100,
  }),
  offshore: createPreset({
    id: "offshore",
    cameraPosition: Object.freeze([320, 180, -280]),
    target: Object.freeze([0, 0, 0]),
    description: "Wide offshore view covering the bounded sea area from a distance.",
    expectedScale: 980,
  }),
});

export function getScenePreset(name) {
  return SCENE_PRESETS[name];
}

function setVector3(vector, values) {
  if (!vector) {
    return;
  }

  if (typeof vector.set === "function") {
    vector.set(values[0], values[1], values[2]);
    return;
  }

  vector.x = values[0];
  vector.y = values[1];
  vector.z = values[2];
}

export function applyScenePreset(camera, controls, preset) {
  const resolvedPreset = typeof preset === "string" ? getScenePreset(preset) : preset;

  if (!resolvedPreset) {
    throw new Error(`Unknown scene preset: ${String(preset)}`);
  }

  if (camera) {
    setVector3(camera.position, resolvedPreset.cameraPosition);

    if (typeof camera.lookAt === "function") {
      camera.lookAt(...resolvedPreset.target);
    }

    if (typeof camera.updateProjectionMatrix === "function") {
      camera.updateProjectionMatrix();
    }
  }

  if (controls) {
    setVector3(controls.target, resolvedPreset.target);

    if (typeof controls.update === "function") {
      controls.update();
    }
  }

  return resolvedPreset;
}
