# Expanded city performance review

Root owns map writes, lighting edits, builds, GPU runs and Git.
This is a read-only source audit, not a benchmark or an acceptance claim.
UE 5.8, Windows, RTX 4060 Laptop 8GB, 16GB system memory.
Expanded city: 1472 shell buildings, 6551 HISM groups, 281266 instances, eight interiors.
Preserve all character models and user changes. No subagents.

## Scope and shared interfaces

- Inspect Source/ANANTA/Private/City and Public/City for streaming, lights, crowd, vehicles and services.
- Inspect Tools/Editor/CityExpansionLayout.py, CityExpansionBuildings.py, CityExpansionLandscape.py,
  CityScene.py, CreateCityHLOD.py and Config for relevant runtime settings.
- Geometry units are centimetres. Road grid extent 84000, spacing 12000, save extent 86000.
- CityWorldBounds.h is the runtime authority for those constants.
- HLOD is pending rebuild after dressing. Do not treat stale HLOD as a new code defect.
- Current editor offscreen service walk passed 293 seconds, mean 8.985ms, p95 10.423ms.
  This does not prove packaged sustained 60 FPS or visual acceptance.
- Root is adding MPC_CityLighting.NightAmount and WindowGlass emissive material, plus dressing.
- Do not modify any source, map, asset, configuration, save game or Git state.

## Deliverable

Create only Saved/QA/CityExpansionPerformanceReview.md, less than 150 lines.
Report concrete bottleneck or correctness risks with exact file/line and evidence, ranked by impact.
Separate confirmed issues from hypotheses requiring GPU measurements; omit speculative rewrites.
Check overlapping bounds or mesh material slots only if source demonstrates a concrete risk.
Identify the smallest possible fix, if any, without applying it.
Self-check all cited files and line ranges exist, and report once in at most 15 lines.
No UE, Blender, game processes, benchmark, installation or network operation.
