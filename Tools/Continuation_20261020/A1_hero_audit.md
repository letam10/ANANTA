# A1/A2 hero source audit — 2026-10-20

Status: **SOURCE AUDIT COMPLETE; HERO ART / NATIVE IMPORT / RUNTIME UNVERIFIED**. This report only reads existing evidence and tools. No Blender, Unreal, browser, server, test runner or Git mutation was executed by this audit. Only this report is owned by the audit. Pre-existing untracked A1–A6 scripts and artifacts remain contextual material; they have not been adopted, modified or approved for staging.

## Current contract and bounded hero selection

`Docs/ANANTA_ART_AND_WATER_CONTRACT.md:213–244` defines `Hero_Street_Block_Modern01`, `Hero_Interior_Lobby01`, `Hero_Coast_Seawall01`, `Hero_Traffic_Sedan01`, `Hero_Rail_Station01`, civilian/transit anime NPCs and `Hero_Prop_StreetFurniture01`. These are specification IDs, not proof that a complete native hero package exists. V1 already fixes palette, PBR, 1.75 m human reference / 1.60 m eye height, lighting contexts and a no-map-expansion gate. The world remains modern/semi-realistic; only characters/NPCs use anime.

The concrete first bounded selection available in source is:

| Group | Existing candidates / exact source | Current meaning |
| --- | --- | --- |
| Road / sidewalk / curb / markings | `Tools/AssetPipeline/Generate_Nova_ModularKit.py`; `Tools/A2/BuildStreetCivicHero.py` lists `NovaStreet_Road`, `NovaStreet_Sidewalk_-1/1`, `NovaStreet_Curb_-1/1`, crosswalks, planters, lamps | Static dressing in the A2 manifest; source signal checks do not prove imported or placed geometry |
| Civic facade / transit facade | `Tools/CityAssets/expansion_architecture.py`; A2 review names `FacadeCivic`, `FacadeTransit`, `CivicServiceMarker` | A2 review uses hard-coded local reference bounds, planned eye-level cameras, no headed captures |
| Police / Fire / Bar / Arcade / AmusementPark | `Tools/Editor/CityCivicDistrict.py` | Authored City civic rooms and services; separate from Coastal hero import |
| Street furniture | Original `Assets/CoastalUpgrade/{StreetLamp,Railing,ParkBench,StreetBin,ParkingMeter,TrafficCone,FireHydrant}.fbx`; contextual A4 output adds detail | Eleven-asset A4 tranche also includes FactoryBarrel/Crate/Conveyor/Control; native readback explicitly false |
| Signs / signal / monument / tree | Original Coastal FBX; contextual A3C includes StreetSign, TrafficLight, Monument, ParkTree, OperaShells | Five authored source assets with old headless review manifests; not a native street block acceptance |
| NPC style control | Original `Citizen.fbx`; contextual A6 | Five material-family contract exists; old A6 preview is static dressing with schedule/prompt pending |

`CityCivicDistrict.py` has five SITES, four service IDs and `ENTRY_CLEAR_WIDTH = 480` cm. The generic V1 door reference is 90 × 210 cm; the civic access opening is a different authored opening and must be checked by actual passage/collision rather than silently scaled to the generic door. `Tools/A2/ReviewStreetCivic.py` plans street_eye/civic_front/civic_entry/civic_traffic at 1.60 m and civic_upper at 4.50 m. A camera plan is not capture evidence.

## Provenance, licence, pivot and scale

`Assets/CoastalUpgrade/manifest.json` is dated 2026-10-15, units metres. It contains model name, dimensions, min/max bounds, triangle count, one material section, ground-center pivot and +X forward. It does **not** provide a complete asset-level licence/source URI/import revision/texture provenance chain. Original entries include:

| Model | Dimensions metres | LOD0 source triangles | Pivot |
| --- | --- | --- | --- |
| StreetLamp | 1.89 × 0.30 × 5.6646 | 212 | ground center |
| StreetSign | 0.11 × 1.05 × 2.715 | 168 | ground center |
| TrafficLight | 0.53 × 0.40 × 3.55 | 732 | ground center |
| Railing | 2.50 × 0.09 × 1.10 | 220 | ground center |
| ParkBench | 1.80 × 0.55 × 0.865 | 756 | ground center |
| Monument | 3.40 × 3.40 × 3.32 | 1048 | ground center |
| Door | 0.17 × 0.90 × 2.35 | 168 | ground center |
| Citizen | 0.335 × 0.7681 × 1.90 | 1516 | ground center |

Door height 2.35 m and Citizen height 1.90 m differ from V1 references. Record a deliberate approved exception or adjust only a newly owned hero copy; do not treat this audit as permission to overwrite originals. Updated A4 StreetLamp detail bounds are 2.02 × 0.44 × 5.661542 m, illustrating why old FBX bounds cannot validate the newer artifact.

`Tools/A4/output/a4-street-civic-v1.json` explicitly records `provenanceStatus=in_repo_source_manifest_pending_external_license` and `lodCollision=native Unreal import/collision readback pending`. A repository path and sourceBlend SHA-256 establish identity, not legal ownership or distribution permission.

There is existing reusable licensed material in `Assets/City/Sources/HOUSE/manifest.json`: Poly Haven entries declare CC0-1.0, and GlamVelvetSofa declares CC BY 4.0 with a Khronos source URL. This is a local manifest declaration, not a fresh external licence verification. It does not automatically license Coastal custom generators, output models or textures. Trace the actual selected asset and attribution through its manifest before reuse; do not copy a licence from an unrelated furniture record.

## LOD, collision and material import boundary

`Tools/Upgrade/ImportCoastalModels.py` imports the original Coastal FBX kit into `/Game/ANANTA/CoastalUpgrade/Models`, combines meshes, suppresses imported materials/textures, and applies one shared vertex-color `M_CoastalSurface`. Its LOD reductions are 1.0 / 0.5 / 0.2 at screen sizes 1.0 / 0.25 / 0.08. It removes collision and adds a single box. The script replaces existing assets, so it must not be run unchanged over protected content for this continuation.

`Saved/Upgrade/import-readback.json` is historical native readback of that original kit. StreetLamp reads approximately 189 × 30 × 566.463 cm; StreetSign 11 × 105 × 271.5 cm; Railing 250 × 9 × 110 cm; ParkBench 180 × 55 × 86.5 cm. Each has lod_count=3, collision_shapes=1, materials=1. This is useful original-import evidence, but has no demonstrated package/source hash linkage to the A4/A6 updated blend. It does not prove open space under a bench, rail gaps, door passage, collision response in play or contact after placement.

## Texture reuse and two concrete A1 issues

Original `Assets/CoastalUpgrade/Textures/manifest.json` declares Concrete, Brick, Asphalt, Tile and Sand at 1024 px, physical height-gradient normals, generally 2.4 m tile spans (Brick 2.4 × 1.2 m). Original files include `Concrete_Color.png`, `Concrete_Normal.png`, `Concrete_Rough.png` and corresponding surfaces. This manifest lacks channel SHA-256/perceptual hash records.

`Tools/Upgrade/GenerateA1Textures.py` supports channel semantics/color space, requested versus actual dimensions, source reuse via links/copy, SHA-256 and perceptual hash, plus 1K/selected hero 2K output. Its `find_source` uses suffix matching. Existing generated texture evidence may be reused only after current semantic/content hash checks; no new texture was generated by this audit.

**Issue 1: shading channel selection is too broad.** `Tools/Upgrade/ApplyA1Shading.py:172–185` normalizes names and accepts `stable_key(suffix) in stem`. `_N` becomes `n`, so an occurrence in a material prefix can match an unrelated channel. The existing `Saved/QA/A1ShadingFixed2/coastal-a1-manifest.json` concretely assigns `Concrete_AO.png` to the Normal slot, with the same hash as AO: `87cb3730e785c505be33f3633dcc14e876170f2d8cbf32e893eed06a46c124dc`. BaseColor is `fa1352e9ffaae127a49883f7815f3f4692ae09f9e20cd3fe9668a0eed0634030`; Roughness is `4d3bf63a94aa80046aefb9d8bd5b847b58848a7266cd890dcef49cda3a893bf0`. These are recorded historical manifest hashes, not newly recomputed file hashes. Before adopting this tool, use exact channel suffix/semantic checks and reject AO-as-Normal. Do not infer native material corruption: this audit did not inspect the live graph.

**Issue 2: material mapping is incomplete.** The same A1 output records 72 processed objects in Blender 4.5.1, `visualPass=false`, `textureKeysUsed=[]`; AirportCart's materialKey is CoastalSurface and textureKey is null. Old review metadata contains the label `A1 material textures`, but a generic label alone cannot prove the intended Concrete/Asphalt/PBR textures are attached. Read each material slot, image path, colorspace, channel and hash from the actual selected output.

A4 records `no new raster texture generated; procedural PBR detail only`. This correctly avoids duplicate raster generation but does not establish a full native texture/material readback or prove visual material richness at street distance.

## Shading and review evidence

`ApplyA1Shading.py:434` gates removed `mesh.use_auto_smooth` behind Blender <4.1 plus hasattr; modern versions attempt the Essentials Smooth by Angle node group and its angle socket. Its fallback only sets smooth shading and explicitly does not enforce an angle threshold. AirportCart's existing A1Fixed2 receipt records the asset operator CANCELLED and this fallback. A modifier named Smooth by Angle therefore cannot itself certify actual angle-based hard edges. Bevel/weighted normals are heuristic or metadata-controlled; target selection and evaluated readback remain necessary.

`Saved/QA/A1Reviews/20261016-A1/coverage.json` contains eight model records, each eight rendered views. The sibling placement coverage has eight placements. The `20261016-A1-placement-real/placement-coverage.json` additionally records real source-layout positions, scale/yaw/pitch, transformed bounds and five camera transforms/image paths per placement. Example StreetLamp: position [-167.6,-192,2.16] m, scale [1,1,1], yaw 180°, bounds [-169.4,-192.15,2.16] to [-167.51,-191.85,7.82463] m. Its acceptance remains pending_headless_render_only. The source `RenderA1Reviews.py` includes actual placement duplication and matrix_world bounds for rendered placement, unlike a camera-plan-only report.

Contextual old artifact counts, as declared in their review JSON:

| Package | Objects | Eight-direction images | Five-angle images | Native readback |
| --- | ---: | ---: | ---: | --- |
| A3C authored street/venue/tree | 5 | 40 | 25 | false; human review pending |
| A3D vehicle detail | 8 | 64 | 40 | false; human review pending |
| A4 street/civic/factory | 11 | 88 | 55 | false; native import pending |
| A5 interior/venue props | 12 | 96 | 60 | false; native import pending |
| A6 Citizen | 1 | 8 | 5 | false; native import pending |

Important limitation: `Tools/A4/ReviewStreetCivic.py` calls the inherited `Tools/A3B/ReviewHeroDetail.py` setup/render_set. combined_bounds uses target/child matrix_world; render_set moves cameras around that blend asset. The manifest records transformed bounds but does not record actual Unreal actor transforms, map package identities or collision readback. This is five camera angles around a source artifact, not proof of five-angle important placement review in the game. `Tools/A2/ReviewStreetCivic.py` also uses hard-coded bounds and yaw=0/scale=1 fixture placements; its transforms are not map readback.

This audit visually opened only three existing 320 px images: A4 StreetLamp azimuth_045, A4 ParkBench azimuth_045, A6 Citizen azimuth_045. Lamp pole/head and bench slats/supports are readable; bench surfaces remain visually simple, and Citizen is visibly primitive/block-based. These limited observations are not an eight-direction review, new renders, style acceptance, rig/animation evidence or native lighting acceptance. The remaining images were inventoried/read through manifests, not all visually approved.

## Interaction evidence boundary

Historical `Saved/QA/A2/street-civic-hero.json` cites CityCivicCheck/Report.json: map ANANTA_City, scope authored-map physics/input fixture, eight legs, four services Police_Read/Fire_Read/Bar_Read/Arcade_Read, collisionBypass=false, passed=true. `street-civic-review.json` says sourceGate/runtimeInteractionGate PASS but visualPass=false. No fixture was rerun here; report age/build/source identity is not refreshed. This narrower City service evidence does not certify new Coastal actor hooks, amusement park interactions, furniture interactions or real NPC schedule.

## Exact next gates before map expansion

1. Root must explicitly select a bounded newly owned hero package and connect its stable Hero IDs to existing source asset IDs; leave original Assets/Content and pre-existing untracked artifacts protected.
2. Resolve each selected asset's provenance/source/licence, source/output SHA-256, import revision, pivot/forward, local bounds and triangle budget. Check licensed reuse against the actual selected material/model, not an unrelated manifest.
3. Repair/adapt the A1 channel selector in an owned tool before use; prove wrong-channel rejection, actual texture/material mapping, normal colorspace and existing-channel reuse. Record SHA-256 plus perceptual hash and 1K/2K rationale. Do not generate all seven channels for every material without need.
4. Confirm installed Blender API and real Smooth by Angle threshold on evaluated geometry, intentional hard edges and only necessary bevel/weighted normals. Render fresh eight directions **after** shading changes; review all images and record failures explicitly.
5. Import only selected hero copies into an isolated native asset path; read back material graphs/slots, source revision, bounds, LOD screen sizes/triangles, collision shapes and response. Old original-kit LOD/readback cannot be substituted for revised A4 geometry.
6. Place important assets in a bounded hero scene, read actual actor translation/yaw/scale and bounds including children, then generate five views from those transformed bounds. Check curb/ground contact, entry clearance, rail/bench gaps, pivots, collision and camera occlusion.
7. Capture fresh eye-height street/interior/coast/traffic/NPC contexts with camera transform/FOV, renderer, resolution, exposure and lighting preset. Resolve the 1.90 m Citizen / 1.75 m reference discrepancy and assess anime silhouette/materials alongside world lighting. Three old thumbnails cannot satisfy this.
8. Classify each selected venue enterable+interactive, enterable+static dressing or shell-only. Capture fresh normal-input interaction logs for any interactive label; keep source, direct-API fixture and native-input evidence separate.
9. Hold map expansion until those bounded visual/import/placement gates pass. About 60 FPS remains a separate headed F1 measurement requirement; no source tool, old image count, import receipt, config, build or NullRHI result can satisfy it.
