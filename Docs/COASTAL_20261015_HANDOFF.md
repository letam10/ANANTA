# Coastal City — bàn giao ngày 15/10/2026

## Phạm vi lượt này

Tiếp tục nhánh `codex/coastal-interiors-20261014` của Unreal Engine 5.8.3.
Giữ nguyên thay đổi người dùng trong `AGENTS.md`; chỉ cập nhật nguồn Coastal,
cấu hình render, công cụ kiểm chứng và Docs thuộc lượt này.

## Đã thực hiện

- Thêm `Tools/Upgrade/AuditCoastalQuality.py`, audit engine-free cho manifest,
  hash FBX, 8 hướng/model, LOD/collision và review placement.
- Audit mới đạt: `COASTAL_QUALITY_OK manifest_models=55 review_units=36 warnings=0`.
  Bằng chứng có 55 model coverage/import, 23 building, 36 room review unit,
  180 view và 2 room coverage file tại `Saved/Upgrade/coastal-quality-report.json`.
- Sửa `Tools/Upgrade/coastal_scene.py`: cull distance được gom band 5 m,
  quy đổi đúng từ mét sang cm Unreal, fade 120%; không đổi placement, scale hay collision.
  Điều này giảm object nhỏ tồn tại quá xa do công thức cũ nhân 80/100 sai đơn vị.
- Sửa `Config/DefaultEngine.ini`: bỏ khóa trùng, giữ DX12/SM6, thêm TSR,
  tắt hardware ray tracing, giữ Lumen software/VSM, bật HZB/occlusion/instance culling.
  Comment cấu hình ghi rõ ngân sách mục tiêu 16.667 ms, chưa phải benchmark.

## Kiểm chứng mới

- `python -m py_compile Tools/Upgrade/AuditCoastalQuality.py`: PASS.
- `python Tools/Upgrade/AuditCoastalQuality.py --root .`: PASS, không warning.
- `git diff --check`: PASS.
- `Tools/Build/Build-ANANTA.ps1 -Configuration Development -MaxParallelActions 2`:
  PASS, UnrealBuildTool exit 0, thời gian 20.37 s.
- `Tools/Build/Validate-ANANTA.ps1`: PASS; plugin, workflow và file nền tảng đầy đủ.
- Quick gameplay headless dùng map CoastalCity với `-game -CoastalQA -NullRHI`:
  `Saved/Upgrade/runtime-r6-quick.log` ghi
  `COASTAL_QA_COMPLETE failures=0 views=122`.
  Các check spawn, 23 cửa, 23 dịch vụ, 23 NPC, 5 item, cửa từ phố,
  chặn biên biển, đi bộ, lên/lái/xuống xe, lên/chèo/xuống xuồng đều PASS.
  Đây là acceptance run bounded, không phải benchmark 60 FPS.

## Dọn file tạm

- Giữ `runtime-r6-quick.log`, `Saved/Upgrade/Runtime/2026.10.14-23.08.44`
  với `checks.csv`, `frames.csv`, `metadata.txt` làm bằng chứng.
- Không có PNG được tạo trong lượt NullRHI.
- Bytecode `AuditCoastalQuality` trong `Tools/Upgrade/__pycache__` là cache tạm
  cần xóa khi hệ thống cho phép; không xóa asset/model hay file của người dùng.

## Chưa hoàn tất và giới hạn bằng chứng

- Chưa đo headed 60 FPS, GPU p95, VRAM hoặc benchmark soak; cấu hình hiện chỉ là target.
- CoastalCity vẫn chưa chuyển sang World Partition/HLOD/Data Layers.
- NPC vẫn chưa có lịch sinh hoạt và phương tiện vẫn là kinematic; chưa có lái máy bay,
  hoạt ảnh chèo tay, minigame, kinh tế/save đầy đủ hoặc phản chiếu gương riêng.
- 55 model hiện có đã được kiểm 8 hướng và 36 unit phòng đã có 5 view/unit;
  chưa tạo thêm một tranche model mới trong lượt này vì các nhóm phố, transit,
  nội thất, venue và dịch vụ đã có trong bộ kit hiện tại.
- Ảnh editor Unreal/material lighting không được dùng làm bằng chứng mới trong lượt này;
  hình học Blender và runtime NullRHI không thay thế visual acceptance headed.

## Kế hoạch còn tồn đọng

1. Dọn cache đúng phạm vi và giữ lại log/checks cần thiết.
2. Tạo hero slice có World Partition/HLOD và đo streaming trước khi nhân rộng district.
3. Thêm material/lighting review headed riêng, sau đó đo ba view downtown, interior và traffic.
4. Mở rộng interaction data-driven cho đồ nhỏ, NPC schedule, transit và save state.
5. Chỉ tuyên bố đạt 60 FPS sau khi có log headed mới với preset và phần cứng ghi rõ.

## Evidence

- `Saved/Upgrade/coastal-quality-report.json`
- `Saved/Upgrade/runtime-r6-quick.log`
- `Saved/Upgrade/Runtime/2026.10.14-23.08.44/checks.csv`
- `Saved/Upgrade/Runtime/2026.10.14-23.08.44/frames.csv`
- `Docs/Evidence/Coastal20261014/model-review.jpg`
- `Docs/Evidence/Coastal20261014/rooms-five-views.jpg`

## Git

`AGENTS.md` đang dirty từ trước và không được stage. Chỉ stage nguồn/config/audit/Docs
thuộc lượt này; kiểm tra push bằng `git rev-parse HEAD` và `git ls-remote` sau commit.
