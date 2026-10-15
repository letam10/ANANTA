# Focused city input smoke

Run a Development executable or Unreal Editor in standalone game mode:

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' `
    'D:\GAME\ANANTA\ANANTA.uproject' /Game/ANANTA/Maps/ANANTA_City `
    -game -CityInputSmoke -CityQASlot -windowed -ResX=1920 -ResY=1080 -log
```

The harness exits with status 0 on success and 1 on failure. Evidence is written incrementally to
`Saved/QA/CityInputSmoke/Report.txt`, with phase results, transforms, camera separation and speed.
Do not combine it with `-CityCapture`, which changes the active view target.

This is engine injected input through `PlayerController.InputKey`. It holds ordinary WASD keys and
presses E, Space and F5 through the native bindings. Controller facing is set for deterministic walking
and driving guidance. It never sets an actor transform, teleports, changes mission state directly,
disables collision, grants invulnerability or calls the interaction/save gameplay methods directly.

Sequence: wait for safe player restore; check camera; walk to giver; E; verify Investigating; walk
into and back out of the cafe, then along street waypoints; approach PlayerCar; E; check car camera; drive approximately
18 metres; brake; E exit; check capsule clearance and ground; F5; reload the QA file for verification.
Each phase has a timeout and the complete run is bounded to 120 seconds. Held keys are released on
every phase change, completion, failure and subsystem deinitialization.

`-CityInputSmoke` starts a new QA state in memory on each run; it does not load earlier progress.
All save IO is confined to `ANANTA_City_QA` and `ANANTA_City_QA_Backup`. There is no normal-slot read,
write, deletion or legacy migration. The explicit `-CityQASlot` flag is required by the harness;
the smoke switch also forces QA isolation before the first save even if that flag is accidentally omitted.
Use `-CityQASlot` without the smoke flag to load the saved QA journey in a separate Development run.
Both switches are ignored for save-slot selection in Shipping, and the smoke subsystem is never created there.

A passing smoke is evidence for this short injected-input path only. It does not complete the three-clue,
three-enemy mission, prove desktop keyboard/mouse delivery, validate rendered visual quality, or measure FPS.
