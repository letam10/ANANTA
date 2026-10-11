# Runtime integration repairs

Read CITY_IMPLEMENTATION_CONTRACT.md first. Root owns map, editor scripts and lighting.
The gameplay agent owns the repairs below and a focused input smoke test only.

## Confirmed integration defects

- Character and vehicle cameras use SetupAttachment(CameraArm) without the spring arm socket.
  Actual View_00 GPU capture is inside the player mesh. Use the proper socket attachment.
- City map now uses roads every 12000 cm from -60000 to +60000.
  Crowd currently computes 24000 cm spacing. Update the route math and sidewalk segment bounds.
- Player start is now (-25000, 1500, 120), yaw 90. Preserve these coordinates for recovery fallback.

## Exclusive file ownership

May edit Source/ANANTA/Private/City and Source/ANANTA/Public/City for these repairs only.
May create Source/ANANTA/Private/QA/CityInputSmoke* and Public/QA/CityInputSmoke*.
May create Tools/QA/CityInputSmokeNotes.md.
Do not edit existing QA/CityCaptureSubsystem files; root owns those.
Do not edit Content, Config, Assets, Tools/Editor or build scripts.

## Input smoke contract

A development only subsystem selected by -CityInputSmoke, never active in normal or Shipping play.
Drive keys through PlayerController InputKey and normal input bindings, not direct mission mutation.
Wait until CanCaptureProgress is true. No teleport, no actor transform edits, no god mode.
One short functional sequence on the city map: walk toward giver, press E, verify Investigating,
then walk clear of the cafe toward the car, enter, drive a short safe distance, brake, exit and F5 save.
Use steering toward concrete waypoints and ordinary held WASD keys, bounded timeouts, release keys on exit.
Inputs may set controller facing for deterministic navigation; report that this is engine injected input.
Reject missing actors, failed interaction, no displacement, bad camera separation, unsafe exit, save failure.
Write evidence under Saved/QA/CityInputSmoke with phase results and observed transforms.
Use -CityQASlot command line switch to isolate save IO into ANANTA_City_QA and ignore legacy migration there.
Never delete or overwrite normal user saves. Root will run the smoke on the improved map.
Input smoke is not full mission or desktop keyboard acceptance; report boundaries honestly.

## Self check and completion

Compile once with Tools/Build/Build-ANANTA.ps1 -MaxParallelActions 2 and run RuntimeSourceAudit.py.
Do not launch editor or game. Root may run editor scripts concurrently; compile only after source complete.
Check smoke file count and line limits, bounded timeout and key cleanup. No benchmarks or loops of laps.
Report once, at most 15 lines: changed files, compile outcome, command to run, unresolved issues.
No subagents, no status polling, no Git commit or broad refactoring.
