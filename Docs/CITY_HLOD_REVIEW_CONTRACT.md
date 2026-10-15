# HLOD build review

Read-only analysis; no source edits, no Unreal launch, no process control, no Git or subagents.
Write only Saved/QA/CityHLODReview.md, under 120 lines, with concrete recommendations/evidence.
Root owns the running HLOD PID7500 and exec session42362, started 2026-10-08 10:33 local.
At 10:56 still cluster6/288, CPU advancing, private memory8GB, resident about0.7GB.
Current 1472 shell buildings, 238666 detailed facade instances, 281266 total instances.
Source scripts: Tools/Editor/CreateCityHLOD.py, ImportCityAssets.py, CityExpansionBuildings.py,
CityScene.py. Logs: Saved/Logs/CityHLOD.log and CityHLODConsole.log.
Engine source: C:/Program Files/Epic Games/UE_5.8/Engine/Source.

Find the likely expensive build stage from observed logs plus UE implementation, separating
evidence from inference. Check whether source LOD selection uses full facade geometry and
whether supported proxy/LOD settings could reduce build cost while preserving the skyline.
Review impacts on World Partition runtime streaming, material/night-window appearance,
and whether an incremental restart would preserve completed clusters if eventually necessary.
Do not recommend stopping the process solely because it is slow.
Choose the smallest supported change if any, cite exact file paths/settings/code lines.
Use local primary source; no need to browse internet for this engine version.
Self-check recommendations against actual supported engine structs and project values.
Report once <=15 lines with diagnosis, evidence, action if justified, and remaining uncertainty.
