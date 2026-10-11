# Airport terminal camera anchor repair

Current source: Tools/Editor/CityMetroDistrict.py, airport() calls
shell(layout, 186000, 188000, 750, DistrictLimestone). Airport site centre
(228000, 204000) is a different point and must not be used for terminal close review.

## Writer ownership

- Tools/QA/PrepareFacilityCloseViews.py
- Tools/QA/TestFacilityCloseViews.py (new)
- Docs/CITY_AIRPORT_CLOSE_CAMERA_ROUND.md

Root owns runner integration, manifests, execution status and native capture.
Do not edit map, engine source, factory source, actors, saves or characters.
Do not start Unreal, Blender or build processes. Do not spawn agents or commit.

## Shared constants and API

TERMINAL_LOCATION = (186000.0, 188000.0, 20.0), centimetres.
TERMINAL_TARGET = (186000.0, 188000.0, 425.0).
TERMINAL_SIZE = (6800.0, 5680.0, 810.0), conservative envelope includes canopy/roof.
Keep build_close_views(location, target, site_size) -> list[dict] callable.
Exactly five directions: front/rear/left/right/upper; four eye heights 170 cm.
Orient front towards the -Y entrance, rear +Y, left -X, right +X.
Upper should see the roof and facade with positive camera clearance above the roof.
Use id AirportTerminal. Each record keeps location/rotation/target/direction.
The default CLI writes Saved/QA/CityAirportCloseViews.json, accepted false.

## Required checks

Reproduce the old site-centre error in a regression against airport() source.
Check default camera focus matches the real terminal and rejects site centre as correct focus.
Project all eight terminal-envelope corners through camera transforms, 75 degree horizontal FOV,
16:9 aspect; require positive depth and frame margins for all five views, choosing radius as needed.
Check camera positions outside building envelope, eye heights, directions, deterministic JSON.
Run python -m unittest discover -s Tools/QA -p TestFacilityCloseViews.py.
Run py_compile on both owned Python files, max 300 lines/file and 120 columns.
Report once <=15 lines with files, checks, open issues. No final visual/FPS acceptance.
