# ANANTA Current Handoff

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
  đổi profile directional/sky light. Capture headed 1280x720 đã chạy hai lần:\n+  Day folder `Saved/Upgrade/Runtime/2026.10.15-12.58.16` và BlueHour folder
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
