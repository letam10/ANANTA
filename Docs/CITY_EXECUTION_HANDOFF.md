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
- The current head is `02813bb64` (`docs: record city model handoff and quality source pass`, 2026-10-11).
  The preceding relevant heads are `9b071830d` (`city: add diverse venues and pocket dressing`)
  and `656277dc6` (`qa: add model view and instance reuse gates`).

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

## Current source-only continuation 2026-10-11

- Source changes after the previous handoff add deterministic west/core/east building profiles,
  district metadata and six pocket themes. The character model and saved gameplay anchors were not
  edited.
- Offline evidence: VerifyCityDistrictVariety PASS with 10.750 buildings, 3 districts, 7 facade
  styles and 8 forms. VerifyCityExpansionLayout PASS with width 6.788,225 m, four hidden boundary
  colliders, three ocean surfaces and nine access lanes. Python compilation PASS.
- The generator output is 89.097 groups and 1.659.861 instances. This is source evidence only.
  It does not prove that the dirty World Partition map contains the new source.
- No Unreal, packaged game, port probe, benchmark or long gameplay run was started. Do not infer
  visual quality, runtime collision, HLOD, GPU stability or 60 FPS from these gates.
- Safe next step is a controlled map apply/readback after the actor tree is reviewed. Keep the map
  and external actors out of a source-only commit until persistence and ownership are accepted.

## FacadeCivic asset checkpoint 2026-10-11

- `Tools/CityAssets/expansion_architecture.py` now owns a reusable `FacadeCivic` module with a
  recessed glazed entry, stone piers, brass canopy and civic sign panel. It is 4 x 3.2 m and uses
  existing PBR material slots so the module can be instanced with the city kit.
- Blender 5.2 headless evidence: `Saved/QA/CityExpansionAssets/build.json` PASS, FBX roundtrip
  `Saved/QA/CityExpansionAssets/fbx_roundtrip.json` PASS for 12/12 meshes, and 24 offline review
  renders at `Saved/QA/CityExpansionAssets/*_front.png` and `*_quarter.png`.
- The source QA style set now requires 8 facade styles including `FacadeCivic`. This proves source
  generation and mesh integrity only; it does not prove Unreal import, map persistence, HLOD, runtime
  collision, NPC traversal, GPU stability or 60 FPS.
- Existing facade FBX files were regenerated by Blender during the build. Before commit, restore
  unchanged legacy binaries and retain only the new FacadeCivic FBX plus the manifest/hash update;
  this keeps the source checkpoint surgical.

## Checkpoint handoff: nội thất venue 2026-10-11

### Đã làm
- `Tools/Editor/CityVenueDressing.py` đã có dressing riêng cho Library, Restaurant, Cinema và Hotel; output deterministic và nhãn `Dressing_<Room>_<Name>` duy nhất.
- `Tools/Editor/CityInteriorArchitecture.py` thêm wall detail cho bốn venue, còn `Tools/Editor/CityExpansionVenues.py` cố định vị trí TicketDesk Cafe.
- `Tools/QA/VerifyCityVenueDressing.py` kiểm tra bounds, corridor, collision, overlap với nội thất nền, schema và giới hạn số lượng.

### Bằng chứng
- 249 additions; tất cả 12 room đạt điều kiện tối thiểu; 166 additions không collision.
- VerifyCityVenueDressing PASS và VerifyCityModelViewCoverage PASS.
- Chưa mở Unreal, chưa chạy EXE, chưa probe port, chưa benchmark; visual acceptance và persistence vẫn mở.

### Việc còn lại
1. Apply source vào map trong một lượt riêng có marker/readback, không stage actor tree tự động.
2. Kiểm tra năm góc placement trong Unreal cho các venue mới và rà corridor/door clearance.
3. Chạy HLOD/instance identity, collision fixture và GPU capture có giới hạn thời gian sau khi map sạch.
4. Tiếp tục thêm facade/transport/water/landmark theo từng checkpoint nhỏ.

## Checkpoint handoff: sửa gate đồ nhỏ 2026-10-11

### Thay đổi
- `Tools/QA/VerifyCitySmallPlacement.py` giữ lại danh sách dressing/living một lần và thêm các material field thực tế vào fixture catalog trước khi gọi `Layout.add`.
- Không hard-code `ShellSage`; gate phản ánh material mà source placement thực sự dùng, nên không che giấu thiếu tài nguyên khác.

### Bằng chứng
- `small_audit.py` PASS: 8 mesh, topology/UV/normals/bounds/hash đạt, renderCount 0 ở lượt audit nhẹ.
- `VerifyCitySmallPlacement.py` PASS: 8 placement, 3 overhang regressions bị từ chối.
- `py_compile` và `git diff --check` PASS.

### Giới hạn
- Đây là source AABB/support gate. Chưa chứng minh import/reopen, simple collision trong Unreal, ánh sáng, HLOD, map persistence hoặc FPS.
- Tám prop đã được `ApplyCityExpansion.py` gọi qua `CitySmallDetails.furnish`; việc gọi đó chưa được chạy lại trong Unreal ở checkpoint này.

## Checkpoint handoff: civic dressing 2026-10-11

### Đã xác nhận
- `Tools/Editor/CityCivicDressing.py` tạo sáu cabinet thật ở ba vị trí mỗi bên Arcade, xoay vào phòng và giữ lane trung tâm.
- `Tools/Editor/CityCivicDistrict.py` gọi civic dressing sau shell và room details; source apply path đã có sẵn trong `ApplyCityExpansion.py`.
- Gate `python -X utf8 Tools/Editor/VerifyCivicDressingLayout.py` PASS với 54 instance và 43 collider.

### Giới hạn còn mở
- Chưa Apply lại World Partition map vì actor tree đang dirty rất lớn.
- Chưa có native five angle capture, readback HLOD, collision runtime, NPC route hoặc GPU/FPS evidence.
- Khi được phép chạy lượt native riêng, cần kiểm Arcade prompt approach, door clearance, cabinet simple collision và không nhân đôi actor Living.

## Checkpoint handoff: render audit 2026-10-11

### Kết luận source/config
- `Saved/QA/CityRenderConfigAudit.md` là bằng chứng đọc Config, source và log capture; nó không khẳng định CVar cuối cùng sau gameplay.
- `Config/DefaultEngine.ini` bật Lumen/VSM; `Config/DefaultScalability.ini` quality 2 có texture pool 3000 và VSM bias; log capture có nhiều lần áp profile nên không được dùng như runtime Max cuối.
- HLOD cell/loading intent nằm trong `Tools/Editor/CreateCityHLOD.py`; HLOD vẫn stale và cần rebuild sau map persistence.

### Việc còn lại
1. Controlled HLOD rebuild rồi so sánh route và proxy identity.
2. Diagnostic VSM bias với cùng độ phân giải 1920x1080, ghi frame time và ảnh gần/trung/xa.
3. Diagnostic VSM off chỉ để xác định liên quan PageFault, không tính là preset sản phẩm.
4. Chỉ sau khi map sạch mới chạy lượt gameplay ngắn có log `stat unit`, `stat gpu`, `stat levels` và xác nhận 60 FPS thực tế.

## Checkpoint handoff: sửa gate layout 6,8 km 2026-10-11

### Nguyên nhân
- Asset `FacadeCivic` đã được thêm ở checkpoint trước nhưng `VerifyCity6800Layout.py` vẫn assert đúng bảy style, khiến audit dừng với AssertionError dù source layout không có lỗi.

### Đã sửa và kiểm chứng
- Gate hiện tạo tập `styles`, yêu cầu đúng tám style và yêu cầu có `FacadeCivic`.
- `python -X utf8 Tools/QA/VerifyCity6800Layout.py` PASS với 10.750 building và không có errors/pending meshes.
- `py_compile` và `git diff --check` PASS.

### Giới hạn
- Số liệu là source layout audit; chưa chứng minh map persistence, native visuals, HLOD rebuild, runtime collision, NPC/transport hoặc FPS.

## Checkpoint handoff: FacadeTransit 2026-10-11

### File và API
- `Tools/CityAssets/expansion_architecture.py` thêm `transit()` và `Tools/CityAssets/expansion_build.py` xuất mesh mới.
- `Tools/Editor/CityExpansionBuildings.py` thêm style `FacadeTransit`; `CityExpansionLayout.py` phân phối style ở west/core/east.
- `FacadeTransit` không tạo `V_FacadeTransit_*` material variant; mesh dùng material slots PBR đã có để tránh tham chiếu import mới.

### Bằng chứng
- `Saved/QA/CityExpansionAssets/build.json`: 13 mesh, build PASS.
- `Saved/QA/CityExpansionAssets/fbx_roundtrip.json`: 13/13 hash/bounds/material/UV/manifold PASS.
- Render review: 26 ảnh, `FacadeTransit_front.png` và `FacadeTransit_quarter.png` đã xem.
- District variety, 6.8 km layout, py_compile và diff check PASS.

### Giới hạn
- FBX/Blender render không chứng minh Unreal import, map persistence, HLOD, collision, NPC traversal hoặc FPS.
- Các FBX facade cũ được khôi phục để checkpoint chỉ chứa binary mới `FacadeTransit.fbx`; manifest hash đã đồng bộ.

## Checkpoint handoff: station concourse 2026-10-11

### Đã làm
- `Tools/Editor/CityMetroDistrict.py` đặt một `FacadeTransit` và một `BusStopSign` tại sân ga tây nam, collision tắt để không chặn capsule hoặc xe.
- Layout source giữ nguyên 10 facility, 4 hidden boundary và 9 access lane; facade được lấy từ expansion manifest đã hash PASS.

### Đã kiểm chứng
- `VerifyCity6800Layout.py` PASS.
- `VerifyCityExpansionLayout.py`, py_compile và diff check PASS.
- Không mở Unreal, không apply World Partition, không chạy EXE, port hoặc benchmark.

### Còn mở
- Native capture năm góc cho station, kiểm simple collision và prompt route sau map persistence.
- HLOD rebuild/readback và gameplay boarding vẫn chưa được chứng minh.

## Checkpoint handoff: facility facade identity 2026-10-11

### Đã làm
- `Tools/Editor/CityMetroDistrict.py` thêm facade front detail cho Hotel, Restaurant, Cafe và Theater.
- Mesh đều lấy từ `expansion_manifest.json` đã hash/FBX roundtrip PASS; placement không tạo interior giả và không bật collision.

### Đã kiểm chứng
- `VerifyCity6800Layout.py` PASS và không có pending asset mesh.
- `VerifyCityExpansionLayout.py`, py_compile và diff check PASS.
- Không mở Unreal, không apply map, không chạy EXE, port hoặc benchmark.

### Còn mở
- Cần native capture năm góc để xác nhận facade không che cửa, bảng hiệu và lối vào.
- Cần HLOD/readback, collision fixture, interaction prompt và gameplay route sau map persistence.

## Checkpoint handoff: airport terminal facade 2026-10-11

### Đã làm
- `Tools/Editor/CityMetroDistrict.py` đặt facade transit tại `(207000,181900,15)` và `(220000,181900,15)`, cùng bus signs tại y 180950.
- Placement nằm trong `AIRPORT` reserve và ngoài access lane; collision tắt để giữ lối đón khách và runway logic.

### Đã kiểm chứng
- `VerifyCity6800Layout.py` PASS.
- `VerifyCityExpansionLayout.py`, py_compile và diff check PASS.
- Không mở Unreal, không Apply map, không chạy EXE, port hoặc benchmark.

### Còn mở
- Cần camera native gần terminal để kiểm tỷ lệ, lối vào và biển hiệu.
- Cần map readback/HLOD và gameplay airport access sau controlled apply.

## Checkpoint handoff: pool roof dressing 2026-10-11

### Đã làm
- `Tools/Editor/CityRoofPool.py` thêm `DetailedStreetLamp`, `DetailedPlanter` và `BusStopSign` ở roof deck.
- Các actor trang trí không collision; water surface, stair body, railings và roof bounds giữ nguyên.

### Đã kiểm chứng
- `VerifyCity6800Layout.py` PASS.
- `VerifyCityExpansionLayout.py`, py_compile và diff check PASS.
- Không mở Unreal, không Apply map, không chạy EXE, port hoặc benchmark.

### Còn mở
- Cần native five angle pool capture để kiểm tỷ lệ đồ deck và lan can.
- Cần player roof traversal, HLOD/readback và GPU/FPS evidence sau controlled map apply.
## Checkpoint handoff: chẩn đoán EXE và bản đóng gói 2026-10-11

### Kết luận đã kiểm tra

- EXE vẫn tồn tại. Bootstrap của bản City nằm ở
  `Saved/Builds/City/Windows/ANANTA.exe` (171,520 bytes, ghi ngày 07/10/2026).
- Runtime chính nằm ở
  `Saved/Builds/City/Windows/ANANTA/Binaries/Win64/ANANTA.exe`
  (337,542,656 bytes, ghi ngày 07/10/2026).
- Ngoài ra còn bản City6800 và staged copy 338,096,640 bytes ghi ngày 10/10/2026;
  đây là các package khác nhau, không được coi là bản mới nhất của source.
- `Binaries/` và `Saved/` bị Git ignore nên EXE không xuất hiện trên GitHub. Lịch sử Git
  cũng không chứa `.exe` hoặc `.pak`; người nhận checkout phải dùng artifact local hoặc
  tự package lại.
- Commit source mới nhất `f7536deeee` ngày 11/10/2026 chưa được đóng gói vào các EXE
  hiện có. Vì vậy mở EXE cũ không thể hiện các facade/pool dressing mới nhất.
- Không mở game, không probe port, không benchmark và không tạo log runtime trong lượt
  chẩn đoán này. Không có bằng chứng để kết luận crash mới từ bản hiện tại.

### Nguyên nhân dễ gây lỗi hoặc tưởng như không có game

1. Chỉ sao chép `ANANTA.exe` ra ngoài sẽ thiếu thư mục `ANANTA`, `Engine`, Content/Paks
   và DLL đi kèm; bootstrap hoặc runtime sẽ không khởi động đúng.
2. Mở `Binaries/Win64/ANANTA.exe` của source root hoặc bản City6800 cũ sẽ chạy artifact
   khác với bản được mô tả trong handoff hiện tại.
3. Tài liệu `CITY_PLAYABLE_BUILD.md` đang trỏ tới bootstrap
   `Saved/Builds/City/Windows/ANANTA.exe`; phải giữ nguyên toàn bộ cây thư mục bên cạnh
   file đó.
4. Project config vẫn đặt GameDefaultMap là Slice, trong khi script package chọn
   `ANANTA_City`; package mới cần được build và kiểm tra map khởi động trước khi gọi là
   bản thành phố 6,8 km.

### Cách khôi phục có thể kiểm chứng ở lượt được phép package

- Chạy `Tools/Build/Package-City.ps1` với Unreal Engine 5.8 và output mặc định
  `Saved/Builds/City`; script dùng BuildCookRun Win64 Development, cook City, stage,
  pak và archive.
- Sau khi script trả `CITY_PACKAGE_OK`, kiểm tra cả bootstrap và inner EXE cùng các
  file Paks/Engine. Ghi timestamp, kích thước, SHA-256 và map startup vào handoff.
- Chỉ sau package mới được thực hiện một lần chạy ngắn có giới hạn để kiểm tra startup;
  lượt này chưa thực hiện theo yêu cầu không chạy game nặng/lâu.
