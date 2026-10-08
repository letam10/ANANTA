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
