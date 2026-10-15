# Contract: next 6.8 km HLOD acceptance

## Shared state and formats

- Repository: D:\GAME\ANANTA; Unreal 5.8.3, Windows PowerShell.
- Persisted map: /Game/ANANTA/Maps/ANANTA_City.
- Layout: 6788.2250993908565 metres square; 85386 HISM groups, 1660761 instances.
- Saved/QA/CityExpansionApplied.json is the applied map report, not runtime acceptance.
- Saved/QA/CityMobilityMapReadback.json has status PASS and matching groups/instances/services.
- Saved/QA/CityWholeMapCollision.json has passed=true, errors=0, roadSamples=13987.
- Saved/QA/CityWorldBoundaries.json currently passed=0, errors=14; root owns its investigation.
- Tools/Build/Build-CityHLOD.ps1 accepts SingleHLOD and EngineRoot; no other required parameters.
- Existing HLOD layer: /Game/ANANTA/City/HLOD/City_HLOD.
- New binaries remain unstaged until required acceptance gates are verified.

## Assigned output

The delegated reader may create/edit only Docs/CITY_6800_HLOD_READINESS.md.
Report exact existing commands, gate dependencies, report schemas and concrete stale-map risks.
Inspect source/config/tools and existing reports read-only. Do not start Unreal or change assets.
Check intended full HLOD generation and validation covers the expanded map, preserves instance/material
geometry, excludes hidden physical boundary colliders, and does not accept old 3.4 km reports.
Use rg and short source reads; identify a minimal required repair if there is a real gap.
Report once, at most 15 lines, with file changed, checks and remaining issues.
Do not spawn agents, compile, test Unreal, package, publish, alter saves or modify any other file.
