# Complete city mission input check

Run these commands sequentially in **separate Development game processes** after the integrated C++ build.
Wait for the first process to exit successfully before starting the second. No editor commandlet may be active.

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' `
    'D:\GAME\ANANTA\ANANTA.uproject' /Game/ANANTA/Maps/ANANTA_City `
    -game -CityMissionCheck -CityQASlot -windowed -ResX=1920 -ResY=1080 -log

& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' `
    'D:\GAME\ANANTA\ANANTA.uproject' /Game/ANANTA/Maps/ANANTA_City `
    -game -CityMissionReload -CityQASlot -windowed -ResX=1920 -ResY=1080 -log
```

For a packaged Development executable, substitute that executable and omit the `.uproject` and `-game` arguments.
Each mode requests process exit 0 only on success, otherwise 1. The harness is disabled in Shipping.
Never combine either mode with CityInputSmoke, CityCapture, or the other mission mode.

`CityMissionCheck` creates fresh progress in memory. Both flags force save isolation before any runtime save,
even if the required explicit `CityQASlot` argument is accidentally omitted. The only save slots accessed are
`ANANTA_City_QA` and `ANANTA_City_QA_Backup`; existing normal saves are never loaded, migrated, or overwritten.
The earlier completion checkpoint is invalidated when a new mission check starts.

The sequence waits for safe player and car restoration, walks to the giver, presses E, then traverses the
boulevard sidewalk to Clue_01, Clue_02, and Clue_03. Each clue is accepted only through the controller's
ordinary target finding and E binding. Walking uses W and LeftShift with controller facing changes.
The encounter uses observed active enemies, S to maintain melee spacing, and ordinary left mouse attacks;
no damage or mission API is called.
The player then collects Fragment_Anomaly, walks back, reports to the giver, repeats E, and presses F5.
Repeat E is sent beside the reachable giver even though a completed giver is no longer an available target.

Checks require Completed, all three exact clue IDs, all three exact enemy IDs, the collected fragment, reward
exactly one, and matching primary/backup saves with player/car transforms. Save attempt/success counters must
increase after F5. Both final observed and saved transforms and all IDs are included in the report.
The checkpoint contains the producing process ID and saved transforms; reload rejects the same process ID.
Reload waits for safe restoration before comparing state and transforms, repeats E beside the giver, then F5.
Position tolerance is 10 cm, rotation tolerance 0.5 degrees, and scale tolerance 0.001.

Evidence: `Saved/QA/CityMissionCheck/MissionReport.txt`, `ReloadReport.txt`, and `Checkpoint.txt`.
Reports record phase transitions with wall elapsed time, locations, full transforms, health, IDs and save counts.
The checkpoint is produced only after successful completion, repeat input and verified F5 save.
Fresh runs preserve the old QA save files until ordinary gameplay overwrites them; reload without a valid
successful checkpoint fails instead of accepting an unrelated QA save.

Each process is limited to 900 wall seconds. Readiness: 60 seconds; each route: 180 seconds, return: 240;
combat: 90; interaction/repeat/save: 15. Blocked walking fails after 12 seconds without 80 cm displacement.
Recovery, unexpected jumps, falls, lost actors, incorrect IDs/state, invalid save or evidence IO fail the run.
Held keys are released on every phase change, failure, completion and subsystem teardown.

This harness proves only the observed engine input path when both runs actually pass. It does not certify
desktop keyboard delivery, vehicle operation, visual quality, FPS, or benchmark performance.
Vehicle input remains covered by the separate focused CityInputSmoke sequence.

Static checks: `python Tools/QA/RuntimeSourceAudit.py`, file sizes below 300 lines, local header API inspection,
and forbidden direct mutation scan. Integrated UHT/C++ build and the two runtime commands remain required.
