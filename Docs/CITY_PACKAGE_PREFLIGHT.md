# Win64 City package preflight

Scope: source/config review only. The Win64 Development package has not yet been
built or launched; HLOD work remains in progress.

## Findings

1. **Packaged startup map does not match the requested city package.**
   `Tools/Build/Package-City.ps1:21` passes `/Game/ANANTA/Maps/ANANTA_City`
   to BuildCookRun, while `Config/DefaultEngine.ini:18` still sets
   `GameDefaultMap` to `/Game/ANANTA/Maps/ANANTA_Slice.ANANTA_Slice`.
   The script does not pass a runtime map override. A packaged launch can
   therefore request the Slice map when only the City map was explicitly
   selected. Keep the existing startup map per contract until acceptance;
   launch the staged executable with an explicit City map or separately
   verify that the Slice map is also cooked.

2. **Package execution remains an unverified gate.**
   `Tools/Build/Package-City.ps1:3` defaults to
   `C:\Program Files\Epic Games\UE_5.8`; `:12` resolves RunUAT there and
   `:17-25` requests Win64 Development build, cook, stage, pak and archive.
   The script checks UAT's exit code at `:29-32`, but there is no prior
   executable/path check. Confirm the configured engine installation and
   capture the actual BuildCookRun result before treating packaging as passed.

## Reviewed configuration and guards

- Game target is `TargetType.Game` with module `ANANTA` in
  `Source/ANANTA.Target.cs:3-10`; editor target is separate at
  `Source/ANANTAEditor.Target.cs:3-10`.
- `Source/ANANTA/ANANTA.Build.cs:9-19` lists Core, Engine, UMG, AI and
  Navigation dependencies. QA editor utility code is wrapped in
  `WITH_EDITOR` at `Source/ANANTA/Private/QA/CityEditorTools.cpp:9-24`.
- Automated input and mission QA are guarded out of Shipping in
  `CityInputSmokeSubsystem.cpp:15-23` and `CityMissionCheckSubsystem.cpp:15-25`;
  capture is guarded in `CityCaptureSubsystem.cpp:21-29`.
- QA save slots are selected only outside Shipping and only for QA flags in
  `Source/ANANTA/Private/City/ANANTACitySubsystem.cpp:15-25`. Normal save/load
  uses the subsystem's regular defaults; save writes backup then primary at
  `:123-140` and restores backup before primary at `:143-154`.
- Project settings retain Slice for editor and game startup at
  `Config/DefaultEngine.ini:16-20`. This preflight leaves that setting intact.

## Check boundary

Reviewed the target/module rules, project descriptor, startup-map settings,
package script, QA Shipping/editor guards, and save-slot selection with
read-only PowerShell and `rg`. No engine launch, build, cook or asset/Saved/
Intermediate contents were opened or changed. No source, config or asset was
changed.
