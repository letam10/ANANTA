# Airport close camera review round

## Scope

This round supplies five deterministic camera transforms for a closer review of
the Airport terminal.  The existing Unreal map and actors are untouched.  The
script emits a JSON manifest only; it does not move actors, capture PNG files,
or claim that the terminal art is accepted.

## API and assumptions

`build_close_views(location, target, site_size)` receives centimetres in Unreal
coordinates.  `location` is the terminal ground anchor, `target` is the point
the camera should keep in frame, and `site_size` is the terminal envelope.
The function returns exactly five records in this order: `front`, `rear`,
`left`, `right`, `upper`.

The first four records place the eye 170 cm above the supplied ground anchor,
which is a player-scale close review height.  The upper record raises the eye
to show the terminal roof and nearby apron while retaining the same target.
The horizontal radius is derived only from `site_size`, so repeated runs are
deterministic and do not depend on editor state.

## Local check

Run from the repository root:

```powershell
python -m py_compile Tools/QA/PrepareFacilityCloseViews.py
python Tools/QA/PrepareFacilityCloseViews.py
```

The second command writes `Saved/QA/CityAirportCloseViews.json`.  That generated
file is a QA receipt and remains uncommitted.  The script validates record count,
direction order, positive distances, ground-view eye heights, and upper-view
elevation before writing it.

## Acceptance boundary

The manifest proves only that the requested transforms are deterministic and
geometrically valid at source level.  It does not prove that Unreal places the
terminal in frame, that the view is unobstructed, or that facade, apron,
signage, lighting, collision, traversal, performance, or gameplay are correct.
An Unreal capture and human visual review are still required; visual acceptance
is explicitly **not achieved** by this round.

## Corrected terminal anchor checkpoint 2026-10-11

- Camera source now uses the real terminal shell anchor `(186000,188000,20)` and target
  `(186000,188000,425)`. The old airport site centre `(228000,204000)` is rejected by regression.
- Five deterministic directions are emitted as `AirportTerminal`: front toward -Y, rear +Y,
  left -X, right +X and upper. Ground views use 170 cm eye height.
- Every view projects all eight envelope corners with 75 degree horizontal FOV and 16:9 aspect;
  positive depth and a 0.92 normalized frame margin are required before writing the receipt.
- `TestFacilityCloseViews.py`: 7/7 PASS; `py_compile` and manifest generation PASS.
- `Saved/QA/CityAirportCloseViews.json` remains a source receipt with `accepted=false`; no Unreal
  capture or visual acceptance is claimed.
