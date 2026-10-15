# Expanded city ordinary traversal acceptance

## Shared interface and ownership

- UE 5.8.3 project D:/GAME/ANANTA. New opt-in nonshipping QA only; preserve gameplay and character models.
- Agent owns Source/ANANTA/Public/QA/CityStreamingJourney.h and Private/QA/CityStreamingJourney*.cpp only.
- UCityStreamingJourney : UTickableWorldSubsystem; ShouldCreateSubsystem, Tick, Deinitialize, GetStatId overrides.
- Command flag -CityStreamingCheck; require -CityQASlot and ANANTA_City game world.
- Root owns runner modes, builds, actual runtime checks, docs and Git. Agent must not run Unreal or build.
- No subagents, Content mutations, settings changes, speed overrides, teleport, time dilation or benchmark mode.
- At most 300 lines per file and 120 columns. Follow existing QA style and use short Vietnamese comments.

## Concrete route and behavior

- Read CityInputSmokeSubsystem and CityServiceJourney for real InputKey events, ready gate and cleanup.
- Require the isolated fresh QA start used by the current controller; never alter the normal user save slot.
- Initial route follows the cafe sidewalk from the fresh spawn, then joins x=-22900, y=1100 cm.
- Walk/sprint using existing W and LeftShift bindings north on x=-22900 to y=73100 cm.
- Then follow y=73100 east to x=73100 cm, on the sidewalk adjacent to road y=72000.
- Confirm the route against Tools/Editor/CityExpansionData.py and CityExpansionLayout.py.
- Stop at the north and northeast endpoints. Release movement keys and turn the camera 180 degrees.
- Capture before/after the turn at both endpoints: NorthForward.png, NorthReverse.png,
  NorthEastForward.png, NorthEastReverse.png in Saved/QA/CityStreamingJourney.
- Use existing screenshot APIs from local UE headers and the existing capture subsystem.
- Bounds use centimetres. Reach tolerance <=60 cm; no jumps across route segments or recovery teleport.
- Hard upper bound 300 seconds overall, with meaningful movement/stall and readiness timeouts.
- If the normal route cannot finish in this budget, report failure; do not increase player movement speed.

## Evidence and pass conditions

- Write Saved/QA/CityStreamingJourney/Report.txt with complete and success flags, elapsed wall time,
  observed route endpoint positions, total displacement/path distance and held-key input provenance.
- Record frame intervals from the ordinary play session, max gap and counts above 33.3/50 ms.
- Record streaming completion at each settled endpoint using supported local WorldPartition APIs.
- Validate ground contact along the route with ordinary world collision, ignoring the hero itself.
- Log camera angles and save screenshot paths; verify all four files exist before success.
- End marker exactly CITY_STREAMING_JOURNEY_FINISH success=1 on success, success=0 on failure.
- Nonzero exit on failure; release keys on transitions, finish and Deinitialize.
- No claims of globally stable 60 FPS, perfect culling or visual acceptance based only on this check.
- Self-check source line limits and inspect local UE API declarations; root will compile and run once integrated.
- Report once, at most 15 lines: files, checks, route length estimate, APIs verified and remaining runtime risks.
