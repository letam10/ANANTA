# Facility dressing round contract

Scope: add measurable source-level Factory dressing and an Airport close camera review plan.
The existing ANANTA map, Content/ExternalActors, character assets, saves, and generated Unreal
map actors are out of scope and must not be edited or staged by these subtasks.

Factory subtask owns only:
- Tools/Editor/CityMetroDistrict.py
- Docs/CITY_FACTORY_DRESSING_ROUND.md

Airport camera subtask owns only:
- Tools/QA/PrepareFacilityCloseViews.py
- Docs/CITY_AIRPORT_CLOSE_CAMERA_ROUND.md

Factory API contract: factory(layout, x, y, height, material) in CityMetroDistrict.py remains callable by
CityMetroDistrict.generate. It must preserve the same shell footprint and reserve bounds.
New dressing must use existing Layout.box/Layout.add calls, shared mesh names where possible,
collision false for visual-only pieces, and keep all new source files under 300 lines and 120
columns. The source must remain deterministic and must not touch characters or saves.

Airport camera API contract: build_close_views(location, target, site_size) returns exactly five
records with direction values front, rear, left, right, upper. It must keep the terminal in frame,
use ground-level eye heights for four views, and emit only JSON/documentation. No actor movement.

Done criteria: both modules pass Python compilation; each writes a concise evidence document;
Factory preserves footprint constants and adds named loading/yard details; Airport manifest has
five deterministic views and explicit visual-review limits. Do not build Unreal, edit map actors,
or claim final art/performance acceptance.
