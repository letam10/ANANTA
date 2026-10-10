# Contract: bind HLOD validation to the current city

Repository D:\GAME\ANANTA, Unreal 5.8.3 Python editor scripts, PowerShell runners.
Read Docs/CITY_6800_HLOD_READINESS.md and existing scripts as the shared API baseline.
Current map: /Game/ANANTA/Maps/ANANTA_City; expanded; width 6788.2250993908565 metres.
Saved/QA/CityExpansionApplied.json supplies writtenGroups=85386 and writtenInstances=1660761.
Saved/QA/CityMobilityMapReadback.json has status PASS and matching groups/instances.
Root owns boundaries, CityScene and C++ editor helpers. No edits to those files.

## Owned files and done criteria

- Tools/Editor/VerifyCityHLODInstances.py
- Tools/Editor/CityHLODIdentity.py (new helper if needed)
- Tools/Build/Build-CityHLOD.ps1
- Tools/Build/Test-CityHLODLog.ps1
- Docs/CITY_6800_HLOD_IDENTITY_GATE.md

Make the full build produce a fresh completion receipt tied to the applied map dimensions/counts,
new build log hash and its complete built actor set. Partial SingleHLOD must stay a sample.
The instance readback must require matching current apply/readback/full build receipt, fresh log hash,
descriptor parity and built actor set; include source identity in the JSON report.
Reject stale or incomplete evidence; reject hidden boundary source actors in HLOD using real source
actor metadata where Unreal exposes it. If exact exclusion cannot be verified statically/API reliably,
report the limitation explicitly rather than invent acceptance.
Keep existing geometry/material/instance checks. Do not infer geometry totals from city total:
some non-HLOD actors/interiors and hidden colliders are legitimately excluded.
Use current report fields and add fields without breaking existing consumers.
Static Python compile and PowerShell AST plus targeted temporary fixture checks are allowed.
No Unreal, compile Editor, asset mutation, packaging, gameplay, Git commit/push or agents.
Files under about 300 lines and one statement per line; no unrelated refactors.
Report once at most 15 lines with changes, checks and open issues.
