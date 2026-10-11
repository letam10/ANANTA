# ANANTA city execution contract

Status: implementing the approved 1.2 km city plan, 2026-10-07.
Owner: root integrates map, renderer, import pipeline and end-to-end acceptance.
Do not mark complete until rendered gameplay, persistence and packaged build are verified.

## Fixed scope

- One continuous 1200 x 1200 metre city, world origin at its centre, Unreal centimetres, Z up.
- Commercial/cafe west, residential/apartment centre, transit/anomaly east.
- Photoreal PBR architecture with restrained anime colour and effects.
- Only cafe and player apartment have furnished accessible interiors.
- One arcade player car, up to 24 nearby pedestrians, up to 6 local traffic cars.
- One mission: cafe giver -> three clues -> three enemies -> fragment -> report to giver.
- Windows offline single player, 1080p output around 60 FPS on RTX 4060 Laptop 8 GB / RAM 16 GB.
- Background asset/build work. Short real-input functional tests; no benchmark circuits or stress tests.
- Preserve old ANANTA_Slice map. New map package /Game/ANANTA/Maps/ANANTA_City.
- Root switches default map only after integration passes. No publishing, purchases, unrelated refactors.

## Spatial contract

- Ground walking surface Z = 0 cm; sidewalks Z = 15 cm.
- Roads use X/Y centre lines every 12000 cm from -60000 to +60000 cm.
- Main east-west boulevard is Y = 0, road width 1800 cm, sidewalks 450 cm.
- Mission giver: (-25000, 2400, 110), within cafe facing south.
- Player start: (-25000, 1500, 120), yaw 90, car: (-22000, 500, 70).
- Clues: (-12000, 1800, 100), (1000, 1800, 100), (24500, 2400, 100).
- Encounter centre: (26000, 4500, 100); fragment same centre, enemy radius 400 cm.
- Apartment entrance: (1000, 2500, 15). Root may move set dressing, not these gameplay anchors.
- Roads and sidewalks must have connected collision, including junctions and interior thresholds.

## Runtime contract: gameplay agent owns all Source/ANANTA files

Runtime is C++/Blueprint; Python is editor-only. Keep each new file under about 300 lines.
Use existing ANANTACharacter, combat/traversal and HUD where practical.
Expose these classes/properties so root can author the level through Unreal Python:

1. AANANTACityGameMode (Python ANANTACityGameMode), usable directly as world game mode override.
   It supplies playable character, controller and HUD; original third-person skeleton/animations allowed.
2. AANANTACityVehicle (Python ANANTACityVehicle), root places one actor. VehicleId FName = PlayerCar.
   BodyMesh UStaticMeshComponent public editable; optional wheel visuals, root assigns imported vehicle body.
   Enter/exit with E, drive WASD, brake Space; collision sweep and safe exit required.
3. AANANTACityInteractable, editable InteractionId FName, InteractionKind enum ECityInteractionKind:
   Giver, Clue, Fragment. VisualMesh UStaticMeshComponent. Root assigns the visual meshes.
   IDs Giver_Cafe, Clue_01, Clue_02, Clue_03, Fragment_Anomaly.
4. AANANTACityEnemy, editable EnemyId FName, basic chasing and melee damage/death.
   IDs Enemy_01, Enemy_02, Enemy_03. Activate after three clues. Persist defeated IDs across streaming.
5. AANANTACityCrowd, root places one non-spatial manager. Cap 24 pedestrians, 6 traffic cars.
   Use nearby authored pedestrian routes around the road grid; never spawn inside buildings.
6. UANANTACitySubsystem : UGameInstanceSubsystem owns mission/save state, never actor hard references in saves.
   ECityMissionStage: NotStarted, Investigating, Combat, ReturnToGiver, Completed.
   Methods GetMissionStage(), GetObjectiveText(), TryInteract(FName, ECityInteractionKind),
   RegisterEnemyDefeated(FName), SaveProgress(), LoadProgress(). Public Blueprint callable as appropriate.
   Completed requires fragment AND reporting to giver, reward once, stable unique IDs, save schema version 1.
   Save location and car transform; restore safely after streamed collision exists.
7. IANANTACityInteractable (Unreal interface) optional only if it simplifies shared E interaction.

Bind real keyboard/mouse input including move/look, jump, sprint, mantle, attack, interact and pause.
HUD shows current mission, context prompt, health, car speed when driving; avoid duplicate legacy overlay.
Reuse EnhancedInput if appropriate; ensure mappings exist in cooked game, no editor-only runtime APIs.
Fix old fragment pickup to player-only and restore collected visibility from saved IDs.
Keep NPC/civilian/vehicle actors immune to player mission damage unless explicitly enemy.
Add focused automation for mission invalid order, repeat completion, save/load and duplicate IDs.
Agent may edit Source/ANANTA/** and create Tools/QA/RuntimeSourceAudit.py only.
Do not run Unreal editor, cook, git commit or edit Config/Content/Tools/Editor.
Compile once with Tools/Build/Build-ANANTA.ps1, report errors if shared integration is required.

## Asset contract: asset agent owns Assets/City and Tools/CityAssets

Use Blender background with --factory-startup --python-exit-code 1. Read applicable Blender skills.
Reuse HOUSE CC0 glTF models and texture sets, with complete referenced files and provenance hashes.
HOUSE is read-only. Do not copy CC-BY GlamVelvetSofa; CC0 sofas exist.
Create reusable detailed architecture and props, avoiding plain cube towers and painted fake whole buildings.
Deliver source FBX meshes in Assets/City/Meshes, textures in Assets/City/Textures and original source copies.
Mesh FBX must be centimetres, Unreal import scale 1, Z up, X forward; documented bounds in cm.
UVs, bevels, thickness, material slots and sensible collision/LOD recommendations required.
Buildings are shells; make separate cafe/apartment entry modules with open doorways.
Required kit IDs: FacadeResidential, FacadeCommercial, FacadeTower, Storefront, Cornice,
Balcony, RoofEquipment, StreetLamp, Bench, Bollard, Planter, CarBody.
Facade modules default width 400 cm, height 320 cm, shallow depth; root repeats them over structural shells.
Facade face is -Y, origin at centre of bottom edge. CarBody forward +X, ground at Z=0.
HOUSE furniture IDs prefix House_, imported as combined static FBX with material slots recorded.
Deliver manifest Assets/City/manifest.json with schemaVersion:1, units:cm, upAxis:Z,
meshes:[{id,file,boundsCm,materialSlots:[string],triangles,source,license}],
materials:[{id,baseColor,normal,roughness,ao,metallic,normalConvention}],
sourceFiles:[{file,sha256,source,license}]. Paths relative to Assets/City.
Missing maps use null; never mislabel packed maps as roughness. Colour maps sRGB, others linear.
Materials can include baseColorFactor and metallicFactor; root builds Unreal material graphs.
Review sheet and audit JSON in Saved/QA/CityAssets; inspect rendered sheet before reporting ready.
Do not import into Unreal, change Content/Config/Source, or start UE/builds. Root owns UE imports.

## Integration and acceptance

- Write small idempotent editor scripts, deterministic IDs and report manifests in Saved/QA.
- Copy map, remove only obsolete layout in the copy, build connected road grid and three districts.
- Convert new map to World Partition, OFPA, configure cells ~128m and source radius ~256m, build HLOD.
- Recast with nearby Navigation Invoker, not experimental partitioned navigation.
- Software Lumen, hardware ray tracing off, TSR 83.33%, limited shadow lights; tune from actual GPU evidence.
- Mesh readback, materials connected, collision routes, BP compile, editor build and cooked game build.
- Inspect daylight and blue-hour screenshots in game, cafe/apartment interiors and all district transitions.
- Actual inputs must finish drive/investigate/combat/fragment/report and persist reload exactly once.
- Report incomplete visual/gameplay/performance gates honestly; target 60 FPS is not evidence of achievement.
