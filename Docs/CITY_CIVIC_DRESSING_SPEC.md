# Civic dressing plan: Low Tide and Pixel Pier

Coordinates are Unreal centimetres. Site anchors and room geometry come from
`Tools/Editor/CityCivicDistrict.py`; its `x,y` below are Bar `(-36000,-6000)`
and Arcade `(-24000,-6000)`. Keep `FLOOR_Z=15` and the source's 480 cm
door/access lane. This is a placement specification, not evidence of an
engine readback or visual acceptance.

## Evidence and bounds

- The current GPU views are `Saved/QA/CityCivic/View_03.png` (Bar) and
  `View_04.png` (Arcade). Bar has widely separated tables, chairs, and a
  counter run; Arcade has a broad empty middle and two visible detailed
  cabinets.
- Bar shell footprint is 3400 x 3600 cm centered at `(x+3500,y)`;
  interior limits are approximately `x+1800..x+5200`, `y-1800..y+1800`.
  Arcade uses the same shell. `access_lanes()` runs between
  `(x+1380,y-240)` and `(x+4720,y+240)` with 480 cm clear width.
- `ArcadeCabinet` bounds are `[-36,-40.2,0]..[48,40.2,191]` cm,
  84 x 80.4 x 191 cm, 8,944 triangles (`Saved/QA/CityLivingAssets/build.json`).
- Bar detailed assets already authored: `Refrigerator` bounds
  `[-34.8,-38,0]..[47.75,38,176]`, `Microwave` bounds
  `[-19,-28.05,0]..[27.2763,27.5,32.5]`, and `KitchenSink` bounds
  `[-30,-35.5,0]..[30,35.5,57.5694]` cm. `FireExtinguisher` is
  `[-9.8,-9.8,0]..[10.6,15.08,55.2]` cm. These are manifest-local bounds.
- The placement manifest records 19 authored living details; it explicitly
  says map readback and runtime are not verified and HLOD rebuild is required
  (`Saved/QA/CityLivingAssets/placement-source.json`, `applied.json`).

## Low Tide bar

Keep the existing furniture as three readable groups, with a clear diagonal
entry/service route through the room:

| Role | Mesh | World centre(s) | Yaw | Budget |
| --- | --- | --- | --- | ---: |
| Service counter run | `CafeCounter` | `(x+2800,y+1300,15)`, `(x+3250,y+1300,15)`, `(x+3700,y+1300,15)` | 0 | 3 |
| Dining tables | `CafeTable` | `(x+2600,y-1050,15)`, `(x+3550,y-1050,15)`, `(x+4400,y-1050,15)` | 0 | 3 |
| Seating | `House_dining_chair_02` | each table at `(same x,y-1300,15)` and `(same x,y-800,15)` | 0 | 6 |
| Existing detailed bar assets | `Refrigerator`, `Microwave`, `TableLamp`, `KitchenSink`, 4 sink-leg cubes, `FireExtinguisher` | Keep manifest transforms | As authored | 9 |

The table and counter positions match `room_details()`; detailed transforms
match `CityLivingDetails.describe()`. Do not add stools or chairs along the
`y+1300` counter edge. Keep the existing slat panel at `(x+3500,y+1760,180)`
and route display/service desk on the east wall. No new dynamic lights.

**Bar budget:** 21 total placement instances including existing detailed
fixtures; zero new instances. Budget 9 existing living-detail actors, plus
12 source furniture placements. The detailed living mesh assets are
individual actors in the current authoring path, so this is an instance
budget, not a claim that they already share an HISM. If converted to HISM,
cap at 16 mesh/material/collision groups for the existing fixtures, based on
the manifest slot counts (including one shared `Cube` material group for the
four legs); do not split groups by yaw. The 12 furniture mesh bounds are not documented
in the living manifest, so verify those transformed bounds before changing
their positions.

## Pixel Pier arcade

Retain the two `ArcadeCabinet` living details already at `(x+4700,y-1250,15)`
and `(x+4700,y+1250,15)` (the source yaws them toward the room). Add six
instances on the same two side rows to fill the long walls. Replace the six
procedural box cabinet stand-ins from `arcade_cabinet()` at those coordinates;
do not leave both representations in place.

| Local X | World centre, negative-Y row | World centre, positive-Y row | Yaw |
| ---: | --- | --- | --- |
| 2550 | `(-21450,-7250,15)` | `(-21450,-4750,15)` | +90 / -90 |
| 3300 | `(-20700,-7250,15)` | `(-20700,-4750,15)` | +90 / -90 |
| 4050 | `(-19950,-7250,15)` | `(-19950,-4750,15)` | +90 / -90 |

These rows leave the room centre open. With the 84 x 80.4 cm local bounds,
the long-row footprints stay clear of the 480 cm diagonal access lane; retain
the prompt/service approach at `x+4730` and do not place a cabinet beyond
`x+4050` except the two already-authored `x+4700` cabinets. Keep the existing
wall neon and extinguishers clear.

**Arcade budget:** 8 `ArcadeCabinet` instances total (2 existing + 6 proposed),
all collision enabled, one mesh group per streamed cell and up to 3
mesh/material/collision groups because the asset has three material slots.
The six old procedural cabinets use 42 `layout.box()` calls in total (7 each);
removing those stand-ins avoids visual and collision duplication. No dynamic
lights.

## Source references and limits

- `Tools/Editor/CityCivicDistrict.py:4-24`: site anchors, entry width, floor,
  shell dimensions, and access lane; `:64-90` has bar/arcade layouts and
  `:106-113` defines the seven-box arcade stand-in.
- `Tools/Editor/CityLivingDetails.py:26-44`: current detailed fixture
  transforms and cabinet yaw.
- `Saved/QA/CityLivingAssets/build.json:451-480` and
  `placement-source.json:318-344`: ArcadeCabinet bounds/triangles and current
  placed transformed bounds. Other cited bounds are adjacent build records.
- The plan derives coordinates from source and local asset bounds. It does
  not validate UE actor bounds, map readback, collision, HLOD, or final in-game
  appearance. Validate transformed overlaps and lane width before applying.
