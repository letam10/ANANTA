# Coastal City — bàn giao ngày 15/10/2026

## Phạm vi lượt này

Tiếp tục nhánh codex/coastal-interiors-20261014 của Unreal Engine 5.8.3.
Giữ nguyên thay đổi người dùng trong AGENTS.md; chỉ cập nhật nguồn Coastal,
asset sinh bởi bộ công cụ, công cụ kiểm chứng và Docs thuộc lượt này.

## Đã thực hiện

- Thêm Tools/Upgrade/coastal_micro_props.py với 10 prop low-poly có pivot nền:
  KitchenKnifeBlock, BathroomBin, BedroomClock, ToyBlocks, BarGlassRack,
  TrafficCone, FireHydrant, ParkingMeter, AirportCart và Lifebuoy.
- Nối 10 prop vào GenerateCoastalModels.py và đặt vào phòng ngủ, bếp, phòng tắm,
  phòng khách, cafe/bar/nhà hàng, sân bay, giao lộ, phố biển và bến thuyền.
- Cập nhật placement để prop nhỏ tắt collision khi không cần, giữ bounds assertion
  cho các đồ trong phòng, và không thay đổi hệ trục/đơn vị hiện có.
- Sinh lại bộ kit: 65 model FBX và CoastalModels.blend. Mỗi model có 8 hướng review.
- Import vào Unreal thành công 65 model; map commandlet dựng lại 23 building,
  6.947 placement và 969 HISM batch.
- Review hình học phòng đạt 180 view cho 36 review unit, tương ứng 5 view/unit.
- Cấu hình render đã có từ lượt trước: TSR, Lumen software, hardware ray tracing
  tắt, HZB/occlusion/instance culling bật; cull distance đã sửa từ mét sang cm Unreal.

## Kiểm chứng mới

- python -m py_compile trên GenerateCoastalModels.py, coastal_micro_props.py,
  coastal_home.py, coastal_rooms.py, coastal_landscape.py và coastal_transit.py:
  PASS.
- Blender 4.5.1: COASTAL_MODELS_OK 65 models; max triangles=9678; exit 0.
- ReviewModels.py: MODEL_VIEW_COVERAGE_OK 65 models x 8 views; exit 0.
- ComposeModelReviews.py: MODEL_REVIEWS_OK 65 models, 520 rendered views; exit 0.
- AuditCoastalQuality.py: COASTAL_QUALITY_OK manifest_models=65 review_units=36
  warnings=0; import_readback=65, layout_buildings=23, review_views=180.
- ImportCoastalModels.py commandlet với NullRHI: IMPORT_EXIT=0, Python script
  executed successfully, 0 import errors; có 1 cảnh báo UE-MCP Slate startup.
- BuildCoastalCity.py commandlet với NullRHI:
  COASTAL_MAP_OK 23 enterable buildings, 6947 instances / 969 HISM batches,
  map check 0 Error(s), 0 Warning(s); còn cảnh báo API deprecated của Unreal
  và UE-MCP Slate startup.
- ReviewRoomGeometry.py: ROOM_GEOMETRY_VIEWS_OK 180 views; đây là review hình học,
  không thay thế gameplay hoặc lighting acceptance.
- Quick gameplay bounded với map CoastalCity, -game -CoastalQA -NullRHI:
  runtime-r7-quick.log ghi COASTAL_QA_COMPLETE failures=0 views=122.
  Các check spawn, cửa, dịch vụ, NPC, item, chọn cửa từ phố, biên biển, đi bộ,
  lên/lái/xuống xe và lên/chèo/xuống xuồng đều đạt. Đây không phải benchmark 60 FPS.

## Dọn file tạm

- Đã dọn bytecode pyc sinh trong Tools/Upgrade/__pycache__ cho các script của lượt.
- Giữ log import/build/QA, manifest, city-layout, audit report, ảnh 8 hướng và
  room geometry để làm bằng chứng; không xóa asset/model hay file người dùng.
- AGENTS.md vẫn dirty từ trước và không được stage.

## Chưa hoàn tất và giới hạn bằng chứng

- Chưa có headed/player capture để xác nhận visual, material, collision cảm nhận,
  VRAM, GPU p95 hay 60 FPS; NullRHI chỉ xác nhận logic bounded.
- CoastalCity chưa chuyển sang World Partition/HLOD/Data Layers.
- NPC chưa có lịch sinh hoạt; xe/thuyền còn kinematic; chưa có lái máy bay,
  hoạt ảnh chèo tay, minigame, kinh tế/save đầy đủ hoặc phản chiếu gương riêng.
- Các building đã vào được theo harness nhưng chất liệu/ánh sáng và mật độ đô thị
  chưa đạt mức photoreal/AAA cho mọi camera.
- 5 view/unit hiện là review camera; chưa phải người chơi tự do kiểm từng phòng
  trên headed build.

## Kế hoạch còn tồn đọng

1. Tạo hero slice có World Partition/HLOD và đo streaming trước khi nhân rộng district.
2. Thêm material/lighting review headed, sau đó đo downtown, interior và traffic.
3. Mở rộng interaction data-driven cho đồ nhỏ, NPC schedule, transit và save state.
4. Chỉ tuyên bố đạt 60 FPS sau khi có log headed mới ghi preset, độ phân giải,
  phần cứng và frame-time percentile.

## Evidence

- Saved/Upgrade/coastal-quality-report.json
- Saved/Upgrade/runtime-r7-quick.log
- Saved/Upgrade/Runtime/2026.10.14-23.31.04/checks.csv
- Saved/Upgrade/Runtime/2026.10.14-23.31.04/frames.csv
- Saved/Upgrade/ModelViews/coverage.json và review-page-*.jpg
- Saved/Upgrade/RoomGeometry/20261014-232832
- Saved/Upgrade/import-coastal-65.log
- Saved/Upgrade/build-coastal-65.log

## Git

Đã ủy quyền commit/push cho nhánh codex/coastal-interiors-20261014.
AGENTS.md không được stage; sau khi kiểm tra status sẽ stage đúng nguồn, asset và
Docs của lượt này, rồi đối chiếu git rev-parse HEAD với git ls-remote origin.
