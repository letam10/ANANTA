# Current-city HLOD completion gate

The full build now uses a unique `Saved/Logs/CityHLOD-<runId>.log` and writes
`Saved/QA/CityHLODBuildReceipt.json`. It forces rebuilding with `-RebuildHLODs`.
Before launching Unreal it replaces the old receipt with `status=BUILDING`; only a zero
exit code, complete unique actor sequence and unchanged source evidence produce `PASS`.
The receipt records map/stage/width, source groups/instances, SHA-256 of apply/readback
evidence, start/completion UTC, build-log SHA-256 and the complete sorted built-label set.
The existing standalone log validator remains a completion check, not map acceptance.

The required source is `/Game/ANANTA/Maps/ANANTA_City`, stage `expanded`, width
`6788.2250993908565` m, 85,386 groups and 1,660,761 instances. Both layout and written
counts must match; `CityMobilityMapReadback.json` must be PASS, agree with those counts
and have been written after the apply report. Evidence must predate the build start.
Changed report contents or report modification times after the build invalidate acceptance.

`VerifyCityHLODInstances.py` requires the full receipt and freshly hashed build log,
including its run-specific path and build interval. It compares every built label with
the saved HLOD descriptors and loaded actors, rejects duplicate labels/GUIDs and requires
descriptor/actor GUID parity. Existing Instancing/Nanite/filtering, mesh, positive instance
count and material gates remain in place. Total HLOD instances are deliberately not
compared with total city instances: excluded colliders, interiors and other actors differ.

The instance JSON preserves existing fields and adds `status`, `scope`, `sourceIdentity`,
`buildRunId`, `buildLogSha256`, `builtActorCount`, `boundarySourceExclusion`,
`fullMapAccepted` and `renderedArtAccepted`. Preflight failure replaces old readback
evidence with FAIL; a completed geometry readback retains its detailed errors.

`-SingleHLOD` writes a separate sample receipt/log and never creates a full receipt.
`ANANTA_HLOD_LABEL` produces only `CityHLODInstancesSample.json`, status SAMPLE when
successful and `fullMapAccepted=false`; it still requires a current full-build receipt.
A sample run alone is therefore insufficient for this readback gate.

## Hidden boundary source verification

The verifier locates the current four edge-cell Cube actors, then identifies their actual
hidden Cube instances using the persisted edge position and 400-unit Z scale. It requires
all four source actors and `enable_auto_lod_generation=false`, recording real paths/GUIDs.
For each selected HLOD it reads the C++ `CityEditorTools.HLODSourceActorReferences` result
and compares each mapping's `path` and normalized `guid` with those sources. A match fails exclusion regardless of proxy
label or mesh appearance. Missing metadata produces UNVERIFIED and fails acceptance.

Installed UE source confirms `AWorldPartitionHLOD::SourceActors`,
`UWorldPartitionHLODSourceActorsFromCell::Actors` and the mapping's `Path` and
`ActorInstanceGuid` are reflected UPROPERTY fields. However `GetSourceActors()` and
`GetActors()` are C++ methods without UFUNCTION exposure. Python `get_editor_property`
access to these private fields is no longer required: the C++ helper uses the two public getters.
The helper must still build and pass a real Unreal metadata readback before runtime acceptance.
Missing/empty metadata or malformed GUIDs produce UNVERIFIED and block acceptance.

## Verification and remaining acceptance

Static Python compilation, PowerShell AST parsing and temporary fixtures cover valid
receipt/actor parity and rejection of stale identity, modified logs, incomplete/duplicate
actor sets and partial logs. Mocked metadata checks cover excluded sources, included
boundary sources and unavailable reflection. No editor/build commandlet was invoked.

Root integration then built the native getter bridge successfully in 60.38 seconds.
Eight additional boundary-source fixtures passed, including invalid/zero GUID rejection.
The real editor check pinned one existing proxy and read 31 source mappings, exit 0.
This accepts the metadata API binding only; full 6.8 km coverage still needs rebuild/readback.

Full rebuild subsequently passed with 3,557 proxies, run 9a4ba05837584d998162a3092dd72dba.
The receipt initially failed because PowerShell culture ordering differs from Python ordinal ordering.
Sorting both actor lists ordinally preserves exact membership and duplicate rejection; six regressions passed.
Live receipt validation and full readback passed: 3,557 descriptor/actor GUID pairs and 1,619,348 instances.
All 83,212 source mappings were checked; four hidden edge colliders were excluded with no limitations.
Reports remain structural only: renderedArtAccepted and fpsAccepted are false.

After the active editor work finishes, run `Tools/Build/Build-CityHLOD.ps1`, then run
`Tools/Editor/VerifyCityHLODInstances.py` through `Tools/Build/Run-CityEditor.ps1`.
This is structural acceptance tied to applied/readback evidence, not a hash of every
external actor package. Direct asset edits require regenerating the map readback and
rebuilding HLOD. Runtime boundary sweeps, rendered visual review and FPS remain separate.
