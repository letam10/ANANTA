# City mobility and second expansion — shared contract

Updated 2026-10-08. User confirmed doubling BOTH dimensions: about 3.4 x 3.4 km (4x current area).
RoadExtent becomes 168000 cm, SaveExtent 170000 cm; preserve the existing central playable districts.
User requests collision repairs, fixed NPC transport routes,
boarding/alighting, eleven vehicle types, richer architecture/props and another doubling of area.
Maximum graphics target remains 90 FPS, not accepted. Preserve character models and normal saves.

## Ownership

- Collision agent: character movement, player vehicle collision/exit, collision QA only.
- Asset agent: new fleet/street kit source assets and dedicated Blender generators only.
- Root: NPC fleet runtime, integration/import, city layout/architecture, documentation, build and publishing.
- No agent runs Unreal, modifies Content, commits, or spawns other agents.

## Coordinates and assets

- Unreal centimetres, Z up, vehicle nose +X, right side +Y, mesh origin ground/waterline centre.
- Blender authoring metres, explicit FBX centimetre export matching existing venue fixture pipeline.
- Destination: /Game/ANANTA/City/Meshes/SM_<id> and Materials/M_<id>.
- Fleet ids: Coach, CityBus, Taxi, BoxTruck, CargoTruck, TankerTruck, PoliceCar,
  Ambulance, CargoShip, Motorboat, Sailboat.
- Road vehicles: closed visible shells, visible windows/seats, doors, wheels, lights, mirrors,
  grille and distinct livery; passengers use existing Quinn mesh, not newly modelled characters.
- Vessel hulls: bow +X, keel below Z=0, deck above; no simulation requirement for source assets.
- Root uses swept runtime primitive bodies rather than FBX collision for moving vehicles.
- Default road clearance 5 cm. Root collision half-height is derived from manifest bounds.
- No fictional FPS claims. LODs and textures must have measurable budgets.

## Asset delivery API

- New assets exclusively Assets/City/Mobility/ and Assets/City/mobility_manifest.json.
- Tools exclusively Tools/CityAssets/mobility_*.py, QA Saved/QA/CityMobilityAssets/.
- Manifest schemaVersion=1, units=cm, upAxis=Z, forwardAxis=X; meshes/materials/sourceFiles arrays.
- Each mesh: id, file relative to Assets/City, boundsCm {min,max,size}, triangles,
  materialSlots, sha256, source, license, lodRecommendation {screenSizes,triangleRatios}.
- Each material follows finishing_materials.entry and existing import schema.
- Extra props: DetailedPlanter, DetailedStreetLamp, TrafficSignal, RoadBarrier,
  HarborBollard, BusStopSign. Keep mesh sources editable and provenance explicit.
- Asset budget: road mesh <=25000 triangles, vessel <=40000; props <=12000;
  <=6 material slots per mesh; shared 1K or 2K base/normal/roughness textures where useful.
- Builder and auditor runnable in background Blender; report exact commands and outcome.
- Do not create labelled boxes alone: silhouettes, functional parts and UV textures are required.

## Collision interfaces

- Existing character capsule radius38, halfHeight92; preserve input bindings and save format.
- Existing AANANTACityVehicle::Drive(float,float,bool,float) and FindSafeExit stay compatible.
- CityWorldBounds::RoadExtent / SaveExtent are root-owned; remove stale literal bounds by using them.
- Agent must not edit crowd/pedestrian classes: root is replacing traffic with dedicated actors.
- New regression tests use ANANTA.City.Collision prefix; no GPU benchmark or user save changes.
- Collision fixes require demonstrated code/geometry cause and an executable regression;
  do not indiscriminately enable triangle collision on every mesh.

## Root NPC mobility interfaces

- Dedicated ACityRouteVehicle actor with Configure(kind,route,mesh), stopped/boarding/travelling states.
- Dedicated ACityTransitPassenger using existing skeletal model and collision-safe walk/seat/alight phases.
- Routes are authored cardinal main-road segments, lanes at +/-420 cm, public stops on sidewalk.
- Traffic waits for blocking obstacles and streamed ground; never teleports through obstructions.
- Fleet spawned only near player with bounded population; fixed route data independent of camera direction.
- Boats require authored water corridor and pier; do not spawn vessels on streets.
- NPC passenger visible walking to/from stopped vehicle; collision disabled only while seated.
- One route vehicle owns its passengers; actor cleanup releases them without touching other crowd actors.

## Verification and delivery

1. Collision regression + Editor/Game build.
2. Mesh audit, import/reopen and GPU images.
3. Ordinary short route walk/drive/board/alight tests with isolated QA config/save.
4. Expanded connected layout counts/bounds and preserved mission anchors.
5. Honest Max FPS/stability observations; update CITY_EXECUTION_STATUS and commit/push.

## Civic/coast module delegation

- Civic agent owns only Tools/Editor/CityCivicDistrict.py, CityCoastalDistrict.py,
  CityDistrictMaterials.py and Tools/QA/VerifyCityDistricts.py.
- Root owns integration. Do not run Unreal or mutate Content. No subagents.
- API: CityCivicDistrict.RESERVES and CityCoastalDistrict.RESERVES are tuples of
  (minX,minY,maxX,maxY); CityCivicDistrict.generate(layout), CityCoastalDistrict.generate(layout).
- layout.add(mesh, location, scale=(1,1,1), yaw=0, material=None, collision=True).
- layout.box(material, location, size, collision=True); units centimetres, all coordinates absolute.
- Optional CityCivicDistrict.furnish() spawns service/text/detailed interior actors only through
  existing CityScene/CityServiceInteractable, prefix District_; called after layout application.
- CityDistrictMaterials.create() imports/reuses existing project PBR textures with new tints/materials.
- Civic sites: Police (-60000,6000), Fire (-48000,6000), Bar (-36000,-6000),
  Arcade (-24000,-6000), AmusementPark (-12000,-6000); each reserve <=9000x9000 inside its block.
- Need distinct accessible architecture with entrances >=240cm clear, corridors >=240cm;
  no unnecessary furnished upper floors. Police/Fire/Bar/Arcade may have Read service prompts.
- Coast reserve (120000,-168000,168000,-120000), city roads terminate at this coastal cutout.
- Water level -120; seabed -1600; no invisible walkable surface over water.
- Boats dock centre X=131000/135200/139400, Y=-141000, initially head +Y.
  Their right side is -X. Author piers on west side, sidewalk gangway to door, not blocking hull path.
- Coast includes beach, piers, cargo yard with container/gantry details and bollards/railings.
- Use existing meshes plus new DetailedPlanter/DetailedStreetLamp/TrafficSignal/RoadBarrier/
  HarborBollard/BusStopSign. Materials must be created by CityDistrictMaterials.create().
- Do not imply final art acceptance from source. Self-check generated bounds/collisions/clear entries
  and compile Python without Unreal; report required engine verification separately.

## Living detail and play equipment kit

- Detail asset agent owns Tools/CityAssets/living_*.py, Assets/City/LivingDetails/**,
  Assets/City/living_manifest.json, Saved/QA/CityLivingAssets/** only.
- Same manifest/import/export schema as Mobility above; editable sources/provenance required.
- Requested ids: CeilingFan, TableLamp, WallAirConditioner, Refrigerator, Microwave,
  KitchenSink, FireExtinguisher, CivicMonument, PlaygroundSlide, PlaygroundSwing, ArcadeCabinet.
- Reuse a suitable existing HOUSE asset with verified license if present; otherwise author originals.
- Geometry/UV/PBR detail and recognizable functional parts, not plain boxes with names.
- Meshes use ground/base origin; front +X, up Z, centimetre FBX. CeilingFan origin at ceiling mount.
- <=18000 triangles per ordinary prop, <=30000 monument/play equipment; <=5 material slots.
- Shared 1K/2K textures, finite normal/UVs, triangulation/bounds/hash audit.
- No Unreal/content/import/build/push/subagents/GPU rendering; root will integrate and view.

## Fleet verification module

- Fleet QA agent owns Public/QA/CityFleetCheck.h, Private/QA/CityFleetCheck*.cpp,
  Private/Tests/CityFleetTests.cpp, Tools/Build/Test-CityFleet.ps1 only.
- Use current CityRouteVehicle/CityTransitPassenger public API read-only; do not edit gameplay classes.
- Test all 11 imported transport kinds in isolated physical fixtures and/or real routes with
  -CityFleetCheck -CityQASlot; normal saves/config untouched. No benchmarks or FPS claims.
- Collision stop, clear road/deck, boarding, travel, alighting and cleanup need observable assertions.
- Existing root CityTransitCheck follows an actual coach via ordinary W/Shift. Do not duplicate it.
- Controlled fixtures may relocate setup actors; label them explicitly as fixtures rather than ordinary gameplay.
- No Unreal launch/build or Content changes. Root compiles/runs; report required commands once.

## Living details integration

- Integration agent owns Tools/Editor/ImportCityLiving.py, CityLivingDetails.py,
  ApplyCityLivingDetails.py and Tools/QA/VerifyCityLivingPlacement.py only.
- Read living_manifest.json and existing ImportCityMobility.py / CityScene helpers as API contracts.
- Import API main(): verify hashes, create materials, import 11 meshes, generate recommended LODs,
  write Saved/QA/CityLivingAssets/import.json; no engine execution by agent.
- Placement API CityLivingDetails.furnish(): deterministic Living_ actor labels, retain other actors.
  Place all 11 kinds in appropriate existing accessible apartment/civic/playground locations.
  Use real room coordinates from existing scripts; keep 240 cm paths and doorway clearance.
- ApplyCityLivingDetails.py removes only Living_ actors, calls furnish(), saves dirty map/packages.
- VerifyCityLivingPlacement.py validates placement bounds/entrance clearance and manifest coverage
  without Unreal; output Saved/QA/CityLivingAssets/placement-source.json.
- No shared script edits, no Content/UE/build/GPU/commit/subagents. Root runs import/apply/capture.

## Rendering investigation

- Read-only investigation; may write Saved/QA/CityRenderingNextSteps.md only.
- Read current render config, previous crash evidence and engine VSM/Nanite source.
- Search official Epic documentation for frustum/occlusion, HLOD, VSM non-Nanite cost and samples.
- Identify at most three concrete measured experiments suitable for ordinary Max gameplay,
  preserving native resolution and quality labels; include exact existing cvars and doc URLs.
- Do not change code/config/Content, launch tools/UE, benchmark, promise FPS or spawn agents.

## Ferris wheel visual repair

- Agent owns Tools/CityAssets/ferris_*.py, Assets/City/Ferris/**,
  Assets/City/ferris_manifest.json, Tools/Editor/ImportCityFerris.py, Saved/QA/CityFerrisAssets/** only.
- Replace coarse block ring with original authored detailed FerrisWheel static mesh.
- Shared importer schema same as living_manifest.json; 1 mesh, <=60000 triangles, <=5 materials,
  shared 1K PBR textures with UVs, source Blend + FBX, hashes and physical bounds audit.
- Mesh ground origin centre XY; wheel plane YZ, hub Z1835, radius1550 cm, top3385 cm,
  width <=1400 cm. Mesh placed at (AmusementPark anchor X+7450,Y+1700,15).
- Smooth metal rims/spokes/supports, eight detailed enclosed cabins and visible mechanical joints.
  Original project content; no reused unlicensed art. Static ride, no animation claim.
- Import script uses CityMaterials/create_material and ImportCityAssets/import_mesh, recommended LODs.
- Self-check via background Blender build/audit and CPU contact sheet; inspect image; verify bounds,
  finite UV/normals, no degenerate topology and source hashes. No Unreal/Content/build/commit/subagents.
- Root handles replacement of old blocks, collision and GPU acceptance. Report once <=15 lines.

## Authored harbour route physics check

- Agent owns Public/QA/CityHarborCheck.h, Private/QA/CityHarborCheck*.cpp,
  Tools/Build/Test-CityHarbor.ps1 only. No shared gameplay/Content edits, no subagents or Unreal launch.
- UTickableWorldSubsystem enabled only by both -CityHarborCheck and -CityQASlot, never Shipping.
- Use current ACityRouteVehicle Configure(kind, CityMobility::MakeRoute(kind), mesh, 0),
  GetBoardingCount(), GetAlightingCount(), GetBlockedReason(), IsStopped(), actor position.
- Test three vessels together in the actual city map and imported meshes at their authored docks.
- Explicitly label this an authored-map physics fixture: observer relocation/streaming setup allowed,
  no artificial support floors, changed route speed, moved piers, collision bypass on vessels/passengers.
- Keep all dock/route cells streamed, prevent manager creating duplicate vehicles during this QA only.
- Require observable boarding, outbound travel >9000 cm, return near original dock, alighting,
  no below-water movement or permanent blocker. Timeout <=180 seconds after world readiness.
- Preserve normal saves/settings; isolated config. Report Saved/QA/CityHarborCheck/Report.json
  with all three per-kind outcomes, distances/counts, reason, elapsed and explicit fixture scope.
- Exit nonzero if any missing/failed result. Runner validates fresh report, three kinds and all PASS.
- Self-check source constraints/PowerShell parsing; root compiles/runs engine. Report once <=15 lines.
