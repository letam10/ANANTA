# R0–C1 continuation contract — 2026-10-20

Checkout D:/GAME/ANANTA, branch main only. Baseline HEAD 9b295109e280752bd3d1ff7640be3bad02f6dc1e; origin/main verified equal. User authorizes incremental phase commits/pushes. Do not create/switch branches. Do not edit AGENTS.md. Initial tracked Unreal source/content/config/project dirty set is empty; preserve any later unrelated dirt and never blanket stage.

## Existing work and sequencing

Roadmap/handoff contain pre-existing uncommitted historical W3/A1–A5 notes; preserve their body and add dated R0/current receipts. Tools/A2–A6, F1, W3 and four A1 scripts already exist untracked; do not silently adopt/rewrite/commit them. The prior ArchitectureAudit folder is unrelated and remains untracked. R0 records P2 bounded visual but not art acceptance; P4A/P4B PARTIAL for fresh runtime; W1/W2 first; 60 FPS target supersedes legacy UI 90 FPS. W3 apply only after fresh browser W1/W2 gate. V1/A1/A2 hero gate before map expansion. S1 audits City and Coastal separately before edits. G1 needs headed runtime, F1 needs headed samples; NullRHI/build are narrower gates. Commit truthful partial phase work where a gate is incomplete; do not call it PASS.

## Shared water contract fixed before delegation

- Source of truth: Prototypes/ThreeWater/public/wave-spec.json, schema ananta.three-water.wave-spec.v2. Canonical hash f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f. Preserve exact 4 direction/wavelength/amplitude/speed/phase tuples and units.
- Stable preset IDs: coast, beach_boat, offshore, durationSeconds=10. Existing ScenePresets exports stay SCENE_PRESETS, getScenePreset(name), applyScenePreset(camera, controls, preset). Match every camera/target to spec; no public API changes.
- Existing HTML entry remains <script type="module" src="/src/main.js">. DOM IDs stay water-canvas/status. main.js owns requestAnimationFrame and dt; no other module multiplies dt by a global speed. Low water/foam geometry allocated once. No FFT/physical buoyancy.
- Three horizontal XZ metres, Y-up; Unreal XY centimetres, Z-up. Position maps 100*(Three.X, Three.Z, Three.Y), direction maps (dx,dz), time seconds, phase radians. Use world cm/100 in HLSL. Function intended outputs BaseColor/Normal/Roughness/Emissive, opaque material, boundary collision separate.

## Independent ownership

1. WATER_CAMERA owns only Prototypes/ThreeWater/src/qa/ScenePresets.js. Fix the verified beach_boat target mismatch, preserving exports and other metadata. No unrelated cleanup.
2. WATER_RECIPE owns only Tools/Continuation_20261020/water_contract.py. Implement complete pure-Python module: load_spec(root: Path) -> dict validates schema/hash; normal_hlsl(spec: dict) -> str returns exact 4-wave world-space UE normal from P cm and T seconds; foam_hlsl(spec: dict) -> str returns nearest-box-edge smoothstep foam from P cm using same spec; camera_pose(scene: dict) -> dict returns position_cm/target_cm/fov_degrees=48. No Unreal imports or execution. Include concise Vietnamese comments for axes/derivatives. Do not mutate spec or write outputs on import.
3. WATER_CHECKS owns only Prototypes/ThreeWater/src/qa/WaterContractChecks.js. Implement exported runWaterContractChecks(spec) returning {passed,checks,errors}; import WaveField, CoastBoundary, ScenePresets. Check finite-difference height derivatives vs analytic normal at several signed coordinates/times, camera/target equality to spec, boundary contains/clamp with margins at box edges/corners. Use actual existing public methods, read modules first. No DOM/browser globals and no execution on import. Report errors rather than silently repair. No default tolerances hiding coordinate errors; use central difference epsilon=1e-3 and component tolerance=1e-5. Root will execute checks after integration.

Parent owns all main.js/package.json/README/docs/integration/Unreal scripts and Git mutation. Agents only edit assigned files, node --check JS (Python agent may use ast.parse without importing target), then return. No servers, browsers, Unreal/Blender, other agents, send_message/followup_task/list_agents, Git stage/commit/push. Root waits with wait_agent timeout_ms>=120000 and performs runtime QA. Every file edit through one exec/apply_patch call for one file.

## Read-only follow-on audit ownership

Shared runtime contracts and phase ordering above remain fixed. No agents may change Source, Config, Content, existing tools or assets. Root owns native execution and integration.

- STREAMING_AUDIT owns only Tools/Continuation_20261020/S1_source_audit.md. Read City and Coastal source/tool/map metadata separately; list World Partition/OFPA, HLOD identity, Data Layers, PCG seeds, loading range and route evidence with exact paths. Source evidence is not fresh cell/runtime evidence.
- HERO_AUDIT owns only Tools/Continuation_20261020/A1_hero_audit.md. Read existing art manifests/review tools and V1 contract; identify hero street/civic assets, provenance/licence, pivots/bounds/LOD/collision/texture hashes, shading and 8/5-view evidence. Do not adopt or change pre-existing untracked A1-A6 work. Report exact gaps before map expansion.
- GAMEPLAY_AUDIT owns only Tools/Continuation_20261020/G1_source_audit.md. Read native Coastal interaction/transit and P4C actor integration paths plus existing QA. Distinguish real input, direct API fixture, source capability and missing implementation. List narrow next fixes and runtime acceptance for NPC schedule, flight, rowing, signals, boarding, bounds and persistence. Do not edit code or run any engine/test.

These agents may only read files, write their single assigned Markdown report and return. No browser, server, engine, Blender, subagents, Git mutations or cross-agent messaging. Root waits >=120000 ms. Camera comparison uses vertical Three FOV 48 degrees; UE horizontal FOV is 2*atan(tan(48/2)*aspect). Native saved reference cameras use 16:9; actual 1422x800 comparison captures use horizontal FOV 76.7157600295933 degrees. Position conversion is 100*(X,Z,Y).

## Delivery gates

R0: ownership manifest + current dated roadmap/handoff W1 prompt, no Unreal changed. W1/W2: npm check/build, canonical spec validator, meaningful CPU contract checks, fresh HTTP/browser smoke t0/t1, orbit/free and controls, all 3 bounded scenes and zero console errors. W3: exact function graph/readback and separate boundary + same-camera images; no prior partial report promoted to PASS. Build/source/import/runtime/performance remain separate. C1 runs Validate-ANANTA.ps1, git diff --check, git lfs fsck; stage exact allowlists and verify remote hash after every push.
