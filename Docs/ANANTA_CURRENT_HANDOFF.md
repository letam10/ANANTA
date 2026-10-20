# ANANTA Current Handoff

> Active continuation 2026-10-20: R0, W1/W2 and isolated W3 contract DONE bounded.
> W3 uses a new comparison map only; City/Coastal integration and hero art pending.
> Work only on main; incremental phase commit/push authorized by current user.
> P2 bounded historical visual pass is not art acceptance; P4A/P4B PARTIAL until
> a fresh runtime log. Primary FPS target is 60; no current FPS claim.

## Current continuation receipt — 2026-10-20

- R0 pushed `2a481d89b4222cafa965821d7c3ec41180fc1f71`; W1/W2 pushed
  `4aa126b30646c2bf51329abf80ae664906a2f17e`; main remote hashes verified after
  each push. Continue only on main and stage exact phase allowlists.
- W1/W2 fresh gate: 68/68 CPU contract checks; syntax/build/spec validator pass;
  clean browser console; orbit/free/foam/boundary controls; three 10-second
  reports. Startup outlier recorded, not hidden. Browser timings are not city FPS.
- W3 new owned assets: `/Game/ANANTA/WaterW3_20261020/MF_WaveSpec`,
  `M_WaveSpec_Opaque`, `W3_Comparison`. Function has 13 nodes, actual
  BaseColor/Normal/Roughness/Emissive readback, exact source wave tuples and
  HLSL code hashes. Wave inputs are generated literals from the pinned JSON;
  normal world-space, opaque, no WPO/physics/buoyancy.
- Native collision rays hit all four separate BlockAll walls at x=+/-70000 and
  y=+/-40000 cm. These rays are not boat/camera gameplay traversal acceptance.
- Three/UE coast, beach_boat and offshore images use matching mapped transforms,
  1422x800, Three vertical FOV48 and UE horizontal FOV76.7157600295933. Wave-band
  directions are comparable; lighting/color/time differ. Native captured editor
  images are offscreen evidence and never F1 FPS proof.
- Fresh evidence: `Tools/Continuation_20261020/W3_native_readback.json`,
  `W3_review.json`, six W3 images. Earlier failed shader/callback iterations are
  diagnostic only. A skipped expression during bulk deletion caused duplicate
  TimeSeconds inputs; snapshot-list deletion plus exact 13-node assertion fixes it.
- Read-only audit reports: A1_hero_audit.md, S1_source_audit.md,
  G1_source_audit.md in the same continuation folder. Root reviewed them.
  Existing untracked A1-A6/F1/W3 work has not been adopted or staged.
- A1 warning: historical untracked shading output assigns Concrete_AO to Normal;
  fix only in an owned adaptation before any use. Native hero import, full eight
  directions after shading and five placement views from map bounds remain open.
- G1 gaps include availability bypass, no train E/ride path, no flight altitude,
  no visible rowing stroke, NPC sinusoidal motion instead of real schedule, and
  missing native Coastal persistence hooks. Direct API QA is not full interaction.
- S1: City WP/HLOD history differs from Coastal. Fresh native identity/cell,
  Data Layers/PCG and short normal-input route remain open. Do not run the old
  300-second journey or full HLOD rebuild simply to refresh a receipt.
- Foundation/spec/diff checks pass. Full LFS check found 88 pre-existing
  unexpectedGitObject entries under Assets/CoastalUpgrade; R0_gates.json stores
  them. Do not hide this red repository gate or rewrite unrelated file contents.

Next bounded implementation prompt: preserve all initial unrelated dirty/untracked
work; select a new isolated street/civic hero source package, correct semantic
texture selection/reuse, resolve provenance and source hashes, then fresh shading
8-view + native import/5-placement review. Keep each venue explicitly interactive,
enterable dressing or shell-only. Refresh native P4 runtime separately, then fix
one confirmed gameplay tranche at a time. Do not expand map or claim 60 FPS until
its hero and headed F1 gates are actually met. All historical receipts below keep
their original scope and are not fresh evidence for this continuation.

Ngày cập nhật: 2026-10-15
Phase ID: P2 — Material graph và hero slice
Trạng thái: PASS — bounded P2 material và headed hero gate đạt; GPU tier/FPS chưa kiểm

## Checkout và dirty-state

- Checkout: `D:\GAME\ANANTA`
- Engine: Unreal Engine 5.8.3
- Branch: `main`
- Baseline remote sau sync: `479da5b044669c8a18f2f11084961791284db390`; current HEAD sau commit P2: `25bee1260842c7ee5e74bedde5c22f740f010519`
- Dirty file có sẵn: `AGENTS.md`; không sửa, stage, commit hoặc xóa.
- P2 thay đổi: material helpers/readback, coastal map material assets, CoastalCity map, CoastalQA hero flags và hai Docs; chỉ `AGENTS.md` là dirty có sẵn.

## Git đối chiếu và baseline sync

Đã chạy:

```powershell
git fetch origin refs/heads/codex/coastal-interiors-20261014:refs/remotes/origin/coastal-interiors-20261014
```

Kết quả: exit 0; remote-tracking ref cập nhật từ `dcc05d8fc3` lên
`9057c9beec`.

Đã đọc lịch sử và xác nhận fast-forward an toàn; không reset mù hoặc force-push:

- Remote commit: `9057c9beecd2ef1e1cc433eb4f672b9130343e79`
- Subject: `Merge branch 'main' into codex/coastal-interiors-20261014`
- Parents: `dcc05d8fc3...` và `77c9ba76fe67834730d3989781c4bea6e51575f3`
- Trước sync local `behind 78`; sau sync local và remote cùng ở `9057c9...`.
- `git merge-base --is-ancestor HEAD origin/...` exit 0.
- `git merge-tree HEAD origin/...` không báo conflict.
- `git merge --ff-only origin/codex/coastal-interiors-20261014` exit 0.
- `AGENTS.md` không nằm trong diff; hai Docs P0 không nằm trên remote nên không xung đột.

**Quyết định P0:** fast-forward an toàn local từ `dcc05d8...` lên `9057c9...`;
local đã đồng bộ remote. Không cần reset hoặc force-push.

## Evidence hiện tại

- `& .\Tools\Build\Validate-ANANTA.ps1` — exit 0:
  `ANANTA foundation validation passed`, BridgeDescriptor=True,
  WorkflowConfig=True, MissingPlugins/Files rỗng.
- `git diff --check` — exit 0. Có warning Git rằng LF của `AGENTS.md` sẽ
  chuyển thành CRLF nếu Git chạm file; không sửa warning này.
- Manifest và file source hiện hành:
  - `Assets/CoastalUpgrade/manifest.json`: 72 models, max triangles 9678.
  - `Assets/CoastalUpgrade`: 72 FBX, 15 PNG, 1 blend và 1 blend1.
  - `Saved/Upgrade/ModelViews/coverage.json`: 72 model entries.
  - Room geometry: 36 review unit, 180 views theo handoff/evidence hiện hành.
- Map/interior tranche:
  - 23 building vào được.
  - Map commandlet r15: 6745 instances / 816 HISM; MapCheck 0 Error/Warning.
  - `Saved/Upgrade/build-coastal-interactive.log`: marker
    `COASTAL_MAP_OK 23 enterable buildings, 6745 instances / 816 HISM batches`;
    Python exit 0. Hai warning là UE-MCP Slate startup và
    `save_current_level` deprecated.
- Runtime bounded:
  - Lệnh: `UnrealEditor-Cmd.exe ANANTA.uproject -game -CoastalQA -NullRHI
    -unattended -NoSound`.
  - `Saved/Upgrade/runtime-r15-interactive.log`: profile High Lumen,
    TSR 900p/1080p, target 16.667 ms; `COASTAL_QA_COMPLETE failures=0 views=122`.
  - Các gate cửa/building, service/NPC, schedule, micro props, signal, train hai
    chiều, ocean boundary, đi bộ, xe và xuồng đều PASS.
  - Đây là bounded NullRHI logic proof, không phải headed visual, material,
    collision cảm nhận, GPU/VRAM, frame-time hoặc 60 FPS proof.

## P1 source/geometry review evidence

- Lần audit read-only đầu tiên exit 1 vì 71 source_sha256 trong coverage cũ lệch FBX;
  nguyên nhân là commit fe7b67fe... refresh model kit nhưng evidence Saved/ bị ignore và
  chưa được tạo lại.
- ReviewModels.py được sửa tối thiểu để thử BLENDER_EEVEE_NEXT, fallback BLENDER_EEVEE
  trên Blender 5.2. Chạy background tạo lại 72 model x 8 hướng, 576 PNG và coverage hash mới.
- ReviewRoomGeometry.py có cùng fallback. Chạy background exit 0 và ghi
  ROOM_GEOMETRY_VIEWS_OK 180 views vào folder Saved/Upgrade/RoomGeometry/20261015-092127.
- AuditCoastalQuality read-only exit 0: manifest_models=72, coverage_models=72,
  import_readback=72, layout_buildings=23, layout_review_units=36,
  layout_review_views=195, room_coverage_files=4, errors=0, warnings=0.
- AST parse 130 Python scripts exit 0. Evidence này chỉ xác nhận source/geometry; không claim
  headed visual, material graph, GPU/VRAM hoặc FPS.
## P2 material, lighting và headed hero evidence

- `Tools/Upgrade/coastal_materials.py` thêm fallback graph thật cho BaseColor,
  Roughness, Normal và Emissive; `coastal_detail.py` và `coastal_scene.py` áp dụng
  cùng contract trước compile/save. Ocean giữ opaque surface, normal/foam nhẹ và
  collision boundary trong scene generator.
- `& .\\Tools\\Build\\Build-ANANTA.ps1 -MaxParallelActions 2` exit 0 sau khi thêm
  `CoastalQA` hero flags; warning còn lại chỉ là compiler deprecation và VS version.
- `BuildCoastalCity.py` headless exit 0; log mới có `MapCheck: 0 Error(s), 0 Warning(s)`
  và `COASTAL_MAP_OK 23 enterable buildings, 6745 instances / 816 HISM batches`.
- `InspectCoastalMaterials.py` readback exit 0; `Saved/Upgrade/coastal-material-readback.json`
  có 19 materials, BaseColor=19/19, Roughness=19/19, Normal=19/19, Emissive=19/19,
  19 package SHA-256 không null, `errors=[]`, `packagesUnchanged=true`.
- `CoastalQA` hỗ trợ `-CoastalHeroOnly` với năm camera cố định `hero_day`,
  `hero_blue_hour`, `hero_street`, `hero_interior`, `hero_coast`; `-CoastalBlueHour`
  đổi profile directional/sky light. Capture headed 1280x720 đã chạy hai lần:
  Day folder `Saved/Upgrade/Runtime/2026.10.15-12.58.16` và BlueHour folder
  `Saved/Upgrade/Runtime/2026.10.15-13.00.11`; mỗi log có
  `COASTAL_QA_COMPLETE failures=0 views=5`, 5 PNG mới và checks gameplay PASS.
- Đã mở kiểm tra trực quan `hero_day.png` và `hero_coast.png` từ hai folder; không thấy
  gap nền trong overview/coast, biển và boundary hiện diện. Đây là bounded headed visual
  proof, không phải FPS/VRAM proof.
## Phân loại

**DONE ở baseline/P1:** fast-forward baseline; foundation validation; 72 model
source/manifest và 8-view coverage; 36 unit/180 room geometry review; 23 building;
r15 bounded NullRHI logic; roadmap/handoff P0.

**PASS ở P2 bounded gate:** material graph bốn output, map check, lighting metadata,
  năm camera hero và hai headed captures đã có evidence mới.

**UNVERIFIED:** headed visual/material, GPU/VRAM/frame-time percentile, 60 FPS,
World Partition, HLOD, Data Layers, PCG, aircraft control, rowing animation,
railway signal control, save/economy và AAA quality toàn map.

**BLOCKED:** không có blocker P2. P3 World Partition/HLOD/Data Layers/PCG và các gate
  toàn map vẫn chưa thực hiện; không mở rộng phạm vi trong chat này.

## Evidence stale cần giữ nguyên

- `Saved/Upgrade/coastal-quality-report.json` có `manifest_models=65`; đây là
  report cũ, không dùng thay cho 72 model.
- `Saved/Upgrade/city-layout.json` có 195 review views; không dùng thay cho
  room geometry proof 180 views.
- Không xóa hoặc ghi đè các report cũ trong P0.

## File đã đổi và kiểm chứng sau khi ghi

- Đã tạo [ANANTA_MASTER_ROADMAP.md](ANANTA_MASTER_ROADMAP.md).
- Đã tạo [ANANTA_CURRENT_HANDOFF.md](ANANTA_CURRENT_HANDOFF.md).
- Không sửa `AGENTS.md`, ExternalActors hoặc report cũ. P2 đã sửa CoastalCity map/material
  packages do generator tạo, bốn helper/readback script, `CoastalQA.cpp` và hai Docs.
- Lệnh và exit code mới: `python -m py_compile` exit 0; `Build-ANANTA.ps1` exit 0;
  `BuildCoastalCity.py` exit 0; material readback exit 0; headed Day/BlueHour đều
  `COASTAL_QA_COMPLETE failures=0 views=5`. Warnings còn lại: Lumen scalability
  priority, UE-MCP Slate startup, deprecated `save_current_level`, environment DLL/SDK
  notices; không có content error trong các gate trên.
- Chưa kiểm: RTX 3050/4060 frame-time, VRAM, 60 FPS, soak/benchmark, P3 streaming.
- Sau baseline sync đã chạy `& .\Tools\Build\Validate-ANANTA.ps1` (exit 0),
  `git diff --check` (exit 0, chỉ warning line-ending của `AGENTS.md`) và
  `git status --short --branch`.

## Commit và push

- P0 Docs commit: `927369f8bbc4fa5b0a1a5981fa1d927533e6bf3d` (`docs: establish ANANTA master roadmap and handoff`).
- P1 implementation/docs commit: `c854fad796610e42c01f36cd7cff815be1181134` (`qa: refresh coastal model and placement reviews`).
- P2 readback script/docs commit trước phiên: `8e63eb1d6adb05b1a98bc9f803e78e5b17aba76c`.
- P2 commit: `25bee1260842c7ee5e74bedde5c22f740f010519` (`qa: complete coastal hero material slice`).
- Push: `git push origin main` exit 0; remote `refs/heads/main` =
  `25bee1260842c7ee5e74bedde5c22f740f010519`; không force-push, `AGENTS.md` không stage.

## Prompt pha tiếp theo

```text
PHASE P2 — Hero slice, material graph và headed visual.

Đọc ANANTA_MASTER_ROADMAP.md và ANANTA_CURRENT_HANDOFF.md.
Baseline P1 đã đạt source/geometry gate; không sửa AGENTS.md, evidence cũ, map hoặc gameplay ngoài scope.
Chốt material graph/output readback và hero slice 200–300 m; headed capture chỉ chạy khi prompt cho phép.
Không claim visual/FPS từ Blender, static parse, build hoặc NullRHI; cập nhật hai Docs với evidence mới.
```

## P4A P4B continuation 2026-10-15

Phase ID: P4A plus P4B — Interaction data driven and transit state
Trạng thái: PARTIAL — source build and coastal map commandlet pass; bounded runtime QA launch did not produce a fresh log and headed visual collision was not run

### File đã đổi trong chat
- Source/ANANTA/Public/CoastalInteractable.h
- Source/ANANTA/Private/CoastalInteractable.cpp
- Source/ANANTA/Public/CoastalTransitTypes.h
- Source/ANANTA/Public/CoastalVehicle.h
- Source/ANANTA/Private/CoastalVehicle.cpp
- Source/ANANTA/Public/CoastalTrain.h
- Source/ANANTA/Private/CoastalTrain.cpp
- Source/ANANTA/Public/CoastalQA.h
- Source/ANANTA/Private/CoastalQAGameplay.cpp
- Tools/Upgrade/coastal_scene.py
- Tools/Upgrade/coastal_transit.py
- Content/ANANTA/Maps/ANANTA_CoastalCity.umap and generated CoastalUpgrade material packages
- AGENTS.md was not edited or staged

### Evidence mới
- `& .\Tools\Build\Build-ANANTA.ps1 -MaxParallelActions 2` exit 0 after source changes; UHT and link produced a fresh UnrealEditor-ANANTA.dll.
- `python -X utf8 -m py_compile Tools/Upgrade/coastal_scene.py Tools/Upgrade/coastal_transit.py Tools/Upgrade/coastal_rooms.py` exit 0.
- Coastal map commandlet exit 0 with `COASTAL_MAP_OK 23 enterable buildings, 6743 instances / 814 HISM batches`; warnings were Slate startup, Lumen scalability priority and deprecated save_current_level.
- Source now exposes VenueId, PropId, InteractionKind, prompt, response, collision policy, save key, failure message and P4A interaction markers while preserving legacy Kind 0 through 6.
- Transit source now exposes road emergency rowboat aircraft and helicopter states, bounded route and stop rules, train signal stop and boarding alighting APIs, and rowboat feedback.

### Runtime gate and remaining errors
- CoastalQA launch attempts exited 1 or were stopped by a watchdog before a fresh abslog was created. The latest failed launch produced no current `COASTAL_CHECK` or `COASTAL_QA_COMPLETE` marker, so P4A/P4B runtime gate is not PASS.
- Headed visual and collision capture was not run. GPU FPS and VRAM were not measured. Save persistence remains outside this phase.
- Generated map and material packages are dirty from the successful commandlet and need review before staging. No commit or push was made in this partial turn.

### W3 fresh Unreal readback continuation (2026-10-16)

- Đã khởi động editor Unreal riêng cho W3 qua UE-MCP; project `D:/GAME/ANANTA/ANANTA.uproject`, engine 5.8, bridge kết nối ở port `60765`, thời gian sẵn sàng khoảng 52.9 giây. Đây là phiên read-only và không sửa asset Unreal.
- Readback mới ghi vào `Tools/W3/ReadbackEvidence.json` cho `/Game/ANANTA/CoastalUpgrade/Materials/M_Ocean` và `/Game/ANANTA/City/Materials/M_DistrictWater`. Cả hai đang opaque và có custom normal động; các output BaseColor/Normal/Roughness/Emissive được ghi nhận theo graph hiện tại.
- Custom expression readback cho thấy hai material chưa giữ được tuple direction/wavelength/amplitude/speed/phase của `wave-spec.json`; chưa có `MF_AnantaWater`, foam output hoặc parameter contract đầy đủ. Validator `Tools/W3/ValidateReadback.py` kiểm tra source hash `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f` và giữ các cờ chưa đạt ở `false`.
- Native boundary collision và ảnh so sánh cùng camera coast/beach_boat/offshore chưa có readback mới. Không dùng material readback này để claim 60 FPS.

**DONE:** read-only graph evidence và validator contract.
**PARTIAL:** material hiện có opaque water + dynamic normal nhưng chưa phải `MF_AnantaWater` theo wave-spec.
**UNVERIFIED:** native boundary collision, same-camera Three.js/Unreal comparison, visual direction equivalence và headed performance.
**BLOCKED:** exact graph port cần tạo/sửa Unreal asset trong khi các file Unreal dirty phải giữ nguyên; chưa thực hiện trong lượt này.

- Kiểm tra sau cùng: `python Tools/W3/ValidateReadback.py` exit `0`; `Tools/Build/Validate-ANANTA.ps1` exit `0`; `Tools/Build/Build-ANANTA.ps1 -MaxParallelActions 2` exit `0` sau khi đóng editor W3. `git diff --check` exit `0` (chỉ cảnh báo chuyển LF/CRLF).
- `git lfs fsck` exit `1` với nhiều `unexpectedGitObject` trong `Assets/CoastalUpgrade/*` của tree remote `5268d9a15649fd5ad59e5bc5d6878131834ddacf`; đây là lỗi LFS tồn tại trước pha W3, không sửa hoặc xóa object.

### Prompt pha tiếp theo
Fix the Unreal commandlet launch or provide a supported bounded QA entrypoint that writes a fresh log, then run CoastalQA checks for normalized interaction metadata, failure messages, NPC schedule, aircraft and helicopter control state, train signal stop, boarding, alighting, route bounds and rowboat input. Run the short headed visual collision capture only after the runtime gate has a fresh exit and marker. Review generated map and material diffs, stage only P4 files plus the handoff, commit on main and push after all gates pass. Keep AGENTS.md untouched and do not claim FPS or persistence.

## P4C Persistence 2026-10-15

Phase ID: P4C — Persistence
Trạng thái: PASS — schema 2, migration, corruption rejection và quick Check/Reload bounded đã đạt; native Coastal actor hooks và backend economy thật vẫn là giới hạn fixture.

### File đã đổi trong pha này
- Source/ANANTA/Public/City/ANANTACityState.h
- Source/ANANTA/Private/City/ANANTACityState.cpp
- Source/ANANTA/Public/City/ANANTACitySubsystem.h
- Source/ANANTA/Private/City/ANANTACitySubsystem.cpp
- Source/ANANTA/Public/QA/CityPersistenceCheckSubsystem.h
- Source/ANANTA/Private/QA/CityPersistenceCheckSubsystem.cpp
- Source/ANANTA/Private/Tests/CityPersistenceTests.cpp
- Docs/ANANTA_MASTER_ROADMAP.md
- Docs/ANANTA_CURRENT_HANDOFF.md

### Contract và giới hạn
- `UANANTACitySave` giữ schema 1 để đọc save cũ và migrate sang schema 2; schema không hỗ trợ, slot hỏng hoặc state invalid bị từ chối và không ghi đè file hiện có.
- Schema 2 lưu interaction door/prop/district, NPC schedule, vehicle/transit transform route boarding signal, inventory/city tokens và day/night layer cùng mission/service state.
- Check/Reload dùng fixture event IDs để chứng minh save API và process reload. Report ghi `fixture_mode=true`, `backend_economy=fixture_only` và `native_coastal_actor_hooks=false`; chưa tuyên bố Coastal `ACoastalInteractable`/`ACoastalVehicle` native hook hoặc economy backend thật.

### Lệnh và evidence mới
- `& .\Tools\Build\Build-ANANTA.ps1 -MaxParallelActions 2` — exit 0.
- Automation `ANANTA.City.Persistence` — exit 0; `Saved/QA/CityPersistenceAutomation3/index.json` ghi `succeeded=4`, `succeededWithWarnings=1`, `failed=0`, `notRun=0`, `inProcess=0`, report `2026.10.15-15.55.56`.
- `-game -CityPersistenceCheck -CityQASlot -NullRHI -unattended -NoSound` trên `ANANTA_City` — exit 0; `Saved/QA/CityPersistence/Report.txt` ghi schema 2 và các state group.
- `-game -CityPersistenceReload -CityQASlot -NullRHI -unattended -NoSound` trên process khác — exit 0; `Saved/QA/CityPersistence/Reload.txt` ghi snapshot khớp checkpoint, PID khác và `status=PASSED`.
- Warning còn lại: truncated payload test tạo warning deserializer `Failed to find object 'Class '` nhưng không fail test; không có crash ở lượt PASS.

### Chưa kiểm và không thuộc P4C
- Chưa chạy headed/PIE visual, GPU/VRAM, frame-time hoặc FPS; không dùng NullRHI làm visual/FPS proof.
- Chưa nối persistence trực tiếp vào Coastal P4A actor interactions, chưa có backend economy thật và chưa chạy soak/benchmark.

Commit hash: pending
Push hash: pending

### P4C commit and push receipt

Commit hash: a6ef5d2b6079669bae70c229530707e813a4886d
Push hash: a6ef5d2b6079669bae70c229530707e813a4886d (`refs/heads/main`)

## P4A P4B completion 2026-10-16

Phase ID: P4A plus P4B — interaction data driven and transit state
Trạng thái: DONE bounded — source, map, runtime logic and headed hero collision gates đạt; FPS, VRAM, full map AAA quality and Three.js water prototype gate chưa có bằng chứng.

### Thay đổi trong lượt này

- `Source/ANANTA/Private/CoastalQAGameplay.cpp` chọn vehicle loại `Road` hoặc `Emergency` cho bài kiểm tra W drive; aircraft và helicopter vẫn được kiểm tra riêng trong `TestTransit`. Lỗi trước đó chọn `CivilAirplane`, bị collision route và làm `W_key_drives_vehicle` fail.
- Tạo `Tools/Build/Test-CoastalInteractive.ps1` làm bounded entrypoint. Script truyền map `/Game/ANANTA/Maps/ANANTA_CoastalCity`, ghi log mới theo UTC dưới `Saved/QA/CoastalInteractive`, kiểm tra exit code và marker `COASTAL_QA_COMPLETE` theo mode `views=122` hoặc `views=5`.
- Sửa wrapper sau lỗi thật `PSInvalidOperationException: There is no Runspace available to run scripts in this thread` bằng `ProcessStartInfo.ArgumentList` và `ReadToEndAsync` thay cho PowerShell `DataReceivedEventHandler` callback.

### Evidence mới sau sửa

- `& .\\Tools\\Build\\Build-ANANTA.ps1 -MaxParallelActions 2` — exit 0; UHT, compile `CoastalQAGameplay.cpp`, link `UnrealEditor-ANANTA.dll` và metadata đều thành công. Warning còn lại là `GetMovementBase` deprecated và VS compiler 14.51 chưa preferred.
- `python -X utf8 -m py_compile Tools/Upgrade/coastal_scene.py Tools/Upgrade/coastal_transit.py Tools/Upgrade/coastal_rooms.py` — exit 0.
- `& .\\Tools\\Build\\Validate-ANANTA.ps1` — exit 0; `BridgeDescriptor=True`, `WorkflowConfig=True`, `MissingPlugins/Files` rỗng.
- `git diff --check` — exit 0; chỉ có cảnh báo LF to CRLF trên các file đã dirty, không có whitespace error.
- Map commandlet `UnrealEditor-Cmd.exe ANANTA.uproject -run=pythonscript -script=Tools/Upgrade/BuildCoastalCity.py -NullRHI -unattended -NoSplash -FullStdOutLogOutput -abslog=Saved/QA/CoastalInteractive/20261016-map-commandlet.log` — exit 0; `MapCheck: 0 Error(s), 0 Warning(s)`; `COASTAL_MAP_OK 23 enterable buildings, 6743 instances / 814 HISM batches`. Summary có 4 warning đã biết: Lumen scalability priority, UE-MCP Slate startup, deprecated `save_current_level` và SDK notices.
- `& .\\Tools\\Build\\Test-CoastalInteractive.ps1 -TimeoutSeconds 330` — exit 0; log `Saved/QA/CoastalInteractive/20261015-173630083/runtime.log`; marker `COASTAL_QA_COMPLETE failures=0 views=122`; runtime folder `Saved/Upgrade/Runtime/2026.10.15-17.36.38`. Checks mới gồm normalized interaction, failure message, NPC schedule, aircraft/heli state, route bounds, train signal stop, boarding/alighting, road vehicle drive, rowboat drive/exit và ocean boundary; tất cả `1`.
- `& .\\Tools\\Build\\Test-CoastalInteractive.ps1 -HeadedHero -TimeoutSeconds 330` — exit 0; log `Saved/QA/CoastalInteractive/20261015-173951316/runtime.log`; marker `COASTAL_QA_COMPLETE failures=0 views=5`; runtime folder `Saved/Upgrade/Runtime/2026.10.15-17.40.03`. Năm PNG mới: `hero_day`, `hero_blue_hour`, `hero_street`, `hero_interior`, `hero_coast`; metadata ghi resolution 1920x1080 profile Day. Đã xem `hero_day.png` và `hero_coast.png`: đô thị, mặt nước rộng, sóng nhẹ và xuồng hiện diện; không thấy gap nền trong hai view. Đây là bounded visual/collision review, không phải FPS proof.

### Phân loại hiện tại

**DONE:** P4A/P4B bounded interaction and transit gate; 23 doorway/service/NPC interactions; normalized metadata and failure response; NPC schedule; road/emergency/rowboat/aircraft/helicopter states; train signal stop, direction, boarding and alighting; route bounds; ocean boundary; fresh map commandlet; fresh headed hero capture; build and source gates.

**PARTIAL:** headed review mới bao phủ năm camera hero và collision checks; chưa phải review toàn bản đồ hoặc chứng nhận chất lượng AAA ở mọi district. Water material/foam/boundary đã có trong CoastalUpgrade và xuất hiện ở hero coast, nhưng chưa có Three.js prototype gate trong checkout để làm tiền đề port shader/parameters.

**UNVERIFIED:** GPU frame time, VRAM, 60 FPS, soak/benchmark; full map visual quality; anime character/NPC style audit; Three.js water prototype pass; World Partition/HLOD/Data Layers/PCG; backend economy and native persistence hooks; aircraft flight path visual review.

**BLOCKED:** không có blocker cho bounded P4A/P4B. Three.js water port và FPS acceptance vẫn blocked by missing prototype/runtime evidence, không được tuyên bố hoàn thành từ build hoặc NullRHI.

### Commit scope

Chỉ stage file P4A/P4B và handoff này; giữ `AGENTS.md` untouched. Generated CoastalCity map/material packages được review là output của map commandlet và nằm trong scope P4. Commit/push chỉ thực hiện sau khi diff review và mọi gate bắt buộc ở trên vẫn đạt.

### P4A P4B commit and push receipt

Commit hash: `8f0889168cfe169d1f0b309526afceea7341aa66`
Push hash: `8f0889168cfe169d1f0b309526afceea7341aa66` (`refs/heads/main`)

## W1 Three.js water prototype — 2026-10-16

Phase ID: W1 — Three.js water prototype gate before Unreal port.

### Dirty ownership and scope

- Pre-change `git status --short --branch` showed `main...origin/main` and only
  pre-existing ` M AGENTS.md`. That file was not edited, staged or overwritten.
- No Unreal file was changed in W1. Historical P4A/P4B commit `8f088916...` and
  its bounded evidence remain historical; this turn has no fresh Unreal runtime
  log, so P4A/P4B are **PARTIAL** for the current handoff and are not reclassified
  as a new runtime PASS.
- New scope is limited to `Prototypes/ThreeWater/`, the art/water contract and
  these roadmap/handoff notes. Generated `node_modules` and `dist` are temporary
  and are not part of the phase deliverable.

### W1 implementation

- `WaveField` has four sanitized low-preset waves and samples height plus a normal
  derived from the same phase field.
- `WaterSurface` uses one fixed plane and shader uniforms; it does not rebuild
  geometry in the animation loop. The shader carries wavelength, speed and
  phaseOffset using the contract formula.
- `ShoreFoam` provides a fixed translucent shore band. `CoastBoundary` provides
  XZ containment/clamp and a visible rectangle preview.
- `main.js` provides orbit/free camera, keyboard toggles, a bobbing boat visual
  fixture and `PerformanceOverlay` frame-time/render information.
- `wave-spec.json`, `README.md` and `Docs/ANANTA_ART_AND_WATER_CONTRACT.md` record
  Three.js Y-up to Unreal Z-up mapping, interaction/static-dressing boundaries,
  review requirements and the no-FPS-inference rule.

### Evidence mới

- `npm install` — exit 0; lockfile created. npm reported two audit advisories and
  an install-script approval warning; neither blocked the prototype gate.
- `npm run check` — exit 0; all six JavaScript modules passed `node --check`.
- `npm run build` — exit 0; Vite produced `dist/index.html` and a bundled asset.
  Vite emitted only the known chunk-size warning (>500 kB).
- `node --input-type=module` WaveField runtime check — exit 0; printed
  `WAVE_RUNTIME_CHECK=PASS waves=4 height=0.169722 normalY=0.999316` after the
  preset was synchronized with `wave-spec.json`.
- Browser smoke at `http://127.0.0.1:4178/` — Vite server ready; body
  `data-qa-ready=true`; visible status `Ready · orbit camera · 4 waves`; console
  error log empty. A fresh screenshot showed visible wave bands, shore foam,
  boundary edges and the boat fixture. The synchronized run reported
  `frame 17.62 ms`, `drawCalls 7`, `triangles 51268`, `waves 4`, `boundary on`,
  `foam on`; these measurements are observation only, not a 60 FPS claim.
- Input smoke toggled orbit to free camera and toggled boundary/foam visibility;
  a second orbit camera frame remained continuous without a visible seam.

### Phân loại W1

**DONE:** W1 source contract, four-wave fixed-mesh shader prototype, foam/boundary
preview, orbit/free camera, overlay, dependency lock, syntax/build gate and
browser smoke gate.

**PARTIAL:** P2 remains a bounded visual pass and is not AAA art acceptance;
P4A/P4B have no fresh Unreal runtime log in this W1 turn; the prototype boat is
only a visual/static-dressing fixture.

**UNVERIFIED:** headed Unreal water port, native Coastal persistence/interaction,
full-city anime character/NPC audit, GPU/VRAM frame-time percentile, 60 FPS on
RTX tiers, soak/benchmark, and seam behavior beyond the browser smoke views.

**BLOCKED:** Unreal shader/parameter port is intentionally blocked until W1
prototype evidence is reviewed as the source gate. No Unreal file was modified.

### Prompt pha tiếp theo

`W2 — Review W1 browser evidence and port only the accepted water shader/parameters
to Unreal. Keep AGENTS.md and all unrelated dirty files untouched; do not claim
60 FPS, native persistence or AAA quality from build, config or NullRHI. Add fresh
headed/runtime evidence before changing P4A/P4B classifications.`

## W2/W3 Coastal water continuation (2026-10-16)

Phase ID: W2 — coastal waves, foam, boundary and quick visual QA; W3 — Unreal
water contract handoff.

### Dirty ownership before W2 changes

- Pre-change `git status --short --branch` was `main...origin/main` with only
  pre-existing ` M AGENTS.md`. `AGENTS.md` was preserved and is still not staged.
- No Unreal file was edited in this turn. Existing interaction/transit work is
  historical and has no fresh Unreal runtime log in this W2 turn, so P4A/P4B
  remain **PARTIAL** for current handoff classification; build or old map logs
  are not converted to runtime PASS.
- W2 files are limited to `Prototypes/ThreeWater/`, `Tools/QA/ValidateThreeWaterSpec.py`
  and the water/roadmap/handoff contract documents. No old asset or map file was
  overwritten.

### W2 implementation

- Expanded the water extent to box boundary `minX=-700`, `maxX=700`, `minZ=-400`,
  `maxZ=400`, with camera margin 14 m and boat margin 8 m. `CoastBoundary`
  supports box/polygon preview, containment, distance-to-shore and clamp.
- `ShoreFoam` uses one fixed plane and shader distance to the nearest boundary
  edge with `foamWidth=6 m` and `shorelineDepth=16 m`. The low preset keeps one
  fixed water mesh and `cpuMeshRebuild=false`.
- Added fixed `coast`, `beach_boat` and `offshore` presets. Auto QA runs each for
  10 seconds, then freezes and reports average, p95, max and outlier count.
- `wave-spec.json` v2 and the Unreal contract use SHA-256
  `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f`; validator
  enforces schema, units, axes, four exact wave tuples, foam, boundary, scenes,
  Unreal mapping and `fpsClaim=false`.

### Evidence mới và exit code

- `npm run check` — exit 0; JavaScript syntax checks passed.
- `npm run build` — exit 0; Vite transformed 12 modules and emitted the known
  chunk-size warning for a 731 kB minified asset.
- `python Tools/QA/ValidateThreeWaterSpec.py` — exit 0;
  `THREE_WATER_SPEC_OK sha256=f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f waves=4 scenes=3 duration=10s`.
- WaveField runtime smoke — exit 0;
  `WAVE_RUNTIME_CHECK=PASS waves=4 height=0.198274 normalY=0.999875`.
- `git diff --check` — exit 0; only Git LF-to-CRLF advisories for dirty text
  files, no whitespace error.
- Browser cache-bust run at `http://127.0.0.1:4178/?qa=1792089950750` completed
  all three 10-second scenes. Overlay reports coast `avg 17.67 ms, p95 18.60,
  max 23.50, outliers 0`; beach/boat `17.72, 18.40, 19.20, 0`; offshore
  `17.73, 18.50, 19.40, 0`. Final frame showed visible broad water and shore
  foam/boundary edge; overlay had 4 waves, boundary on and foam on. Console error
  log was empty; browser logs contained only Vite connect/debug entries.

- `& .\Tools\Build\Build-ANANTA.ps1 -MaxParallelActions 2` — exit 0; target up to date, Unreal build completed successfully. This build is a build receipt only and does not prove runtime, visual or FPS acceptance.

### Current classification

**DONE:** W2 fixed-mesh source changes, broad sea boundary, foam fade, camera/boat
clamp, three 10-second scene reports, contract hash/schema validator, check/build
and browser smoke.

**PARTIAL:** W2 visual evidence is a prototype water slice. It does not accept
AAA quality for the full city or interaction/static-dressing coverage for every
house, NPC, prop, vehicle, rail, station, airport, boat or venue.

**UNVERIFIED:** F1 headed GPU/CPU/VRAM frame-time percentile, 60 FPS on target
RTX tiers, native Unreal collision, Unreal visual direction comparison and full
map visual quality. The browser overlay is measurement evidence, not a 60 FPS
claim.

**BLOCKED:** W3 Unreal acceptance is blocked until a real Unreal material graph
readback proves BaseColor/Normal/Roughness/Emissive, native boundary collision is
read back at the authored edge, and the three named cameras are compared between
Three.js and Unreal. No Unreal file was modified in W2.

### W2 fresh browser smoke continuation (2026-10-16)

- `npm ci --ignore-scripts` trong `Prototypes/ThreeWater` — exit `0`; npm báo
  2 advisory vulnerabilities (1 moderate, 1 high), không tự chạy `npm audit fix`.
- `npm run check` — exit `0`; `npm run build` — exit `0`; Vite build transform
  12 modules và giữ warning chunk 731 kB.
- `python Tools/QA/ValidateThreeWaterSpec.py` từ repository root — exit `0`;
  hash `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f`,
  4 waves, 3 scenes, 10 giây mỗi scene.
- Browser `http://127.0.0.1:4178/` đạt `qaReady=true`; DOM hiển thị
  `W2 quick QA complete · coast/beach_boat/offshore reports ready`. Browser quick
  QA mới ghi coast `avg 7.60 ms, p95 8.20, max 96.30, outliers 1`; beach_boat
  `avg 7.60 ms, p95 8.20, max 11.10, outliers 0`; offshore `avg 7.64 ms,
  p95 8.20, max 16.50, outliers 0`. Overlay cuối ghi 4 waves, boundary on,
  foam on, drawCalls 4 và triangles 51204.
- Key smoke mới xác nhận `1/2/3` đổi đúng coast/beach_boat/offshore; `B` đổi
  boundary on/off và drawCalls `4→3`; `F` đổi foam on/off và drawCalls `3→2`.
  Browser console `warn/error` không có entry.
- Đây là prototype/browser evidence; không chuyển các frame-time này thành
  claim 60 FPS hoặc native Unreal acceptance. W3 vẫn **BLOCKED** chờ graph
  readback, boundary collision readback và ảnh so sánh cùng camera.

### Prompt pha tiếp theo

```text
W3 — Port the accepted wave-spec.json values into Unreal only after reviewing
Docs/ANANTA_UNREAL_WATER_CONTRACT.md. Create/read back MF_AnantaWater outputs
BaseColor, Normal, Roughness and Emissive; keep boundary collision separate from
the shader; compare coast, beach_boat and offshore cameras. Do not add water
physics/buoyancy and do not claim 60 FPS before F1. Keep AGENTS.md and unrelated
Unreal dirty files untouched. Record fresh runtime/readback evidence before
reclassifying W3 or P4A/P4B.
```
## W2/W3 commit and push receipt

- Implementation/docs commit: `6394e505a3438142fc3ef431efd9cc1d2962e7d`
  (`feat: expand coastal water quick qa contract`).
- Push: `git push origin main` exit 0; remote `refs/heads/main` matched
  `6394e505a3438142fc3ef431efd9cc1d2962e7d`. No force-push was used.
- `AGENTS.md` remains the only unrelated dirty file and is not staged.
## V1 Visual bible contract (2026-10-16)

Phase ID: V1 — visual bible mới: hiện đại + anime có kiểm soát.

### Ownership và scope

- Pre-change dirty state chỉ có `AGENTS.md`; file này được giữ nguyên và không
  stage. V1 chỉ sửa contract art/water và handoff, không sửa Unreal, map, asset,
  generator hoặc toàn map.
- World style được khóa hiện đại bán thực tế cho kiến trúc, đường phố, xe, rail,
  ga, sân bay, biển và props. Character/NPC dùng anime có kiểm soát nhưng chung
  scale, exposure, shadow và material response với thế giới.

### Contract đã ghi

- Palette cố định cho asphalt, concrete, facade, rail metal, glass/water,
  vegetation, sand, wayfinding và character accent.
- Material rules cho world PBR và character `skin`, `hair`, `cloth`, `eye`,
  `accessory`, outline/rim tùy chọn; có texture reuse rule theo material key,
  semantic, SHA-256 và perceptual hash.
- Scale reference human rig 1.75 m, eye height 1.60 m, door, curb, lane, sedan
  và rail gauge; review camera phải ở ngang tầm người.
- Lighting reference cho day street, interior, coast, traffic và NPC.
- Hero list gồm street block, interior lobby, seawall/coast, sedan, rail station,
  civilian NPC, transit NPC và street furniture; mỗi asset yêu cầu provenance,
  licence, pivot, transformed bounds, LOD, collision và texture hashes.
- V1 gate cấm mở rộng toàn map trước khi hero sample có palette/material/scale/
  lighting/readback và năm camera `street`, `interior`, `coast`, `traffic`, `npc`.

### Evidence và phân loại

- Python contract assertion — exit 0; `V1_CONTRACT_CHECK=PASS bytes=14582`.
- `git diff --check -- Docs/ANANTA_ART_AND_WATER_CONTRACT.md` — exit 0; chỉ có
  cảnh báo line-ending của Git.

**DONE:** V1 visual bible contract và hero asset checklist.
**PARTIAL:** chưa tạo hoặc sửa hero assets trong pha này.
**UNVERIFIED:** hero captures/readback ở camera ngang tầm người, texture reuse
audit thực tế và chất lượng visual AAA.
**BLOCKED:** không mở rộng toàn map cho tới khi hero sample đạt V1 gate.

## A1 — Model và texture pipeline chất lượng (2026-10-16)

Phase ID: A1 — Blender headless shading, texture channels và bounded review.

### Dirty ownership và phạm vi

- Pre-change `git status --short --branch` là `main...origin/main` với duy nhất
  ` M AGENTS.md` có sẵn. `AGENTS.md` được giữ nguyên, không stage và không ghi đè.
- A1 chỉ thêm bốn script trong `Tools/Upgrade/`: `ApplyA1Shading.py`,
  `GenerateA1Textures.py`, `ReviewA1Coverage.py` và `RenderA1Reviews.py`.
  Không sửa Unreal, map, ExternalActors, asset source hoặc file dirty cũ.
- Blender cài đặt được kiểm tra là `4.5.1 LTS`. API readback ghi
  `HAS_AUTO_SMOOTH=False`, `GeometryNodeSetShadeSmooth=True`,
  `modifier_add_node_group=True` và `WeightedNormalModifier=True`.
  Vì Blender 4.1+ đã bỏ `Mesh.use_auto_smooth`, script không dùng property đó ở
  nhánh mới; asset Smooth by Angle được thử bằng operator đúng API.

### Texture evidence mới

- `GenerateA1Textures.py` chạy thật với
  `--size 2048 --hero-key Concrete --hero-key Asphalt` — exit `0`, marker
  `A1_TEXTURES_OK`, 35 PNG, 20 map sinh và 15 map reuse/hardlink.
- `Saved/QA/A1Shading/Textures/manifest.json` có 5 key (`Concrete`, `Brick`,
  `Asphalt`, `Tile`, `Sand`) × 7 channel (`BaseColor`, `Normal`, `Roughness`,
  `AO`, `Metallic`, `Emissive`, `Foam`). Mỗi channel có path và SHA-256; Concrete
  và Asphalt yêu cầu 2K, các key còn lại 1K. Các map source 1K được reuse khi đã
  tồn tại, vì vậy requested 2K không được ghi thành actual 2K cho map reuse.
- Channel parser sau fix nested manifest — exit `0`: `recordCount=5`,
  `channelsPerKey=[7]`, `availablePerKey=[7]`, `hashMissing=0`.

### Shading và review evidence mới

- `ApplyA1Shading.py` chạy bằng Blender 4.5.1 trên source blend và ghi mới
  `Saved/QA/A1ShadingFixed2/CoastalModels_A1.blend` cùng manifest. Blender bị
  API RC watchdog giữ sau bước save nên session được dừng có chủ đích sau khi
  output tồn tại; process exit do Ctrl+C là `1`, không được gọi là runtime PASS.
- Manifest shading mới ghi `blendOpened=true`, `objectsProcessed=72`,
  `materialsProcessed=1`, 24 object curved dùng
  `geometry_nodes_set_shade_smooth_fallback`, 15 bevel và 15 weighted normals.
  Smooth by Angle Essentials asset trả `{'CANCELLED'}` với thông báo asset
  loading unfinished; fallback `GeometryNodeSetShadeSmooth` được ghi rõ và
  không được tuyên bố là angle threshold native. Texture records đã đọc đủ
  5×7 channel/hash, nhưng material nguồn duy nhất là `CoastalSurface` và không
  có `a1_surface_key` tương ứng; script không tự đoán gán Concrete/Asphalt.
- `ReviewA1Coverage.py --dry-run` exit `0`, tính đầy đủ 72 model × 8 hướng và
  6,743 placement × 5 góc. Bounds dùng đủ 8 local corners theo thứ tự
  `scale -> yaw -> translation`; report là coverage/bounds evidence, không phải
  native visual acceptance.
- `RenderA1Reviews.py` dry-run exit `0`: 2 model = 16 view và 3 placement = 15
  view. Render thật bounded trên blend A1 exit sau Ctrl+C `1` sau khi save; output
  mới `Saved/QA/A1Reviews/20261016-A1` có 64 model PNG (8 model × 8 azimuth),
  40 placement PNG (8 placement × 5 góc) và hai coverage JSON. Placement đầu
  tiên của layout cũ là `Cube` placeholder nên được ghi là visual fallback; một
  review riêng chọn placement mesh thật (`StreetLamp`, `StreetBin`,
  `ParkingMeter`) tại source index 77–84, ghi 40 view và mọi entry `status=rendered`.
  `visualAcceptance` vẫn là `pending_headless_render_only`.

### Phân loại A1

**DONE:** source/headless pipeline, Blender 4.5 API branching, fixed-mesh-safe
  texture generation/reuse, 7 channel manifest/hash, 72-object shading report,
  full transformed-bounds coverage calculation và bounded fresh 8-direction /
  5-angle render evidence.

**PARTIAL:** visual review mới là headless Blender với neutral light; material
  nguồn `CoastalSurface` chưa có mapping explicit tới 5 surface texture keys;
  Smooth by Angle asset không load được trong Blender 4.5 và fallback không áp
  angle threshold. Chưa đạt visual AAA hoặc hero acceptance camera ngang tầm người.

**UNVERIFIED:** full fresh 72×8 model render, toàn bộ 6,743×5 placement render,
  texture readback trên từng Unreal/native material, provenance/licence audit,
  all priority groups, GPU/VRAM frame-time và 60 FPS. Build, config, headless
  render và NullRHI không được dùng để kết luận FPS.

**BLOCKED:** không có blocker cho bounded A1 source evidence; native Unreal
  material/runtime port, full-map AAA acceptance và F1 performance gate vẫn
  blocked bởi thiếu headed/native evidence. Không có file Unreal nào được sửa.

### Prompt pha tiếp theo

```text
A2 — Gán surface keys explicit cho hero material và review headed ở camera
ngang tầm người. Giữ nguyên A1 report, không đoán mapping CoastalSurface,
không sửa Unreal dirty files và không claim AAA hoặc 60 FPS từ headless output.
```

## A2 — Hero district và venue thật (2026-10-16)

Phase ID: A2 — tranche `street_civic`, chỉ làm street kit và civic block. Không
đụng toàn map, Unreal source, map/ExternalActors hoặc các file dirty có sẵn.

### Dirty ownership và phạm vi

- Trước A2, `AGENTS.md`, các tài liệu A1 và bốn script A1 đã dirty; các file đó
  được giữ nguyên. A2 chỉ thêm `Tools/A2/VerifyVenueStates.py`,
  `Tools/A2/BuildStreetCivicHero.py` và `Tools/A2/ReviewStreetCivic.py`, cùng
  hai manifest QA ignored trong `Saved/QA/A2/`.
- Street kit lấy signal từ `Generate_Nova_ModularKit.py` và props source; civic
  block lấy `CityCivicDistrict.py` và `expansion_architecture.py`. Manifest chỉ
  mô tả bounded tranche, không tuyên bố đã sửa hoặc mở rộng toàn map.

### Venue state contract

`VerifyVenueStates.py` phân loại bằng entry/room source, khai báo service đầy đủ,
`FCityServiceState::IsServiceId` nhận đúng id/kind và `Interact` gọi
`TryUseService`. Actor tồn tại một mình không bao giờ là bằng chứng interaction.
Report source-only có 18 venue: `enterable_interactive=10`,
`enterable_static_dressing=7`, `shell_only=1`.

- Civic `Police`, `Fire`, `Bar`, `Arcade`: `enterable + interactive` theo source
  và service runtime contract; fixture mới xác nhận bốn id này.
- Civic `AmusementPark`: `shell-only` vì không có entry/service contract.
- Expansion `Bookshop`, `Clinic`, `Market`, `Gallery`, `Workshop`, `Transit`:
  source-classified `enterable + interactive`, nhưng chưa có runtime pass riêng.
- Expansion `ToyShop`, `Salon`, `Bakery`, `Library`, `Restaurant`, `Cinema`,
  `Hotel`: `enterable + static dressing`; service id hiện chưa được
  `CityServiceState` nhận diện. Không ghi các venue này là interactive chỉ vì
  actor hoặc helper đã tồn tại.

### Evidence mới

- `python Tools/A2/VerifyVenueStates.py --dry-run` — exit `0`, deterministic,
  schema `A2.venue-state-report.v1`, summary 10/7/1.
- `python Tools/A2/BuildStreetCivicHero.py --output
  Saved/QA/A2/street-civic-hero.json` — exit `0`, source gate PASS; street kit
  được ghi `static_dressing`, civic có 5 site và 5 camera review (bốn camera
  ngang tầm mắt 1.60 m, một camera upper 4.50 m).
- Fresh `Tools/Build/Test-CityCivic.ps1` — exit `0`, marker
  `CITY_CIVIC_CHECK_OK services=4 legs=8`, report
  `Saved/QA/CityCivicCheck/Report.json`; scope là authored-map physics/input
  fixture, `collisionBypass=false`, bốn service và tám doorway legs đều PASS.
- `python Tools/A2/ReviewStreetCivic.py --output
  Saved/QA/A2/street-civic-review.json` — exit `0`; source hashes còn khớp,
  runtime interaction gate PASS, 5 placement transformed bounds dùng đủ 8 local
  corners theo thứ tự `scale -> yaw -> translation`.

### Phân loại A2

**DONE:** state classifier có rule chống false-positive; bounded street/civic
manifest; review 5 camera và transformed bounds; fresh civic interaction
fixture cho Police/Fire/Bar/Arcade; không sửa Unreal hoặc full map.

**PARTIAL:** street kit mới là static dressing; review visual hiện có trạng thái
`visualPass=false`, các camera chỉ là `planned_headed_capture`; sáu expansion
venue interactive mới là source classification, chưa có runtime actor/import
readback riêng.

**UNVERIFIED:** headed 5-camera visual review, native map placement/bounds,
interaction cho expansion venues, shell/static quality, provenance/material,
GPU/VRAM/frame-time, 60 FPS và chất lượng AAA toàn district. Runtime fixture
`NullRHI` chỉ chứng minh logic/input/collision bounded, không chứng minh FPS.

**BLOCKED:** tranche tiếp theo (rail/transit và các venue còn lại) chờ street /
civic headed visual gate; không mở rộng toàn map hoặc commit/push A2 khi gate
visual chưa đạt.

### Prompt pha tiếp theo

```text
A2 tiếp theo — headed capture street/civic ở 5 camera và native placement
readback. Giữ classification interactive/static/shell, không sửa Unreal dirty
files, không mở rộng toàn map, không claim AAA hoặc 60 FPS từ build/NullRHI.
```

## F1 — Đo nhanh và tối ưu khoảng 60 FPS (2026-10-16)

Phase ID: F1. Phạm vi lượt này chỉ thêm contract/runner/parser dưới `Tools/F1/`; không sửa Unreal Source, map, ExternalActors hoặc asset dirty có sẵn.

### Dirty ownership và thay đổi

- Dirty có sẵn trước F1: `AGENTS.md`, `Docs/ANANTA_CURRENT_HANDOFF.md`, `Docs/ANANTA_MASTER_ROADMAP.md`, bốn script A1 dưới `Tools/Upgrade/` và `Tools/A2/`.
- F1 tạo mới: `Tools/F1/HeadedF1Probe.ps1` và `Tools/F1/SummarizeF1Evidence.py`. Ba thư mục run thật dưới `Saved/QA/F1/` được giữ làm evidence; hai fixture kiểm thử do lượt này tạo đã xóa.
- Runner nhận đúng ba scene `downtown_traffic`, `interior_alley`, `coast_streaming`, ép `-windowed`, resolution/internal scale và yêu cầu stat `fps`, `unit`, `gpu`, `sceneRendering`, `initviews`, `levels`, `memory`. Runner fail-closed nếu không có scene selector template chứa `{scene}`, không dùng NullRHI/offscreen.
- Parser yêu cầu headed evidence, renderer/scalability, CPU/GPU samples, VRAM, stat lines và streaming markers cho đủ ba scene; ngưỡng tham chiếu là `1000/60 = 16.667 ms`. Không có sample thì không tạo `fpsClaim`.

### Headed evidence mới

- `HeadedF1Probe.ps1 -Scene downtown_traffic -Width 1280 -Height 720` — exit `3`, run `20261016_003233521_aa7ef274`.
- `HeadedF1Probe.ps1 -Scene interior_alley -Width 1280 -Height 720` — exit `3`, run `20261016_003234682_94f08879`.
- `HeadedF1Probe.ps1 -Scene coast_streaming -Width 1280 -Height 720` — exit `3`, run `20261016_003235746_ba3a508c`.
- Cả ba metadata ghi `headed=true`, `nullRhi=false`, `offscreen=false`, `resolution=1280x720`, `internalScale=1`, nhưng `sceneSelector.provided=false`, `process.launched=false`, renderer/scalability/GPU/VRAM/stats đều thiếu. Lý do giống nhau: `UNVERIFIED: no scene selector template containing {scene}; refusing to launch an unselectable scene.`
- Không có headed CPU/GPU/VRAM frame-time, `stat unit`, `stat gpu`, `stat sceneRendering`, `stat initviews`, `stat levels`, VRAM hoặc streaming sample để tối ưu theo bằng chứng. Không claim 60 FPS.

### Gate nguồn/build mới

- PowerShell AST parse `Tools/F1/HeadedF1Probe.ps1` — PASS.
- `python -m py_compile Tools/F1/SummarizeF1Evidence.py` — exit `0`.
- Parser negative fixture sau khi bắt buộc VRAM — exit `1`, report `F1 UNVERIFIED`, thiếu `vram`; fixture đã xóa sau kiểm tra.
- `Validate-ANANTA.ps1` — exit `0`, `BridgeDescriptor=True`, `WorkflowConfig=True`, không thiếu plugin/file.
- `VerifyCityPerformanceBudget.py` — exit `0`, `status=PASS`, `sourceOnly=true`, `runtimeFpsVerified=false`, `groupCount=90415`, `instanceCount=1667907`, `uniqueSignatures=148`, `reusableFraction=0.999911`, manifest `95` mesh, không thiếu/invalid LOD.
- `VerifyCityInstanceReuse.py` — exit `0`, `uniqueSignatures=148`, `reusableInstances=1667759`, `verificationLevel=group-signature`.
- `Build-ANANTA.ps1 -MaxParallelActions 2` — exit `0`, `ANANTAEditor Development` up to date. Build không phải runtime/FPS evidence.

### Phân loại F1

**DONE:** F1 runner/parser fail-closed; ba scene labels và stat contract; source HISM/LOD/reuse audit; build/source checks mới; cleanup fixture do chat tạo.

**PARTIAL:** bằng chứng tối ưu hiện chỉ là source/static (`HISM`, reuse, LOD manifest). Chưa có bằng chứng để thay đổi HLOD/LOD/Nanite, culling/streaming, material complexity, shadow overlap, texture pool, foliage/Niagara hoặc water draw cost.

**UNVERIFIED:** renderer/scalability, resolution/internal scale readback từ game, CPU/GPU frame-time, VRAM, `stat unit/gpu/sceneRendering/initviews/levels`, frame-time giữa ba cảnh và headed 60 FPS.

**BLOCKED:** không có executable/scene selector được hỗ trợ để chạy ba cảnh headed; F1 không đạt FPS gate. Không sửa Unreal để né blocker.

## C1 — Closure và bàn giao (2026-10-16)

- `git diff --check` — exit `0` (chỉ cảnh báo LF→CRLF trên hai docs).
- `git ls-remote origin refs/heads/main` — exit `0`, remote `5268d9a15649fd5ad59e5bc5d6878131834ddacf`, trùng HEAD trước F1.
- `git lfs fsck` — exit `1`, nhiều `pointer: unexpectedGitObject` ở `Assets/CoastalUpgrade/*` trong tree `5268d9a...`; đây là lỗi repository/LFS có sẵn, không do F1 và không được tự sửa/xóa.
- Do F1 headed gate chưa đạt và LFS gate đang đỏ, **không stage, commit hoặc push** trong lượt này. Evidence cũ và dirty ngoài pha được giữ nguyên.

**DONE:** source/import/build checks, F1 contract, fail-closed metadata và handoff evidence.

**PARTIAL:** source-level instance/LOD evidence; chưa có tối ưu runtime theo CPU/GPU.

**UNVERIFIED:** runtime/import readback, ba cảnh headed, renderer/scalability, stat/VRAM/frame-time và 60 FPS.

**BLOCKED:** scene selector/headed entrypoint còn thiếu; `git lfs fsck` exit `1` chặn C1 delivery.

### Prompt pha tiếp theo

```text
F1 follow-up — cung cấp headed scene selector hoặc entrypoint hỗ trợ {scene} cho
 downtown_traffic, interior_alley và coast_streaming. Chạy lại mỗi cảnh khoảng
 10 giây, thu resolution/internal scale, renderer/scalability, stat unit, stat gpu,
 stat sceneRendering, stat initviews, stat levels, CPU/GPU frame-time và VRAM.
 Giữ nguyên runner fail-closed, không NullRHI/offscreen, không sửa Unreal dirty files,
 chỉ claim 60 FPS khi có fresh headed frame-time. Sau đó xử lý LFS pointer errors
 riêng bằng owner repo, không rewrite hoặc xóa Assets/CoastalUpgrade.
```

## F1 — Fresh headed evidence continuation (2026-10-16)

This continuation supersedes the earlier fail-closed selector-only note while
preserving all previous evidence. The new runs stayed within `Tools/F1/` and
`Saved/QA/F1/`; no Unreal Source, map, ExternalActors, or pre-existing dirty
file was changed.

### Ownership and runner correction

- The parser in `Tools/F1/SummarizeF1Evidence.py` was corrected so a document
  containing a `scenes` mapping is not also counted as a second scene record.
  The sanitized combined input now counts the exact fresh CSV rows instead of
  duplicating downtown samples.
- `Saved/QA/F1/20261016_0137_combined_sanitized/Summary.json` is the current
  combined report. `python Tools/F1/SummarizeF1Evidence.py
  Saved/QA/F1/20261016_0137_combined_sanitized` exited `1`, with
  `status=FAIL` and `fpsClaim=false`.
- The runner's `statUnit`, `statGpu`, `sceneRendering`, `initviews` and
  `levels` booleans record requested/log marker evidence. The fresh logs do not
  contain numeric stat panel readback; these fields are therefore not a
  numeric-stat PASS and remain UNVERIFIED for the requested readback gate.

### Fresh headed runs

| Scene | Selector and mode | Exit | Fresh samples | CPU ms mean/p95/max | GPU ms mean/p95/max | VRAM |
|---|---|---:|---:|---:|---:|---:|
| downtown_traffic | `ANANTA_City`, `CityObserveGraphics`, bounded close | 0 | 3615 | 5.606 / 7.505 / 70.758 | 5.812 / 6.305 / 12.487 | 7956 MB |
| interior_alley | `ANANTA_City`, `CityServiceCheck` proxy plus observer | 0 | 3281 | 5.247 / 7.867 / 70.194 | 6.337 / 7.084 / 18.705 | 7956 MB |
| coast_streaming | `ANANTA_CoastalCity`, `CoastalQA`, `CoastalHeroOnly` | 1 | 0 | unavailable | unavailable | 7956 MB |

All three requested `1280x720`, `ScreenPercentage=100`, DX12 and High
scalability. Downtown used a 75 second bounded headed observation and closed
gracefully after `CITY_GRAPHICS_OBSERVATION_WRITTEN samples=3615`. Interior
completed the service journey before the deadline and wrote
`CITY_GRAPHICS_OBSERVATION_WRITTEN samples=3281`; it is a service-journey map
proxy, not proof of a fixed interior/alley camera. Coast loaded headed with
D3D12 and completed its hero QA path, but `CoastalGameMode` does not create the
city graphics observer and `CoastalHeroOnly` excludes the measure views, so no
fresh CPU/render/GPU sample exists.

The fresh frame CSVs also record render-thread values: downtown
`8.675/10.529/43.476 ms` mean/p95/max and interior `7.585/10.120/95.608 ms`.
The combined report has no console error entries. The logs confirm the chosen
NVIDIA RTX 4060 Laptop GPU, 7956 MB dedicated memory, WorldPartition and
ContentStreaming markers, and a texture pool that starts at 4528 MB and is
reported at 3000 MB after content streaming. The `ExecCmds` line requested
`stat unit`, `stat gpu`, `stat sceneRendering`, `stat initviews` and
`stat levels`, but the log only shows the stat command help (`Empty stat
command!`); no numeric panel readback is claimed.

### Evidence classification

**DONE:** fresh headed downtown and interior CPU/render/GPU capture; truthful
resolution, internal scale, renderer, scalability and VRAM metadata; corrected
scene-record parser; source HISM/reuse/LOD checks; build and foundation checks;
preservation of existing dirty files and old evidence.

**PARTIAL:** downtown GPU distribution is within 16.667 ms at p95 and max, but
interior has a fresh 18.705 ms GPU max. CPU startup spikes reach about 70 ms
and render-thread spikes reach 43.476 ms downtown and 95.608 ms interior. The
source audit supports keeping existing HISM/reuse/LOD choices; it does not
provide enough evidence to change HLOD/Nanite, culling, material complexity,
shadow overlap, texture pool, foliage/Niagara or water draw cost.

**UNVERIFIED:** coast headed frame-time, numeric stat readback for all five
requested stat groups, equal fixed cameras across all scenes, native coastal
observer integration, and a three-scene 60 FPS gate. No FPS claim is made.

**BLOCKED:** F1 acceptance and C1 delivery remain blocked by the missing
coastal measure-only headed observer and the repository's pre-existing
`git lfs fsck` exit `1` (`unexpectedGitObject` under `Assets/CoastalUpgrade/`).
No stage, commit or push was performed.

### New verification evidence

- PowerShell AST parse of `Tools/F1/HeadedF1Probe.ps1`: exit `0`.
- `python -m py_compile Tools/F1/SummarizeF1Evidence.py`: exit `0`.
- `Validate-ANANTA.ps1`: exit `0`.
- `VerifyCityPerformanceBudget.py`: exit `0`, `status=PASS`,
  `sourceOnly=true`, `runtimeFpsVerified=false`, 90,415 groups,
  1,667,907 instances, 148 signatures, reusable fraction `0.999911`,
  95 mesh manifest entries, no invalid LOD recommendations.
- `VerifyCityInstanceReuse.py`: exit `0`, 1,667,759 reusable instances.
- `Build-ANANTA.ps1 -MaxParallelActions 2`: exit `0`, target up to date.
- `git diff --check`: exit `0` with only existing line-ending warnings.
- `git lfs fsck`: exit `1`, pre-existing pointer errors listed above.
- `git ls-remote origin refs/heads/main`: exit `0`, remote remains
  `5268d9a15649fd5ad59e5bc5d6878131834ddacf`.

### Prompt W1/F1 follow-up

```text
F1 follow-up — add a bounded headed coastal measure-only entrypoint or observer
for coast_streaming, then rerun downtown_traffic, interior_alley and
coast_streaming with the same camera contract. Capture numeric stat unit, stat
gpu, stat sceneRendering, stat initviews and stat levels readback. Keep DX12,
headed mode and fresh CPU/GPU/VRAM samples; do not use NullRHI, config, build or
source-only evidence for an FPS claim. Keep Unreal dirty files untouched and
handle the pre-existing LFS pointer errors with the repository owner.
```

## A3 — Hero art repair và visual QA (2026-10-16)

### Phạm vi và ownership

Lượt A3 xử lý một tranche hero giới hạn gồm 17 asset: tám phương tiện/transit,
năm hạ tầng đường phố, một cây, một monument, một factory prop và một venue
shell. Chỉ các file mới dưới `Tools/A3/` và evidence dưới
`Saved/QA/A3ArtRepair/` được tạo hoặc sửa trong pha này. `Assets/CoastalUpgrade`
được đọc làm nguồn nhưng không ghi đè; không sửa Unreal Source, map,
ExternalActors hay các file dirty có sẵn.

`Tools/A3/RepairConfig.py` giữ anime/stylized identity của Citizen và toy assets
ngoài tranche. `Tools/A3/RepairArtAssets.py` áp dụng smooth shading, bevel có
giới hạn theo góc, normals recalculation cho OperaShells, material Principled PBR
và texture reuse theo SHA-256. Base color blend đã được chỉnh để map A1 chỉ tạo
biến thiên bề mặt, không làm mất màu nhận diện xe và hạ tầng.

### Evidence mới

- `python -m py_compile Tools/A3/RepairConfig.py Tools/A3/RepairArtAssets.py
  Tools/A3/ReviewArtRepair.py Tools/A3/ValidateArtRepair.py` — exit `0`.
- Blender 4.5.1 repair command với `--factory-startup --python-exit-code 1`,
  output `Saved/QA/A3ArtRepair/CoastalModels_A3_Hero_v5.blend` và manifest
  `a3-art-repair-v5.json` — exit `0`; marker
  `A3_ART_REPAIR_OK {"objects":17,"missing":[],"materials":17}`.
- Blender 4.5.1 review command trên v5 blend, output `ReviewsV6` và
  `a3-art-review-v6.json` — exit `0`; marker
  `A3_ART_REVIEW_OK {"objects":17,"modelViews":136,"placementViews":85,"missing":[]}`.
- Render review ghi tám azimuth cho mỗi object và năm placement labels từ
  transformed bounds (`matrix_world`, scale → yaw → translation). Đã mở kiểm tra
  ảnh mới của PoliceCar, FireEngine, TrafficLight, StreetSign, ParkTree và
  OperaShells; chữ debug không còn dính vào xe/đèn. FireEngine có màu đỏ nhận
  diện, TrafficLight có bulb đỏ/vàng/xanh phát sáng, StreetSign có nhãn ANANTA.
- `python Tools/A3/ValidateArtRepair.py
  Saved/QA/A3ArtRepair/a3-art-repair-v5.json
  Saved/QA/A3ArtRepair/a3-art-review-v6.json` — exit `0`; marker
  `A3_ART_VALIDATION_OK {"objects":17,"modelViews":136,"placementViews":85}`.

### Phân loại gate

**DONE:** tạo tranche A3 có kế hoạch riêng; material/texture repair có hash và
reuse record; 17 object không thiếu; 136 ảnh review 8 hướng; 85 mục review
placement 5 góc; validator mới exit `0`; source blend không bị ghi đè.

**PARTIAL:** đây là hero tranche, chưa phải sửa toàn bộ 72 mesh hoặc toàn map.
ParkTree, Monument và OperaShells đã có silhouette/material repair nhưng vẫn
còn low-poly hoặc cần authored detail để đạt visual AAA; PoliceCar/other
vehicles đã có màu PBR và bevel nhưng chưa có native wheel/window/light-bar
readback. Texture licence trong source chưa khai báo nên provenance chỉ ghi
`not declared in source repository`.

**UNVERIFIED:** import/readback và placement trong Unreal; interaction/persistence
của venue; camera ngang tầm người trong map; 60 FPS hoặc GPU cost; chất lượng
AAA của các asset còn lại; native collision/LOD sau import. Render headless không
được dùng để claim runtime PASS.

**BLOCKED:** không có blocker cho artifact A3. Gate delivery vẫn bị chặn bởi
F1 chưa có coast frame-time/stat readback và `git lfs fsck` exit `1` với
`unexpectedGitObject` có sẵn dưới `Assets/CoastalUpgrade`; không stage, commit
hoặc push A3 trong trạng thái này.

### Prompt pha tiếp theo

```text
A3 tranche tiếp theo — review headed street/civic và native import/readback cho
hero assets v5. Giữ source/Unreal dirty nguyên trạng; mở rộng lần lượt buildings,
station/airport, waterfront rồi interiors. Mỗi venue phải ghi enterable +
interactive, enterable + static dressing hoặc shell-only. Giữ review 8 hướng,
placement 5 góc từ transformed bounds, provenance/licence/LOD/collision và không
claim AAA, interaction native hoặc 60 FPS khi chưa có evidence tương ứng.
```

### Cross-phase checks after A3

- `Validate-ANANTA.ps1` — exit `0`.
- `VerifyCityPerformanceBudget.py` — exit `0`, `status=PASS`,
  `sourceOnly=true`, `runtimeFpsVerified=false`, 90,415 groups,
  1,667,907 instances, 148 signatures, reusable fraction `0.999911`.
- `VerifyCityInstanceReuse.py` — exit `0`, 1,667,759 reusable instances.
- `Build-ANANTA.ps1 -MaxParallelActions 2` — exit `0`, target up to date.
- `git diff --check` — exit `0`, only existing LF→CRLF warnings on docs.
- `git ls-remote origin refs/heads/main` — exit `0`, remote remains
  `5268d9a15649fd5ad59e5bc5d6878131834ddacf`.
- `git lfs fsck` — exit `1` with pre-existing `unexpectedGitObject` entries
  under `Assets/CoastalUpgrade`; no LFS repair or asset deletion was attempted.
- No stage, commit or push was performed because F1/C1 delivery gates remain
  red; dirty Unreal/source files were preserved.

## A3B — Hero fidelity detail pass (2026-10-16)

### Ownership and scope

A3B tạo trong `Tools/A3B/` và `Saved/QA/A3BArtRepair/`, đọc A3 v5 làm nguồn
nhưng không ghi đè `Assets/CoastalUpgrade`, Unreal Source, map hoặc
ExternalActors. Các chi tiết mới nằm trong collection `A3B_DetailParts` và có
tag `a3b_owned` để rerun/cleanup chỉ chạm dữ liệu do pha này tạo.

### Fresh evidence

- `python -m py_compile Tools/A3B/*.py` — exit `0`.
- Builder Blender 4.5.1 với `--factory-startup --python-exit-code 1`, output
  `CoastalModels_A3B_HeroDetail_v4.blend` — exit `0`; marker
  `A3B_HERO_DETAIL_OK {"objects":13,"parts":70,"missing":[]}`.
- Review Blender V4 — exit `0`; marker
  `A3B_ART_REVIEW_OK {"objects":13,"modelViews":104,"placementViews":65,"missing":[]}`.
- `ValidateHeroDetail.py` trên manifest v4 — exit `0`; marker
  `A3B_VALIDATION_OK {"objects":13,"modelViews":104,"placementViews":65}`.
- `Tools/Build/Validate-ANANTA.ps1` chạy qua PowerShell process — exit `0`;
  bridge/workflow/plugin/file foundation checks đều pass.
- `Tools/Build/Build-ANANTA.ps1 -MaxParallelActions 2` — process exit `0`,
  `ANANTAEditor Development` up to date. Đây là source/build evidence, không
  phải runtime visual hoặc FPS evidence.
- `git diff --check` — exit `0`; `git ls-remote origin refs/heads/main` — exit
  `0`, remote vẫn ở `5268d9a15649fd5ad59e5bc5d6878131834ddacf`.
- `git lfs fsck` — exit `1`, lặp lại các `pointer: unexpectedGitObject` có sẵn
  trong `Assets/CoastalUpgrade/*`; không sửa, xóa hoặc rewrite LFS.
- Đã mở ảnh mới của PoliceCar, FireEngine, TrafficLight, StreetSign,
  CivilAirplane, ParkTree, Monument và OperaShells trong ReviewsV4. Bánh/kính/
  lightbar/visor/plaque đã xuất hiện; CivilAirplane không còn stripe nổi ngoài
  model. ParkTree có sáu foliage cluster và nhánh, OperaShells có facade glass/
  ribs ở phía trước nhưng vẫn còn phẳng/tối.

### Classification

**DONE:** A3B detail builder, collection ownership, 70 chi tiết hình học,
104 review 8 hướng, 65 review placement 5 góc từ bounds target + children,
manifest/validator và plan/contract.

**PARTIAL:** ParkTree vẫn còn silhouette tròn; OperaShells và Monument vẫn
cần authored geometry/material detail để đạt visual AAA; review là headless
fixture, chưa phải camera ngang tầm người trong map.

**UNVERIFIED:** native Unreal import/readback, collision/LOD sau import,
venue interaction/persistence, toàn bộ models/areas còn lại và 60 FPS.

**BLOCKED:** A3B artifact không bị block. Delivery vẫn bị chặn bởi F1 coast
measure/stat evidence còn thiếu và `git lfs fsck` pre-existing exit `1` dưới
`Assets/CoastalUpgrade`; không stage, commit hoặc push.

### Prompt pha tiếp theo

```text
A3C — authored foliage/venue geometry và fixture street/transit/waterfront.
Giữ A3B v4 làm evidence, review 8 hướng + 5 placement góc, kiểm tra camera
ngang tầm người. Ghi rõ venue enterable + interactive, enterable + static
dressing hoặc shell-only; không claim native/AAA/60 FPS thiếu headed evidence.
```

## A3C — Authored foliage, venue và street-detail pass (2026-10-16)

### Ownership và phạm vi

A3C nằm riêng trong `Tools/A3C/`, đọc `CoastalModels_A3B_HeroDetail_v4.blend`
nhưng không ghi đè A3B, `Assets/`, Unreal Source, map hoặc ExternalActors. Output
blend, manifest và 65 ảnh review nằm trong `Tools/A3C/output/`. Detail mới có tag
`a3c_owned` và collection `A3C_AuthoredDetail`.

### Fresh evidence

- `python -m py_compile Tools/A3C/*.py` — exit `0`.
- Blender 4.5.1 builder — exit `0`; marker
  `A3C_AUTHORED_DETAIL_OK {"objects":5,"parts":45,"missing":[]}`.
- Blender review — exit `0`; marker
  `A3C_ART_REVIEW_OK {"objects":5,"modelViews":40,"placementViews":25,"missing":[]}`.
- `ValidateAuthoredDetail.py` — exit `0`; marker
  `A3C_VALIDATION_OK {"objects":5,"modelViews":40,"placementViews":25}`.
- `Validate-ANANTA.ps1` — exit `0`; `Build-ANANTA.ps1 -MaxParallelActions 2`
  — exit `0`; `git diff --check` — exit `0`.
- Visual readback mới: ParkTree đã dùng cụm tán bất đối xứng; Monument có bệ,
  cột và vật liệu stone; OperaShells có facade hai trục, cửa kính và chữ OPERA;
  TrafficLight có LED lens; StreetSign có reflective edge.

### Classification

**DONE:** kế hoạch A3C, authored geometry cho 5 asset, material surface riêng
trong artifact, review đủ 8 hướng và 5 góc transformed bounds, validator và
fresh source/build gates.

**PARTIAL:** ParkTree vẫn là foliage fixture có stylization; OperaShells còn
phụ thuộc shell gốc và neutral-light review hơi tối; Monument chưa đạt hero AAA.
Chưa mở rộng toàn map hoặc toàn bộ nhóm phương tiện/venue.

**UNVERIFIED:** native Unreal import/readback, LOD/collision, camera ngang tầm
người trong map, venue interaction/persistence, headed GPU/VRAM/frame-time và
60 FPS. Headless Blender không thay thế các gate này.

**BLOCKED:** broader delivery vẫn chờ F1 headed evidence và lỗi `git lfs fsck`
  pre-existing dưới `Assets/CoastalUpgrade/*`; không stage, commit hoặc push.

## A3D — Vehicle và transit fidelity pass (2026-10-16)

### Ownership và phạm vi

A3D nằm riêng trong `Tools/A3D/`, đọc artifact A3C nhưng không ghi đè A3C,
`Assets/`, Unreal Source, map hoặc ExternalActors. Output blend, manifest và
ảnh review nằm trong `Tools/A3D/output/`; detail mới có tag `a3d_owned` và
collection `A3D_VehicleDetail`.

### Fresh evidence

- `python -m py_compile Tools/A3D/*.py` — exit `0`.
- Blender 4.5.1 builder — exit `0`; marker
  `A3D_VEHICLE_DETAIL_OK {"objects":8,"parts":65,"missing":[]}`.
- Blender review — exit `0`; marker
  `A3D_ART_REVIEW_OK {"objects":8,"modelViews":64,"placementViews":40,"missing":[]}`.
- `ValidateVehicleDetail.py` — exit `0`; marker
  `A3D_VALIDATION_OK {"objects":8,"modelViews":64,"placementViews":40}`.
- `Validate-ANANTA.ps1` — exit `0`; `Build-ANANTA.ps1 -MaxParallelActions 2`
  — exit `0`; `git diff --check` — exit `0`.
- Visual readback mới: xe cứu hộ có grille/headlamp/tail lamp/mirror/door seam;
  Train có door/bogie/front lamp; CivilAirplane có cabin windows/engines/tail;
  Helicopter có mast/blades/skids/tail rotor; AirportCart có seats/canopy/
  steering wheel; Rowboat có gunwale/oars/oarlocks/bow cleat.

### Classification

**DONE:** vehicle/transit authored detail tranche, material surface riêng,
review đủ 8 hướng và 5 góc transformed bounds, validator và fresh build/source
evidence.

**PARTIAL:** CivilAirplane và Helicopter vẫn là bounded headless fixture; neutral
review không thay thế authored cockpit/interior hoặc Unreal lighting; chưa xử lý
toàn bộ phương tiện và khu vực trong city.

**UNVERIFIED:** native Unreal import/readback, collision/LOD, traffic behavior,
vehicle interaction, camera ngang tầm người, headed GPU/VRAM/frame-time và 60
FPS. Không dùng build/config/NullRHI để kết luận performance.

**BLOCKED:** F1 vẫn thiếu headed stat/frame-time và `git lfs fsck` pre-existing
exit `1` dưới `Assets/CoastalUpgrade/*`; không stage, commit hoặc push A3D.


## A4 — Street, civic và industrial fidelity tranche (2026-10-16)

### Ownership và phạm vi

A4 nằm riêng trong `Tools/A4/`, đọc artifact A3D và không ghi đè source FBX,
`Assets/`, Unreal Source, map, ExternalActors hoặc file dirty có sẵn. Tranche xử lý
`StreetLamp`, `Railing`, `ParkBench`, `StreetBin`, `ParkingMeter`, `TrafficCone`,
`FireHydrant`, `FactoryBarrel`, `FactoryCrate`, `FactoryConveyor` và
`FactoryControl`. Output blend, manifest và review nằm trong `Tools/A4/output/`;
object detail có tag `a4_owned` và collection `A4_StreetCivicDetail`.

### Fresh evidence

- `python -m py_compile Tools/A4/BuildStreetCivic.py Tools/A4/ReviewStreetCivic.py
  Tools/A4/ValidateStreetCivic.py` — exit `0`.
- Blender 4.5.1 builder — exit `0`; marker
  `A4_STREET_CIVIC_BUILD_OK {"objects":11,"parts":59,"missing":[]}`.
- Blender review — exit `0`; marker
  `A4_ART_REVIEW_OK {"objects":11,"modelViews":88,"placementViews":55,"missing":[]}`.
- `ValidateStreetCivic.py` — exit `0`; schema, target list, material reuse policy,
  transformed-bounds order và toàn bộ render paths đạt.
- Save/reopen readback — exit `0`; marker
  `A4_REOPEN_OK {collection:true,ownedParts:59,targets:11,materialKeys:11}`.
- Visual check mới đã mở các ảnh StreetLamp, ParkBench, FactoryConveyor,
  FactoryControl, TrafficCone, FireHydrant, FactoryBarrel, FactoryCrate,
  ParkingMeter và Railing sau material pass. Authored detail đọc được; cone/hydrant
  vẫn là safety-painted low-poly fixture, chưa gọi là AAA.
- Material family A4 dùng shared procedural PBR, không sinh raster texture trùng;
  target material được gán lại trong artifact A4 để loại màu toy-like của source.

### Classification

**DONE:** bounded A4 authored geometry, shared material family, ownership sau
save/reopen, review đủ 8 hướng + 5 placement views và validator.

**PARTIAL:** headless neutral render đã cải thiện readability nhưng chưa phải
AAA visual acceptance; cone/hydrant/barrel/crate còn cần review trong lighting
ngang tầm người và context đường phố/factory.

**UNVERIFIED:** native Unreal import/readback, LOD, collision, interaction hoặc
static-dressing classification trong map, camera hero ngang tầm người, headed
GPU/VRAM/frame-time và 60 FPS.

**BLOCKED:** không có blocker cho A4 source tranche; native apply vẫn giữ ngoài
phạm vi vì dirty Unreal boundary và F1 headed evidence chưa đạt. Không stage,
commit hoặc push A4 khi gate native/performance chưa đạt.


### A4 fresh repository checks (2026-10-16)

- `Tools/Build/Validate-ANANTA.ps1` — exit `0`; foundation validation passed,
  BridgeDescriptor/WorkflowConfig true và không thiếu plugin/file.
- `Tools/Build/Build-ANANTA.ps1 -MaxParallelActions 2` — exit `0`; ANANTA build
  completed, target up to date. Warning chỉ là compiler version mới hơn preferred.
- `git diff --check` — exit `0`; chỉ cảnh báo line-ending LF/CRLF của hai Docs.
- `git lfs fsck` — exit `1`; lặp lại `unexpectedGitObject` pre-existing trong
  `Assets/CoastalUpgrade/*` của tree `5268d9a15649fd5ad59e5bc5d6878131834ddacf`.
  Không sửa, fetch lại, rewrite hoặc xóa object.
- Vì A4 chưa có native Unreal import/interaction/performance gate và LFS fsck vẫn
  lỗi sẵn, không stage/commit/push ở lượt này.


## A5 — Interior và venue prop fidelity tranche (2026-10-16)

### Ownership và phạm vi

A5 nằm riêng trong `Tools/A5/`, đọc artifact A4 và không ghi đè source FBX,
`Assets/`, Unreal Source, map, ExternalActors hoặc file dirty có sẵn. Tranche xử lý
`Sofa`, `Table`, `Chair`, `Bed`, `KitchenCounter`, `Stove`, `Fridge`,
`ArcadeCabinet`, `Door`, `Bookshelf`, `FloorLamp` và `TVConsole`. Output blend,
manifest và ảnh review nằm trong `Tools/A5/output/`; detail có tag `a5_owned` và
collection `A5_InteriorVenueDetail`.

### Fresh evidence

- `python -m py_compile Tools/A5/BuildInteriorVenue.py Tools/A5/ReviewInteriorVenue.py
  Tools/A5/ValidateInteriorVenue.py` — exit `0`.
- Blender 4.5.1 builder — exit `0`; marker
  `A5_INTERIOR_VENUE_BUILD_OK {"objects":12,"parts":61,"missing":[]}`.
- Blender review — exit `0`; marker
  `A5_ART_REVIEW_OK {"objects":12,"modelViews":96,"placementViews":60,"missing":[]}`.
- `ValidateInteriorVenue.py` — exit `0`; schema, material reuse, interaction
  classification, transformed-bounds order và toàn bộ render paths đạt.
- Save/reopen readback — exit `0`; marker
  `A5_REOPEN_OK {collection:true,ownedParts:61,targets:12,materialKeys:12,staticDressing:12}`.
- Visual check mới đã mở sofa cushions/arms/legs, kitchen backsplash/sink/faucet,
  arcade screen/control deck, door panels/handle, bookshelf shelves/books và
  floor lamp stem/shade/bulb.
- Mọi asset trong fixture ghi rõ `static dressing (native interaction pending)`;
  không gọi actor tồn tại là interactive.

### Classification

**DONE:** bounded A5 authored geometry, shared procedural PBR material family,
ownership sau save/reopen, review đủ 8 hướng + 5 placement views và validator.

**PARTIAL:** neutral headless review đã cải thiện readability nhưng chưa chứng minh
AAA interior/venue lighting; kitchen/door/TV cần camera ngang tầm người trong map.

**UNVERIFIED:** native Unreal import/readback, LOD, collision, enterable venue state,
interaction/persistence, camera hero, headed GPU/VRAM/frame-time và 60 FPS.

**BLOCKED:** native apply vẫn ngoài dirty Unreal boundary; không stage, commit hoặc
push A5 cho tới khi native interaction/performance gate đạt.


### A5 fresh repository checks (2026-10-16)

- `Tools/Build/Validate-ANANTA.ps1` — exit `0`; foundation validation passed,
  BridgeDescriptor/WorkflowConfig true và không thiếu plugin/file.
- `Tools/Build/Build-ANANTA.ps1 -MaxParallelActions 2` — exit `0`; ANANTA build
  completed, target up to date. Đây là source/build receipt, không phải FPS proof.
- `git diff --check` — exit `0`; chỉ warning line-ending LF/CRLF của Docs.
- `git lfs fsck` — exit `1`; lặp lại `unexpectedGitObject` pre-existing trong
  `Assets/CoastalUpgrade/*` của tree `5268d9a15649fd5ad59e5bc5d6878131834ddacf`;
  không sửa, rewrite hoặc xóa object.
- A5 vẫn không stage/commit/push vì native import/interaction/performance chưa đạt.

## R0 — Rebaseline current checkout, 2026-10-20

Baseline: main `9b295109e280752bd3d1ff7640be3bad02f6dc1e`, remote main equal.
Required documents were read before implementation. AGENTS, roadmap and handoff
hashes match the earlier full reads; other required art/coastal/rebuild documents
were read again. `git diff -- Source Content Config ANANTA.uproject` is empty.
No current Unreal dirty file was edited, reset, saved or staged. Committed
Coastal interaction/transit code is not a pending worktree diff and not fresh
runtime proof. P4A/P4B are PARTIAL for the current continuation.

Ownership was written to `Tools/Continuation_20261020/ownership.json` before
implementation. AGENTS.md and previous untracked A1–A6/F1/W3/ArchitectureAudit
remain outside this phase commit. Two existing Docs diffs were reviewed as
historical notes and are preserved with current R0 additions. No old runtime,
Blender or build result is relabeled a new PASS.

R0 decisions: P2 remains bounded visual/history, not AAA art; W1/W2 browser water
is the next priority; target 60 FPS = 16.667 ms supersedes legacy 90 FPS UI/config
notes as acceptance target. Runtime and short headed F1 measurements requested
now are authorized; no long benchmark/soak. Source/build/NullRHI are narrower.

### W1 continuation prompt

Use the existing Prototypes/ThreeWater checkout and pinned dependency lockfile.
Fix camera/spec parity, verify same-wave analytic normals and boundary margins,
run check/build/spec gates, then HTTP browser smoke with fresh t0/t1 views,
orbit/free controls, foam/boundary toggles and coast/beach_boat/offshore reports
at 10 seconds each. Save fresh evidence before W3. Keep Unreal unchanged during
W1/W2. Only after their browser gate may the exact wave contract be ported to an
owned Unreal material-function asset, with separate boundary/readback/camera gates.
Do not expand the map before hero art acceptance or claim 60 FPS before F1.

Current execution contract: `Tools/Continuation_20261020/CONTRACT.md`.
R0 commit/push receipt will be captured by Git and the next phase handoff entry.

## W1/W2 — Fresh prototype acceptance, 2026-10-20

R0 delivery: commit `2a481d89b4222cafa965821d7c3ec41180fc1f71` on main,
push successful, git ls-remote matched. Existing AGENTS/art/F1/W3/audit dirt
was preserved outside the commit. No Unreal worktree changes.

New fixes: ScenePresets beach_boat target X now equals the pinned spec (-42).
CoastBoundary honors explicit box even with interchange polygon present, and
main forwards type/boatMargin. A new independent regression checker originally
failed eight corner-margin cases; after correction all 68 pass, including
finite-difference normals, camera parity and edge/corner margins. A negative
camera case is rejected. Syntax, build and canonical spec validator exit 0.

Fresh browser HTTP URL `http://127.0.0.1:4178/?run=20261020-W2` completed exactly
three automatic 10-second scenes. Avg/p95/max ms: coast 6.06/7.30/135.50 with
one startup outlier; beach_boat 6.08/6.90/15.80; offshore 6.06/6.20/7.20.
No console warnings/errors. Manual orbit drag, free/orbit toggle, scene keys,
boundary/foam off/on were observed working. Draw calls changed 7 -> 5 when
both overlays were off; geometry count stayed seven. Fresh coast/orbit PNGs
show continuous water/foam in the reviewed views. Manual checks are separate
from the automatic performance samples; no long soak or GPU benchmark run.

Evidence: `Tools/Continuation_20261020/W2_math.json`, `W2_browser.json`,
`W2_coast.png`, `W2_orbit.png`. Browser numbers do not imply Unreal 60 FPS.
The wave-spec hash and four exact tuples are unchanged. W1/W2 gate now permits
W3 native port work; it does not accept W3 or full-map AAA/native gameplay.

R0 validation/diff check exit 0. Full git lfs fsck exit 1 with 88 pre-existing
unexpectedGitObject records under Assets/CoastalUpgrade. Full list preserved
in R0_gates.json; no LFS object rewritten or deleted.

Next: consume water_contract.py to create an owned MF_AnantaWater/material
graph using world centimetres -> metres, exact wave tuples and analytic normals.
Read back all four outputs; boundary collision stays separate; capture the
same three spec cameras before applying beyond the bounded water slice.
V1 hero art, native A1/A2, S1 streaming, G1 actors/persistence and F1 remain
pending; do not claim them from source or historical fixture receipts.

## W2 visual refinement continuation — 2026-10-20

The next water pass follows the primary GPU Gems comparison: a small geometric
wave field establishes readable shape, while detail normals and view-angle
response carry the fine surface impression. Three.js `Water2` was reviewed as a
reference for reflection/refraction and flow-map quality, but its extra render
targets are outside the low preset budget.

The prototype now uses four analytic Gerstner-like waves on the existing fixed
plane. Lateral crest displacement, tangent-derived normals, two procedural
detail slopes, Fresnel, a restrained specular term, deep/shallow color, crest
foam and shoreline foam are all shader-side. The original W3 wave tuples,
phase formula, units, axes and SHA-256 remain unchanged. The boat fixture uses
a stable base point and the same displaced sample each frame, then clamps the
result to the boat boundary margin.

Fresh source/contract/build checks pass with 69 contract checks. HTTP delivery
from Vite returned 200 for the page, entry module and wave spec. Browser
screenshot and console smoke are UNVERIFIED because browser automation is
disabled in this Work environment; no headed visual or 60 FPS claim is made.

Follow-up fix: the completed three-scene quick QA previously set the global
simulation to paused, which made the water appear frozen after 30 seconds. The
fix leaves `elapsed`, `water.update` and boat bobbing live after QA completes;
only automatic scene advance stops. The status now reports `water animation
live`, so the prototype remains an animated demo after its reports are ready.

The Unreal port remains gated on the pinned contract and a later same-camera
material readback. Do not add the visual steepness defaults to the Unreal
parameter list without an explicit contract revision and a new hash.

## F1 fresh three-scene observer receipt — 2026-10-20

Commit `43584e3bd91a20efb9396ca41db9d07f7502b83e` is on `main` and matches
`origin/main`. It makes `CityObserveGraphics` sufficient to create the observer,
records map and QA slot in `RenderConfig.txt`, snapshots `FrameTimes.csv` every
120 samples, and still flushes on engine pre-exit/deinitialization. The patch
was built with `Build-ANANTA.ps1 -MaxParallelActions 2` and the build exited 0.

Fresh `HeadedF1Probe.ps1` runs used DX12, High scalability, 1280x720,
internal scale 1 and non-NullRHI `UnrealEditor-Cmd.exe`:

| Scene | Run | Rows | CPU p95/max | Render p95/max | GPU p95/max | VRAM | Console errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `downtown_traffic` | `20261020_151359733_39278ff0` | 857 | 16.848 / 1431.773 ms | 10.670 / 1391.167 ms | 7.253 / 33.514 ms | 7956 MB | 0 |
| `interior_alley` | `20261020_151654176_781259c1` | 2583 | 16.562 / 187.198 ms | 10.879 / 194.941 ms | 6.823 / 30.923 ms | 7956 MB | 0 |
| `coast_streaming` | `20261020_150739259_07110863` | 1319 | 12.953 / 630.261 ms | 8.450 / 2980.685 ms | 5.041 / 35.982 ms | 7956 MB | 0 |

Each metadata file is runner `PASS` with fresh CPU/render/GPU samples,
WorldPartition and ContentStreaming markers, and a completed scene/QA path.
The authoritative artifacts are the matching `metadata.json` and
`captured_FrameTimes.csv` under `Saved/QA/F1/<runId>/`. The actual executable is
`UnrealEditor-Cmd.exe`; therefore this receipt proves a live DX12 runtime
observation and GPU counters, while human headed visual review and numeric stat
panel readback remain separate gates.

F1 classification is **PARTIAL**. GPU p95 is under the 16.667 ms reference in
all three scenes, but downtown wall p95 is 16.848 ms and large startup or
streaming maxima remain. No final 60 FPS claim is made. Numeric readback for
`stat unit`, `stat gpu`, `stat sceneRendering`, `stat initviews` and `stat levels`,
fixed camera parity, and a true headed visual review remain open.

The full objective is still open for W3 city material integration and same-camera
comparison, V1/A1/A2 native hero gates, S1 runtime streaming identity/cell
readback, G1 Coastal actor schedules/aircraft/rowing/rail/persistence, F1
optimization, and C1's pre-existing LFS `unexpectedGitObject` errors.
