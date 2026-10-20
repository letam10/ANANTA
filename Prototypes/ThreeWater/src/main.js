import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { WaveField } from "./water/WaveField.js";
import { WaterSurface } from "./water/WaterSurface.js";
import { getWaterProfile, WATER_PROFILES } from "./water/WaterProfiles.js";
import { ShoreFoam } from "./water/ShoreFoam.js";
import { CoastBoundary } from "./water/CoastBoundary.js";
import { PerformanceOverlay } from "./qa/PerformanceOverlay.js";
import { SCENE_PRESETS, applyScenePreset, getScenePreset } from "./qa/ScenePresets.js";

const canvas = document.querySelector("#water-canvas");
const status = document.querySelector("#status");

function setStatus(message) {
  if (status) {
    status.textContent = message;
  }
}

function finiteNumber(value, fallback) {
  return Number.isFinite(value) ? value : fallback;
}

async function loadWaveSpec() {
  const response = await fetch("/wave-spec.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`wave-spec.json HTTP ${response.status}`);
  }
  return response.json();
}

function createWaveField(spec) {
  const waves = spec.waves.map((wave) => ({
    direction: wave.direction,
    wavelength: wave.wavelength,
    amplitude: wave.amplitude,
    speed: wave.speed,
    phaseOffset: finiteNumber(wave.phase, finiteNumber(wave.phaseOffset, 0)),
  }));
  return new WaveField(waves);
}

function createBoundary(spec) {
  return new CoastBoundary({
    type: spec.type,
    minX: spec.minX,
    maxX: spec.maxX,
    minZ: spec.minZ,
    maxZ: spec.maxZ,
    polygon: spec.polygon,
    boatMargin: spec.boatMargin,
  });
}

function createBoat(scene) {
  const boat = new THREE.Group();
  const hull = new THREE.Mesh(
    new THREE.BoxGeometry(7, 1.1, 2.6),
    new THREE.MeshStandardMaterial({ color: 0x5b3827, roughness: 0.7 }),
  );
  hull.scale.set(1, 1, 0.72);
  hull.position.y = 0.25;
  boat.add(hull);
  const deck = new THREE.Mesh(
    new THREE.BoxGeometry(3.2, 0.75, 2.1),
    new THREE.MeshStandardMaterial({ color: 0xc98755, roughness: 0.65 }),
  );
  deck.position.set(-0.3, 1.05, 0);
  boat.add(deck);
  const mast = new THREE.Mesh(
    new THREE.CylinderGeometry(0.08, 0.1, 2.4, 10),
    new THREE.MeshStandardMaterial({ color: 0xefe1b7, roughness: 0.7 }),
  );
  mast.position.set(0.4, 2.25, 0);
  boat.add(mast);
  boat.position.set(-42, 0, -8);
  boat.rotation.y = -0.35;
  scene.add(boat);
  return boat;
}

function createSceneAccumulator(sceneId) {
  return {
    sceneId,
    frameCount: 0,
    totalFrameMs: 0,
    minFrameMs: Number.POSITIVE_INFINITY,
    maxFrameMs: 0,
    frameTimes: [],
  };
}

function finalizeSceneAccumulator(accumulator, durationSeconds) {
  const averageFrameMs = accumulator.frameCount > 0
    ? accumulator.totalFrameMs / accumulator.frameCount
    : 0;
  const steadyFrameTimes = accumulator.frameTimes.filter((frameMs) => frameMs <= 50);
  const steadyAverageFrameMs = steadyFrameTimes.length > 0
    ? steadyFrameTimes.reduce((sum, frameMs) => sum + frameMs, 0) / steadyFrameTimes.length
    : 0;
  const sortedFrameTimes = [...accumulator.frameTimes].sort((first, second) => first - second);
  const p95Index = sortedFrameTimes.length > 0
    ? Math.floor((sortedFrameTimes.length - 1) * 0.95)
    : 0;
  return {
    sceneId: accumulator.sceneId,
    durationSeconds,
    frameCount: accumulator.frameCount,
    averageFrameMs: Number(averageFrameMs.toFixed(4)),
    steadyAverageFrameMs: Number(steadyAverageFrameMs.toFixed(4)),
    p95FrameMs: Number((sortedFrameTimes[p95Index] || 0).toFixed(4)),
    outlierFrameCount: accumulator.frameTimes.length - steadyFrameTimes.length,
    minFrameMs: Number((Number.isFinite(accumulator.minFrameMs)
      ? accumulator.minFrameMs
      : 0).toFixed(4)),
    maxFrameMs: Number(accumulator.maxFrameMs.toFixed(4)),
  };
}

async function bootstrap(spec) {
  const scenePresets = Object.values(SCENE_PRESETS);
  const boundarySpec = spec.boundary;
  const boundary = createBoundary(boundarySpec);
  const waveField = createWaveField(spec);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x8db8cb);
  scene.fog = new THREE.Fog(0x8db8cb, 260, 920);
  const camera = new THREE.PerspectiveCamera(
    48,
    window.innerWidth / window.innerHeight,
    0.1,
    1400,
  );
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.minDistance = 24;
  controls.maxDistance = 760;

  scene.add(new THREE.HemisphereLight(0xbfeaff, 0x24475c, 1.9));
  const sun = new THREE.DirectionalLight(0xffe7bd, 2.8);
  sun.position.set(-180, 240, 120);
  scene.add(sun);

  const width = boundary.maxX - boundary.minX;
  const depth = boundary.maxZ - boundary.minZ;
  const water = new WaterSurface({
    THREE,
    waveField,
    width,
    depth,
    boundary,
    visualProfile: WATER_PROFILES.low,
  });
  const foam = new ShoreFoam({
    THREE,
    boundary,
    width,
    depth,
    foamWidth: spec.foam.width,
    shorelineDepth: spec.foam.shorelineDepth,
  });
  const boundaryPreview = boundary.createPreview(THREE);
  scene.add(water.object3D, foam.object3D, boundaryPreview);

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(width + 180, depth + 140),
    new THREE.MeshStandardMaterial({ color: 0xd6bd8e, roughness: 0.9, metalness: 0 }),
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.75;
  scene.add(ground);

  const boat = createBoat(scene);
  const boatBasePosition = new THREE.Vector3(boat.position.x, 0, boat.position.z);
  const overlay = new PerformanceOverlay();
  const keys = new Set();
  const freeForward = new THREE.Vector3();
  const freeRight = new THREE.Vector3();
  const freeMove = new THREE.Vector3();
  const up = new THREE.Vector3(0, 1, 0);
  const clock = new THREE.Clock();
  const state = {
    paused: false,
    cameraMode: "orbit",
    boundaryVisible: true,
    foamVisible: true,
    activeSceneId: "coast",
    sceneElapsed: 0,
    autoAdvance: true,
    sceneReports: [],
    sceneAccumulator: createSceneAccumulator("coast"),
    quickQaComplete: false,
    waterProfileId: WATER_PROFILES.low.id,
  };
  let elapsed = 0;
  let lastFrame = performance.now();

  function clampCameraAndTarget() {
    const cameraPoint = boundary.clamp(
      camera.position.x,
      camera.position.z,
      finiteNumber(boundarySpec.cameraMargin, 14),
    );
    camera.position.x = cameraPoint.x;
    camera.position.z = cameraPoint.z;
    const targetPoint = boundary.clamp(
      controls.target.x,
      controls.target.z,
      finiteNumber(boundarySpec.cameraMargin, 14),
    );
    controls.target.x = targetPoint.x;
    controls.target.z = targetPoint.z;
  }

  function applyScene(sceneId, manual = false) {
    const preset = getScenePreset(sceneId);
    if (!preset) {
      return;
    }
    if (manual) {
      state.sceneReports = [];
      state.quickQaComplete = false;
    }
    state.activeSceneId = preset.id;
    state.sceneElapsed = 0;
    state.sceneAccumulator = createSceneAccumulator(preset.id);
    state.paused = false;
    applyScenePreset(camera, controls, preset);
    clampCameraAndTarget();
    boat.visible = preset.id !== "offshore";
    const waterProfile = getWaterProfile(state.waterProfileId);
    setStatus(`Ready · ${preset.id} · ${waterProfile.label} · ${preset.durationSeconds}s quick QA · G storm`);
  }

  function applyWaterProfile(profileId) {
    const profile = getWaterProfile(profileId);
    state.waterProfileId = profile.id;
    water.setVisualProfile(profile);
    setStatus(`Ready · ${profile.label} · ${state.activeSceneId} · G toggles storm`);
  }

  function recordSceneFrame(frameMs) {
    const accumulator = state.sceneAccumulator;
    accumulator.frameCount += 1;
    accumulator.totalFrameMs += frameMs;
    accumulator.frameTimes.push(frameMs);
    accumulator.minFrameMs = Math.min(accumulator.minFrameMs, frameMs);
    accumulator.maxFrameMs = Math.max(accumulator.maxFrameMs, frameMs);
  }

  function advanceSceneIfReady() {
    const preset = getScenePreset(state.activeSceneId);
    if (!state.autoAdvance || state.sceneElapsed < preset.durationSeconds) {
      return;
    }
    state.sceneReports.push(
      finalizeSceneAccumulator(state.sceneAccumulator, preset.durationSeconds),
    );
    const currentIndex = scenePresets.findIndex((item) => item.id === preset.id);
    const next = scenePresets[currentIndex + 1];
    if (!next) {
      state.autoAdvance = false;
      state.quickQaComplete = true;
      state.paused = false;
      setStatus("W2 quick QA complete · water animation live · reports ready");
      return;
    }
    applyScene(next.id);
  }

  function moveFreeCamera(deltaSeconds) {
    if (state.cameraMode !== "free") {
      return;
    }
    camera.getWorldDirection(freeForward);
    freeForward.y = 0;
    freeForward.normalize();
    freeRight.crossVectors(freeForward, up).normalize();
    freeMove.set(0, 0, 0);
    if (keys.has("KeyW")) freeMove.add(freeForward);
    if (keys.has("KeyS")) freeMove.sub(freeForward);
    if (keys.has("KeyD")) freeMove.add(freeRight);
    if (keys.has("KeyA")) freeMove.sub(freeRight);
    if (keys.has("KeyR")) freeMove.y += 1;
    if (keys.has("KeyF")) freeMove.y -= 1;
    if (freeMove.lengthSq() > 0) {
      freeMove.normalize().multiplyScalar(deltaSeconds * 42);
      camera.position.add(freeMove);
    }
    clampCameraAndTarget();
  }

  function updateBoat() {
    const basePoint = boundary.clamp(
      boatBasePosition.x,
      boatBasePosition.z,
      finiteNumber(boundarySpec.boatMargin, 8),
    );
    const sample = waveField.sampleGerstnerPositionAndNormal(
      basePoint.x,
      basePoint.z,
      elapsed,
      water.getVisualProfile(),
    );
    const displacedPoint = boundary.clamp(
      sample.position.x,
      sample.position.z,
      finiteNumber(boundarySpec.boatMargin, 8),
    );
    boat.position.x = displacedPoint.x;
    boat.position.z = displacedPoint.z;
    boat.position.y = sample.position.y + 1.15;
    const normal = new THREE.Vector3(sample.normal.x, sample.normal.y, sample.normal.z);
    boat.quaternion.setFromUnitVectors(up, normal);
  }

  function handleKeyDown(event) {
    keys.add(event.code);
    if (event.code === "KeyC" && !event.repeat) {
      state.cameraMode = state.cameraMode === "orbit" ? "free" : "orbit";
      controls.enabled = state.cameraMode === "orbit";
      setStatus(`Ready · ${state.cameraMode} camera · ${state.activeSceneId}`);
    }
    if (event.code === "Digit1" && !event.repeat) applyScene("coast", true);
    if (event.code === "Digit2" && !event.repeat) applyScene("beach_boat", true);
    if (event.code === "Digit3" && !event.repeat) applyScene("offshore", true);
    if (event.code === "KeyB" && !event.repeat) {
      state.boundaryVisible = !state.boundaryVisible;
      boundaryPreview.visible = state.boundaryVisible;
    }
    if (event.code === "KeyF" && state.cameraMode !== "free" && !event.repeat) {
      state.foamVisible = !state.foamVisible;
      foam.setVisible(state.foamVisible);
    }
    if (event.code === "KeyG" && !event.repeat) {
      applyWaterProfile(state.waterProfileId === "storm" ? "low" : "storm");
    }
    if (event.code === "Space" && !event.repeat) state.paused = !state.paused;
  }

  function handleKeyUp(event) {
    keys.delete(event.code);
  }

  function resize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight, false);
  }

  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
  window.addEventListener("resize", resize);

  applyWaterProfile(state.waterProfileId);
  applyScene("coast");
  window.__ANANTA_WATER_QA__ = {
    sceneReady: true,
    schema: spec.schema,
    waveCount: waveField.waves.length,
    boundary: boundary.toJSON(),
    foam: spec.foam,
    scenes: scenePresets.map((item) => item.id),
    sceneReports: state.sceneReports,
    renderer,
    water,
    foamObject: foam,
    boundaryPreview,
    quickQa: state,
    waterProfile: state.waterProfileId,
  };
  document.body.dataset.qaReady = "true";

  function animate() {
    requestAnimationFrame(animate);
    const deltaSeconds = Math.min(clock.getDelta(), 0.05);
    if (!state.paused) {
      elapsed += deltaSeconds;
      state.sceneElapsed += deltaSeconds;
    }
    moveFreeCamera(deltaSeconds);
    if (!state.paused) {
      water.update(elapsed);
      foam.update(elapsed);
      updateBoat();
    }
    controls.update();
    clampCameraAndTarget();
    const now = performance.now();
    const frameMs = now - lastFrame;
    lastFrame = now;
    renderer.render(scene, camera);
    recordSceneFrame(frameMs);
    advanceSceneIfReady();
    overlay.update(renderer, {
      frameMs,
      waveCount: waveField.waves.length,
      waterProfile: state.waterProfileId,
      cameraMode: state.cameraMode,
      boundaryVisible: state.boundaryVisible,
      foamVisible: state.foamVisible,
      sceneId: state.activeSceneId,
      sceneElapsed: state.sceneElapsed,
      sceneDuration: getScenePreset(state.activeSceneId).durationSeconds,
      sceneReports: state.sceneReports,
    });
    window.__ANANTA_WATER_QA__.sceneReports = state.sceneReports;
    window.__ANANTA_WATER_QA__.waterProfile = state.waterProfileId;
  }

  animate();
}

loadWaveSpec().then((spec) => bootstrap(spec)).catch((error) => {
  document.body.dataset.qaReady = "false";
  setStatus(`Water prototype error: ${error.message}`);
  console.error("ANANTA_WATER_BOOTSTRAP_ERROR", error);
});
