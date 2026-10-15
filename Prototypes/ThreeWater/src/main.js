import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { WaveField } from "./water/WaveField.js";
import { WaterSurface } from "./water/WaterSurface.js";
import { ShoreFoam } from "./water/ShoreFoam.js";
import { CoastBoundary } from "./water/CoastBoundary.js";
import { PerformanceOverlay } from "./qa/PerformanceOverlay.js";

const canvas = document.querySelector("#water-canvas");
const status = document.querySelector("#status");
const state = {
  paused: false,
  cameraMode: "orbit",
  boundaryVisible: true,
  foamVisible: true,
};

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
renderer.setSize(window.innerWidth, window.innerHeight, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8db8cb);
scene.fog = new THREE.Fog(0x8db8cb, 180, 420);

const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 600);
camera.position.set(135, 78, 130);
camera.lookAt(0, 0, 0);
const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 0, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 24;
controls.maxDistance = 340;

scene.add(new THREE.HemisphereLight(0xbfeaff, 0x24475c, 1.9));
const sun = new THREE.DirectionalLight(0xffe7bd, 2.8);
sun.position.set(-80, 140, 60);
scene.add(sun);

const boundary = new CoastBoundary({ minX: -120, maxX: 120, minZ: -80, maxZ: 80 });
const waveField = new WaveField();
const water = new WaterSurface({ THREE, waveField, width: 240, depth: 160, boundary });
const foam = new ShoreFoam({ THREE, boundary, width: 240, depth: 160 });
const boundaryPreview = boundary.createPreview(THREE);
scene.add(water.object3D, foam.object3D, boundaryPreview);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(320, 220),
  new THREE.MeshStandardMaterial({ color: 0xd6bd8e, roughness: 0.9, metalness: 0 }),
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.75;
scene.add(ground);

function createBoat() {
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

const boat = createBoat();
const overlay = new PerformanceOverlay();
const keys = new Set();
const freeForward = new THREE.Vector3();
const freeRight = new THREE.Vector3();
const freeMove = new THREE.Vector3();
const up = new THREE.Vector3(0, 1, 0);
const clock = new THREE.Clock();
let elapsed = 0;
let lastFrame = performance.now();

function setStatus(message) {
  if (status) {
    status.textContent = message;
  }
}

function toggleCamera() {
  state.cameraMode = state.cameraMode === "orbit" ? "free" : "orbit";
  controls.enabled = state.cameraMode === "orbit";
  setStatus(`Ready · ${state.cameraMode} camera · ${waveField.waves.length} waves`);
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
}

function updateBoat() {
  const sample = waveField.sampleHeightAndNormal(boat.position.x, boat.position.z, elapsed);
  boat.position.y = sample.height + 1.15;
  const normal = new THREE.Vector3(sample.normal.x, sample.normal.y, sample.normal.z);
  boat.quaternion.setFromUnitVectors(up, normal);
}

function handleKeyDown(event) {
  keys.add(event.code);
  if (event.code === "KeyC" && !event.repeat) toggleCamera();
  if (event.code === "KeyB" && !event.repeat) {
    state.boundaryVisible = !state.boundaryVisible;
    boundaryPreview.visible = state.boundaryVisible;
  }
  if (event.code === "KeyF" && state.cameraMode !== "free" && !event.repeat) {
    state.foamVisible = !state.foamVisible;
    foam.setVisible(state.foamVisible);
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

window.__ANANTA_WATER_QA__ = {
  sceneReady: true,
  waveCount: waveField.waves.length,
  boundary: boundary.toJSON(),
  sample: waveField.sampleHeightAndNormal(0, 0, 0),
  renderer,
  water,
  foam,
  boundaryPreview,
};
document.body.dataset.qaReady = "true";
setStatus(`Ready · orbit camera · ${waveField.waves.length} waves`);

function animate() {
  requestAnimationFrame(animate);
  const deltaSeconds = Math.min(clock.getDelta(), 0.05);
  if (!state.paused) elapsed += deltaSeconds;
  moveFreeCamera(deltaSeconds);
  if (!state.paused) {
    water.update(elapsed);
    foam.update(elapsed);
    updateBoat();
  }
  controls.update();
  const now = performance.now();
  const frameMs = now - lastFrame;
  lastFrame = now;
  renderer.render(scene, camera);
  overlay.update(renderer, {
    frameMs,
    waveCount: waveField.waves.length,
    cameraMode: state.cameraMode,
    boundaryVisible: state.boundaryVisible,
    foamVisible: state.foamVisible,
  });
}

animate();
