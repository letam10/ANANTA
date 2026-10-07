# Full city functional acceptance harness

Read CITY_IMPLEMENTATION_CONTRACT.md and CITY_RUNTIME_REPAIR_CONTRACT.md first.
The native game is implemented. Root owns rendering, map, World Partition, HLOD and packaging.
Create a bounded development only engine input functional test for the existing full mission.

## Exclusive ownership

- May create Public/QA/CityMissionCheck*.h and Private/QA/CityMissionCheck*.cpp only.
- May create Tools/QA/CityMissionCheckNotes.md.
- May extend City subsystem QA flag selection only to recognize CityMissionCheck and CityMissionReload.
- Do not edit CityCaptureSubsystem, CityInputSmoke files, other runtime systems, editor tools or assets.
- No subagents, editor/game launch, build, cook, Git commit or normal save IO.
- Root integrates and compiles once all C++ work is finished; do not compete with active commandlets.

## Existing interfaces and positions

Use the actual headers in Source/ANANTA/Public/City and established CityInputSmoke input helpers as references.
Controller InputKey handles ordinary W A S D Shift Space E F F5 and left mouse button.
Controller can set facing for deterministic steering; inputs must use existing game bindings.
Controller GetDrivenVehicle and CanCaptureProgress are available.
GetMissionStage and GetProgress on CitySubsystem expose persisted state; do not mutate that state.
Giver at (-25000,2400), car starts (-22000,500), ground Z around 0, sidewalks 15 cm.
Clues (-12000,1800), (1000,1800), (24500,2400). Enemies around (26000,4500).
Fragment (26000,4500), report to original giver for one reward.
Road centre lines every 12000 cm from -60000 to +60000, main east west boulevard Y=0.
Road half width 900 cm, sidewalk outer edge 1350 cm. Full city has connected collision.
Cafe door now (-25350,2400); apartment door (1350,2500). Initial player (-25000,1500,120), yaw90.
No time acceleration, teleport, direct actor transforms, mission mutations, damage calls or god mode.

## Commands and evidence

- -CityMissionCheck -CityQASlot starts new QA progress and runs one complete mission, not benchmark laps.
- Travel to clues on foot or using the existing car with real bindings; never skip traversal with teleport.
- Interact E through normal target finding, fight active enemies with existing attack input.
- Verify three clue IDs, three defeated enemy IDs, collected fragment, Completed and RewardCount exactly one.
- Press E on giver again and check reward stays one. F5 save and report exact final transforms and IDs.
- -CityMissionReload -CityQASlot loads that same QA state in a NEW process, waits for safe player restore,
  then checks Completed, RewardCount one, defeated/collected IDs and restored transforms.
- Reinteract once after reload if reachable, save again and verify reward remains one.
- All writes remain confined to ANANTA_City_QA and its backup; no user save reading or migration.
- Log phase changes with elapsed time and observed locations under Saved/QA/CityMissionCheck.
- Return exit code zero only for actual success. Release every held key on failure and subsystem teardown.
- Explicit bounded phase timeouts and one whole run timeout of at most 15 minutes.
- Do not report this as desktop keyboard acceptance or performance evidence.

## Done and self check

Keep each file under about 300 lines with narrow responsibilities and short Vietnamese comments where needed.
Inspect compile facing API signatures against local headers and existing working smoke implementation.
Run python Tools/QA/RuntimeSourceAudit.py and check file line counts and forbidden direct mutation calls.
Report once at most 15 lines: files, static checks, exact run commands and remaining compile/runtime gate.
Root will handle that gate after the map conversion work completes. No back and forth status messages.
