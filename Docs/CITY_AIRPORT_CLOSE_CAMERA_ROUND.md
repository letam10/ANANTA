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

