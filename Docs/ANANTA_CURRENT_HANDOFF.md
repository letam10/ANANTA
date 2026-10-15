# ANANTA Current Handoff

Ngày cập nhật: 2026-10-15
Phase ID: P0 — Baseline, Git và ngữ cảnh
Trạng thái: PASS cho P0 baseline/audit/docs; P1 chưa bắt đầu

## Checkout và dirty-state

- Checkout: `D:\GAME\ANANTA`
- Engine: Unreal Engine 5.8.3
- Branch: `codex/coastal-interiors-20261014`
- Local HEAD sau baseline sync: `9057c9beecd2ef1e1cc433eb4f672b9130343e79`
- Dirty file có sẵn: `AGENTS.md`; không sửa, stage, commit hoặc xóa.
- Hai Docs P0 là file mới do chat này tạo; không sửa gameplay, asset, map hoặc source.

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

## Phân loại

**DONE ở baseline local:** fast-forward baseline; foundation validation; 72 model
source/manifest và 8-view coverage; 36 unit/180 room geometry review; 23 building;
r15 bounded NullRHI logic; roadmap/handoff P0.

**PARTIAL:** material graph/output readback; visual headed; provenance/LOD/collision
được ghi ở tranche nhưng chưa có visual acceptance mới; evidence JSON chưa đồng nhất.

**UNVERIFIED:** headed visual/material, GPU/VRAM/frame-time percentile, 60 FPS,
World Partition, HLOD, Data Layers, PCG, aircraft control, rowing animation,
railway signal control, save/economy và AAA quality toàn map.

**BLOCKED:** không còn blocker baseline P0; headed visual/FPS và các pha nội dung vẫn
chưa đạt gate. P1 sẽ bắt đầu bằng audit source/readback/review.

## Evidence stale cần giữ nguyên

- `Saved/Upgrade/coastal-quality-report.json` có `manifest_models=65`; đây là
  report cũ, không dùng thay cho 72 model.
- `Saved/Upgrade/city-layout.json` có 195 review views; không dùng thay cho
  room geometry proof 180 views.
- Không xóa hoặc ghi đè các report cũ trong P0.

## File đã đổi và kiểm chứng sau khi ghi

- Đã tạo [ANANTA_MASTER_ROADMAP.md](ANANTA_MASTER_ROADMAP.md).
- Đã tạo [ANANTA_CURRENT_HANDOFF.md](ANANTA_CURRENT_HANDOFF.md).
- Không sửa `AGENTS.md`, map, ExternalActors, asset, C++ hoặc generator.
- Sau baseline sync đã chạy `& .\Tools\Build\Validate-ANANTA.ps1` (exit 0),
  `git diff --check` (exit 0, chỉ warning line-ending của `AGENTS.md`) và
  `git status --short --branch`.

## Commit và push

- P0 Docs commit: `927369f8bbc4fa5b0a1a5981fa1d927533e6bf3d` (`docs: establish ANANTA master roadmap and handoff`).
- Push hash: **chưa chạy**; không push trong chat này do policy `AGENTS.md`.
- P0 đã PASS về baseline/audit/docs; không claim headed visual/FPS.

## Prompt pha tiếp theo

```text
PHASE P1 — Asset and geometry pipeline.

Đọc ANANTA_MASTER_ROADMAP.md và ANANTA_CURRENT_HANDOFF.md.
Baseline đã đồng bộ ở 9057c9be..., không sửa AGENTS.md và không mở rộng toàn map.
Chạy audit source/generator/import-readback/review hiện có; ưu tiên đọc evidence
72 model, 8-view, 36 unit/180 placement. Nếu cần sửa, chốt contract trước,
chỉ sửa file thuộc P1, kiểm tra transformed bounds và không claim headed visual/FPS.
Cuối pha cập nhật hai Docs với lệnh, exit code, evidence mới, commit hash và
push hash; không push nếu AGENTS.md policy chưa cho phép.
```