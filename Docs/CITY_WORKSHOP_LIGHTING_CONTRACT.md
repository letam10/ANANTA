# Workshop detail and daylight diagnosis — 2026-10-08

## Shared boundaries

- Workspace D:/GAME/ANANTA; UE 5.8.3, Blender 5.2, centimetres, Z up.
- Full HLOD builder is live. Do not launch Unreal, write Content or alter existing map inputs.
- Preserve characters, services, collisions, ordinary gameplay routes and player saves.
- No benchmark, hosting, purchases or copying assets from the reference games.
- At most two subagents; no grandchildren. Root owns integration, progress docs and Git.

## Workshop asset contract

- New mesh IDs: WorkshopToolBoard and WorkshopPartsCrate.
- ToolBoard bounds min [-140,-7,0], max [140,7,140] cm; at most 8,000 triangles.
- PartsCrate bounds min [-70,-55,0], max [70,55,70] cm; at most 5,000 triangles.
- Geometry origin at bottom centre; visible front Blender -Y, exported UE +Y.
- ToolBoard: bevelled perforated metal panel with recognizable spanners, sockets and screwdrivers.
- PartsCrate: weathered slatted wood shipping crate, reinforced corners and legible original parts label.
- Keep exact bounds so existing dressing footprints and clear corridor remain unchanged.
- Use original geometry/art and licensed existing PBR; max 2K maps, at most four material slots each.
- New materials use Workshop_ prefix; never change shared existing materials.
- Assets/City/workshop_detail_manifest.json follows interior_architecture_manifest.json schemaVersion 1.
- Required mesh fields: id, file, boundsCm, materialSlots, triangles, source, license, sha256, visibleFront.
- Texture/material metadata follows the same manifest conventions; include source provenance/hashes.
- Authoring root: Assets/City/WorkshopDetail; FBX files in Meshes and maps in Textures.
- Source scripts: Tools/CityAssets/workshop_detail_*.py; optional importer ImportCityWorkshopDetail.py.
- Root will replace Dressing_Workshop_ToolBoard and its six ToolRail children with one tool-board mesh.
- Root will replace Dressing_Workshop_PartsCrate with a crate at the same XY and bottom Z 15.
- Do not edit dressing/layout/QA files; root will integrate once source models pass.
- Self-check: headless Blender factory startup, exit-code 1; FBX roundtrip, UV, bounds, material slots,
  finite geometry, no degenerate faces, source hashes; render front and three-quarter and inspect images.
- Evidence output: Saved/QA/CityWorkshopDetailAssets; CPU renders only, one Blender job, at most two threads.

## Daylight diagnosis contract

- Read-only source/asset inspection; do not run Unreal or change render settings.
- Inspect Saved/QA/CityFinishing/View_03.png and View_04.png plus BlueHour counterparts.
- Trace window shader, exposure volume, directional/sky/interior light and runtime overrides.
- Record exact files, controls and values; distinguish measured evidence from hypotheses.
- Deliver Saved/QA/CityDaylightDiagnosis.md, max 120 lines, with one minimal proposed fix and verification plan.
- Do not claim visual acceptance from configuration alone or recommend broad exposure changes without evidence.
- Keep final agent report to at most 15 lines: files, checks, findings, open issues; report once.
