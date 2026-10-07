# Package preflight contract

## Goal and boundaries

Read-only preflight of the Win64 Development package for the continuous city.
Root owns all code, assets, running editor jobs and packaging commands.
The reviewer may only write Docs/CITY_PACKAGE_PREFLIGHT.md, below 200 lines.
Do not spawn agents, start Unreal, compile, cook, edit config or change code.

## Shared interfaces and formats

- Workspace: D:/GAME/ANANTA, Unreal Engine 5.8.3, Windows, native C++.
- Map package: /Game/ANANTA/Maps/ANANTA_City.
- Existing startup map stays ANANTA_Slice until runtime acceptance passes.
- Build entry: Tools/Build/Package-City.ps1, Win64 Development BuildCookRun.
- New code is under Source/ANANTA/Public/City, Private/City and both QA folders.
- QA flags: CityInputSmoke, CityMissionCheck, CityMissionReload, CityCapture, CityQASlot.
- Each QA mode exits 0 on success, 1 on failure and is disabled for Shipping.
- Runtime QA saves only ANANTA_City_QA and ANANTA_City_QA_Backup.
- HLOD commandlet is running; do not touch Content, Saved or Intermediate.
- A prior editor build passed; packaged target has not been built yet.

## Review and completion

Inspect project, module and target rules, QA editor guards, config and packaging script.
Identify concrete cook/build/startup/save-directory risks with exact file and line evidence.
Do not repeat the completed gameplay review or request changes for hypothetical issues.
Use rg and read-only PowerShell queries. Self-check report paths against existing files.
Report once, at most 15 lines: report file, checks used, actionable open issues.
