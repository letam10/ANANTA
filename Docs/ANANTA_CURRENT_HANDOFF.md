# ANANTA Current Handoff

Ngày cập nhật: 2026-10-15
Phase ID: P2 — Material graph và hero slice
Trạng thái: PASS — bounded P2 material và headed hero gate đạt; GPU tier/FPS chưa kiểm

## Checkout và dirty-state

- Checkout: `D:\GAME\ANANTA`
- Engine: Unreal Engine 5.8.3
- Branch: `main`
- Baseline remote sau sync: `479da5b044669c8a18f2f11084961791284db390`; current HEAD trước commit P2: `479da5b044669c8a18f2f11084961791284db390`
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
- P2 commit/push: chờ commit sau khi kiểm tra `git status`, chỉ stage file in-scope trên
  `main`; không stage `AGENTS.md`, không force-push.

## Prompt pha tiếp theo

```text
PHASE P2 — Hero slice, material graph và headed visual.

Đọc ANANTA_MASTER_ROADMAP.md và ANANTA_CURRENT_HANDOFF.md.
Baseline P1 đã đạt source/geometry gate; không sửa AGENTS.md, evidence cũ, map hoặc gameplay ngoài scope.
Chốt material graph/output readback và hero slice 200–300 m; headed capture chỉ chạy khi prompt cho phép.
Không claim visual/FPS từ Blender, static parse, build hoặc NullRHI; cập nhật hai Docs với evidence mới.
```
