# City service journey acceptance contract

Root integrates map and runs all processes. No other agent/build is running in source ownership.
Goal: a normal short input-driven visit to the eight accessible venues, bounded to 360 seconds.
No benchmark, teleport, direct Interact invocation, mission mutation, damage/health injection or god mode.
Do not spawn agents. No Unreal/builds, assets, map, Docs status or other QA edits.

## Owned files and API

Create Source/ANANTA/Public/QA/CityServiceJourney.h and corresponding Private/QA/CityServiceJourney*.cpp.
May edit ANANTACitySubsystem.cpp ONLY to make -CityServiceCheck start fresh in QA save slot,
and recognize -CityServiceReload as QA; preserve every other initialization path.
Use existing UCityInputSmokeSubsystem / UCityMissionCheckSubsystem as read-only API examples.
Subsystem should exist only for game worlds with -CityServiceCheck or -CityServiceReload and -CityQASlot.
Root adds runner modes. End success via RequestExitWithStatus false 0, failure 1, bounded wall clock.
Use PC InputKey WASD/Shift/E/F5, set controller facing for waypoint travel, maintain collision and normal speed.
Each new file <=300 lines, <=120 columns, short Vietnamese comments for complex behavior.

## Authored route data

Read Tools/Editor/CityExpansionData.py and CityExpansionVenues.py for authoritative coordinates.
Existing cafe east-facing front x=-25350/y2400, service Cafe_Rest at (-26000,2400,100).
Existing apartment west-facing front x=1350/y2500, service Apartment_Rest (2200,2600,95).
New venues have service inside at frontX-face*330, centreY, z80.
Travel between locations along y=1100 or y=-1100 sidewalks/road edge. Before entering a venue,
walk along the nearby vertical-road sidewalk to its doorway centreY, then through centre of doorway.
Leave via the reverse entry route. Do not cut diagonally through shell buildings.
Recommended order Cafe, Market, Bookshop, Clinic, Apartment, Gallery, Workshop, Transit.
Mission anchors/characters unchanged. No direct interaction calls; only E when normal controller target matches.

## Verification

- Confirm each expected service actor is streamed and is the normal interaction target before E.
- Confirm expected VisitedIds after each service, Market supply once, repeat E does not increment again.
- Rest/Heal may happen at full health; record that injured-player healing is not exercised by this journey.
- F5, verify saved data on disk by loading the QA slot without mutating live state.
- Separate -CityServiceReload process loads eight visits, one supply, and compares final player transform
  to a checkpoint file saved by the journey; repeat Market claim need not be revisited during reload.
- Report normal mission remained NotStarted, no bypasses, actual wall time, current map, visited IDs.
- Observe frame times during ordinary journey after ready; include mean and p95 frame milliseconds,
  frames over 33.3 ms and 50 ms with sample count. Label as observations of this short play, not benchmark.
- Save report in Saved/QA/CityServiceJourney/Report.txt (Reload.txt for reload), checkpoint JSON or text.
- Log CITY_SERVICE_JOURNEY_FINISH mode=Check success=1 and mode=Reload success=1 exactly.
- On failure write actual pawn position/current target/step and do not silently skip a venue.

Self-check: source structure, bounded flags, key release on all exits, no shipping subsystem,
and report ONCE <=15 lines with files/APIs, checks, required root compile/runtime checks.
