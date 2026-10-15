# Packaged functional runner contract

Workspace: D:/GAME/ANANTA, Unreal 5.8, Windows PowerShell.
Goal: create a small runner for the cooked Development executable after packaging.

## Ownership

- Agent may create only Tools/Build/Run-CityPackagedQA.ps1.
- Root owns runtime capture fixes, config, packaging, HLOD and GPU execution.
- Existing package preflight is complete; do not repeat that audit.

## Interface and fixed values

- Param ExecutablePath defaults to Saved/Builds/City/Windows/ANANTA/Binaries/Win64/ANANTA.exe.
- Param Mode ValidateSet: Capture, InputSmoke, MissionCheck, MissionReload.
- Optional switch BlueHour only allowed with Capture.
- Launch without a map argument to test the configured default map.
- Use -RenderOffscreen -windowed -ForceRes -ResX=1920 -ResY=1080.
- Use -City<Mode> -CityQASlot -NoSplash -nosound -unattended.
- BlueHour adds -CityBlueHour.
- Absolute logs belong to workspace Saved/Logs/CityPackaged<Mode><lightingSuffix>.log.
- Redirect console to a separate sibling Console.log.
- Working directory must be the executable directory, restored in finally.
- Refuse missing executable, nonzero exit, missing completion marker or incorrect loaded default map.
- Expected map log contains /Game/ANANTA/Maps/ANANTA_City.
- Read the QA subsystem log markers directly from Source/ANANTA/Private/QA.
- Print one concise success line with mode, executable and log path.
- No benchmark, native UI, save deletion, source edits, engine execution or package build by agent.

## Self check

- PowerShell parser reports no errors.
- Invoke with a deliberately nonexistent executable; expect a clear error before any process launch.
- Keep file below 150 lines and lines near 120 columns.
- Report once, max 15 lines: file, checks, open issues. Never spawn agents.
