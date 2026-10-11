# ANANTA City execution handoff inventory

Date: 2026-10-11
Repository: `D:\GAME\ANANTA`
Project: `ANANTA.uproject` (Unreal Engine project)
Contract: `Docs/CITY_HANDOFF_REVIEW_CONTRACT.md`

## Scope and safety boundary

This is a read-only inventory of the current checkout and existing evidence. No Unreal Editor,
packaged game, runtime, port probe, benchmark, soak test, or long gameplay run was started for this
handoff. The existing dirty map and external actors remain untouched. Do not stage the actor tree
blindly; review generated actor deltas separately from source and documentation.

The contract requires every entry to state path, role, current state, evidence, safe next action, and
publishability. “Publishable” here means safe to include in a source/documentation checkpoint after
review; it does not mean runtime, visual, collision, HLOD, GPU, or FPS acceptance.

## Repository state at inventory time

Evidence: `git status --porcelain=v1 -uall`, `git log --oneline -20`, and read-only file counts.

- 115,262 status lines were reported.
- 115,254 status lines are external actor `.uasset` paths under
  `Content/__ExternalActors__/ANANTA/Maps/ANANTA_City`.
- 88,600 additions, 96,966 modifications, and 72,703 deletions were reported by the status parser;
  most are generated actor churn and must not be interpreted as source edits.
- `Content/ANANTA/Maps/ANANTA_City.umap` is modified.
- Non-actor working-tree edits: `Tools/Editor/CityExpansionVenues.py`,
  `Tools/Editor/CityInteriorArchitecture.py`, `Tools/Editor/CityVenueDressing.py`, and
  `Tools/QA/VerifyCityVenueDressing.py`.
- Untracked documentation contracts: `Docs/CITY_AIRPORT_ANCHOR_REPAIR_CONTRACT.md`,
  `Docs/CITY_FACTORY_SOURCE_AUDIT_CONTRACT.md`, and
  `Docs/CITY_HANDOFF_REVIEW_CONTRACT.md`.
- The current head is `9b071830d` (`city: add diverse venues and pocket dressing`, 2026-10-11).
  The preceding relevant head is `656277dc6` (`qa: add model view and instance reuse gates`).

## Audit inventory

| Path | Role | Current state | Evidence source | Safe next action | Publishable now |
|---|---|---|---|---|---|
| `ANANTA.uproject` | Unreal project descriptor | Tracked project entry; no edit in this round | `git ls-files` | Open only in a separately approved Unreal review | Yes, as source |
| `Content/ANANTA/Maps/ANANTA_City.umap` | Persisted city map | Modified and dirty | `git status --short` | Preserve; inspect map persistence before any staging | No |
| `Content/__ExternalActors__/ANANTA/Maps/ANANTA_City/**` | World Partition external actors | 115,254 status lines; large add/delete/modify churn | `git status --porcelain=v1 -uall` | Keep isolated; compare intended map apply and actor ownership | No |
| `Source/ANANTA/Private/QA/**` | C++ QA implementation | 53 files on disk | `Get-ChildItem Source/ANANTA/Private/QA` | Build only in an authorized engineering pass | Yes, source only |
| `Source/ANANTA/Public/QA/**` | C++ QA interfaces | 18 files on disk | `Get-ChildItem Source/ANANTA/Public/QA` | Review API contracts alongside private QA code | Yes, source only |
| `Plugins/UE_MCP_Bridge/Source/**` | Editor bridge and tests | Tracked plugin source; runtime bridge not exercised | `git ls-files` | Use only in an approved native/editor session | Yes, source only |
| `Assets/City/**` | Art/source manifests and generators | 498 files, 269,773,090 bytes | recursive file count | Keep manifests and provenance with source checkpoint | Yes, source only |
| `Tools/CityAssets/**` | Asset generation/audit scripts | 73 files, 382,937 bytes | recursive file count | Run bounded offline checks only when requested | Yes, source only |
| `Tools/Editor/**` | Map/editor apply scripts | 189 files, 955,472 bytes; 3 files modified | status plus recursive count | Review diffs; apply only in a controlled Unreal window | Modified files: no |
| `Tools/QA/**` | Offline/native QA helpers | 57 files, 349,916 bytes; one modified | status plus recursive count | Keep deterministic scripts; native capture remains separate | Modified file: no |
| `Tools/Build/**` | Build/package/test wrappers | 26 files, 96,539 bytes | recursive file count | Do not invoke runtime wrappers in this handoff | Yes, source only |
| `Config/**` | Unreal project configuration | Tracked configuration | `git ls-files` | Inspect active values before a future GPU trial | Yes, source only |
| `Docs/CITY_EXECUTION_STATUS.md` | Existing progress ledger | Updated 2026-10-11; records unresolved gates | file read | Link this inventory in the next status update | Existing doc; no new publish |
| `Saved/QA/**` | Generated evidence and reports | 1,210 files: 194 JSON, 195 log/text, 744 images; 152 report-like names | recursive file count | Treat as evidence, not source; preserve provenance | No |
| `Saved/Builds/City6800/**` | Packaged build evidence | Referenced by prior status; not rerun here | existing status and docs | Use only for a separately authorized Player check | No |

## Source and generated artifact separation

### Source files and documentation

The source inventory contains 498 `Assets/City` files, 73 `Tools/CityAssets` files, 189
`Tools/Editor` files, 57 `Tools/QA` files, 26 `Tools/Build` files, 53 private QA C++ files,
18 public QA headers, and 79 documentation files. Source manifests and provenance files include
`Assets/City/*manifest.json`, `Assets/City/*/Sources/Provenance.json`, and
`Assets/City/source_catalog.json`. These are inspectable and publishable only as source/documentation;
they do not prove that the current map contains the latest source.

### Generated Unreal artifacts

The generated set is the modified map plus the 115,254 external actor `.uasset` status lines.
The map build receipt says 10,754 buildings, 85,387 groups, and 1,660,776 instances, while the
6.8 km mobility readback says 85,386 groups and 1,660,761 instances. These are generated-map
aggregates and differ from the source audit because the source round has not been applied to the
persisted map. Do not merge these counts or call them equivalent.

`Saved/QA/CityMapBuild.json` records `hlodRebuildRequired=true`, `runtimeVerified=false`, and
`physicalBoundaryCheckRequired=true`. It also records 86,073 removed generated actors and four
preserved anchors. `Saved/QA/CityInstanceReuse.json` is `PARTIAL`: it has aggregate counts but no
per-group mesh/material signatures, so reuse ratio and duplicate-group conclusions are unavailable.

## Existing evidence and open gates

| Evidence path | What it proves | Limits recorded for the next chat |
|---|---|---|
| `Saved/QA/City6800SourceAudit.json` | PASS source audit: width 6,788.225 m, 10,750 buildings, 1,668,218 instances, 4 hidden boundaries, 3 ocean surfaces, 9 access lanes, no pending meshes | `inEngineVerified=false`, `visualAccepted=false`, `gameplayFacilities=false` |
| `Saved/QA/CityExpansionSourceAudit.json` | 87,998 groups, 1,668,218 instances, 7 facade styles, 10 venues, no source errors or pending meshes | Source-only; `inEngineVerified=false`; map persistence still open |
| `Saved/QA/CityMapBuild.json` | Prior generated map apply summary: 10,754 buildings, 85,387 groups, 1,660,776 instances, 89,738 actors | Runtime unverified; HLOD rebuild and physical-boundary checks required |
| `Saved/QA/CityMobilityMapReadback.json` | 6.8 km readback: 85,386 groups, 1,660,761 instances, 12 services, 4 boundary edges | `runtimeCollisionAccepted=false`, `renderedArtAccepted=false` |
| `Saved/QA/CityInstanceReuse.json` | Honest aggregate reuse audit status | `PARTIAL`; no per-group signatures, reuse ratio, or duplicate-group result |
| `Saved/QA/CityModelReviewViews.json` | Deterministic offline plan for 93 models, 744 eight-direction views, 465 placement views | Camera plan only; no Unreal render or visual acceptance |
| `Saved/QA/CityHLODBuildReceipt.json` | Existing HLOD receipt and proxy inventory | Must be rechecked against the current dirty map after source apply; no visual/FPS proof |
| `Saved/QA/CityModelReviewViews.json` | Eight model directions and five placement directions are encoded | Requires targeted native captures before accepting geometry/placement |
| `Docs/CITY_EXECUTION_STATUS.md` | Prior progress, performance, collision, HLOD, native diagnostics, and next steps | It explicitly leaves GPU, Player, map persistence, visual quality, and 90 FPS open |
| `Docs/CITY_MODEL_REVIEW_ROUND.md` | Confirms source checks passed and lists four still-open actions | It forbids inferring visual acceptance from manifests or self-tests |
| `Docs/CITY_6800_INTEGRATION_ROUND.md` | Records prior 6.8 km readback, boundary, physics, HLOD, and native diagnostics | Existing evidence is not a substitute for the next controlled native review |

## Unfinished work carried into the next chat

1. The 2026-10-11 venue/pocket-dressing source round is not in the persisted map. Applying it can
   remove and rewrite tens of thousands of generated actors; use a controlled apply, log the marker,
   then read back the map before touching HLOD or staging.
2. The dirty map and external actor tree need an explicit persistence/source-control review. Keep
   the current actor changes separate until intended ownership and map save state are verified.
3. Re-export a per-group layout receipt containing mesh, material, collision, hidden state, and
   World Partition cell signatures. Only then can `CityInstanceReuse.json` leave `PARTIAL` and report
   a reuse ratio or accidental duplicate groups.
4. Run targeted Unreal captures for factory loading frontage, airport terminal, traffic signals,
   rail station, beach props, and vessels. Review all eight model directions and the five placement
   checks required by the contract. The offline camera manifests do not count as captures.
5. Factory detail and airport close views remain open in the existing status ledger. Vessel views
   still have known column/roof occlusion in older captures; recheck after source/map persistence.
6. Rebuild and read back HLOD only after source geometry and map persistence are accepted. Preserve
   the four hidden boundary colliders and the HLOD/source identity gate.
7. Continue the D3D12/Nanite/VSM GPU investigation on the same packaged City6800 build. Prior Base
   and reload trials failed with PageFault/DXGI errors; a shadow-async diagnostic completed at about
   71.58 FPS but is not a product preset or 90 FPS acceptance.
8. Perform a short, explicitly authorized Player check for map edge behavior, settings, save/reload,
   and facilities. This handoff did not run it, and fixture or editor checks cannot replace it.
9. After all requested review evidence is complete, update `Docs/CITY_EXECUTION_STATUS.md`, run the
   required bounded checks, and commit/push only reviewed source/documentation. Do not stage the bulk
   actor tree blindly.

## Safe next actions

- Read the current diffs for the four non-actor modified Python files and the three untracked
  contracts; do not change them as part of this inventory.
- Validate source generators with bounded offline syntax/audit checks only. Preserve generated JSON
  reports under `Saved/QA` and record their exact paths.
- Plan a single controlled map-apply window with a pre-apply status snapshot, a post-apply readback,
  and a clear rollback/snapshot procedure. Keep the map and external actors out of a source-only
  checkpoint until accepted.
- Use the existing model-view JSON as input to native capture planning. Native capture, Player,
  collision, HLOD, GPU, and FPS results must be recorded separately.
- Keep repeated static props instance-friendly and non-interactive interiors sparse. Preserve the
  contract limitation that Nanite/HLOD/LOD and collision are separate gates.

## Verification performed for this handoff

- Read `Docs/CITY_HANDOFF_REVIEW_CONTRACT.md` before editing.
- Read-only Git status, recent history, tracked-file inventory, recursive source counts, and QA
  artifact counts were collected.
- Read-only JSON inspection confirmed source and generated count discrepancies and explicit false or
  partial acceptance flags.
- No Unreal Editor, packaged game, game runtime, port probe, benchmark, soak test, or long gameplay
  test was run.

The only file created by this handoff is `Docs/CITY_EXECUTION_HANDOFF.md`. Do not stage or commit it
from this subtask; the parent chat should review the diff and decide whether to include it in the next
source/documentation checkpoint.
