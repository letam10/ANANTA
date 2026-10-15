# Nâng cấp thành phố ven biển — 2026-10-13

> Cập nhật 14/10/2026: xem [bàn giao mới](COASTAL_20261014_HANDOFF.md).
> Bộ kit hiện có 55 model; bản mới chưa chạy game/benchmark theo yêu cầu.
> Các kết quả runtime bên dưới chỉ thuộc bản ngày 13/10, không áp dụng cho bản mới.

## Phạm vi và trạng thái

Giữ Unreal Engine 5.8.3 và map gốc `ANANTA_Slice`. Bản nâng cấp được dựng trong
`ANANTA_CoastalCity`; nguồn và asset riêng nằm ở `Tools/Upgrade`,
`Source/ANANTA/*/Coastal*`, `Assets/CoastalUpgrade`, `/Game/ANANTA/CoastalUpgrade`.
Không publish, deploy hoặc push trong lượt này.

**Đã hoàn thành trong lượt:** tạo model riêng, kiểm model 8 hướng, dựng map ven biển,
kiểm tương tác headless và build C++ thành công. Chưa xác nhận 60 FPS headed hoặc kiểm
bố trí bằng người chơi ở đủ 5 góc.

## Đã thực hiện và bằng chứng

- 41 model Blender/FBX: xe cảnh sát, cứu hỏa, cứu thương, tàu, trực thăng, máy bay,
  thuyền, đồ đường phố, tượng, vòng quay, đồ nhà máy, nội thất, NPC và cây.
- 328 ảnh riêng: 41 model × 8 góc cách nhau 45°. Đã sửa các model có lỗi khoang,
  chậu rửa/bồn cầu, cánh máy bay, tâm nan vòng quay và bake rotation.
- Import readback: 41 model, kích thước mét → cm sai số dưới 0,1 cm, 3 LOD/model,
  một material/model và collision đơn giản; commandlet import exit 0.
- Map commandlet r9: `COASTAL_MAP_OK 23 enterable buildings, 5123 instances / 681 HISM batches`.
- `Validate-ANANTA.ps1`: exit 0. `Build-ANANTA.ps1 -MaxParallelActions 2`: exit 0;
  warning còn lại là `APawn::GetMovementBase` deprecated từ Engine.
- `ComposeModelReviews.py`: `MODEL_REVIEWS_OK 41 models, 328 rendered views`.
- CoastalQA r6: exit 0, `COASTAL_QA_COMPLETE failures=0 views=122`,
  `Saved/Upgrade/Runtime/2026.10.13-12.20.22`.
- CoastalQA đạt: player spawn, 10 điểm thang máy, 23 cửa, 23 dịch vụ, 23 NPC,
  5 pickup, chọn cửa từ phố, biên biển, đi bộ, vào/ra xe, xe chạy, lên/xuống thuyền,
  thuyền chạy.

## Thiết kế hiện có

- 23 venue vào được: cảnh sát, cứu hỏa, phòng khám, nhà máy/xưởng, nhà hàng, cafe,
  bar, rạp phim, arcade, khách sạn, căn hộ, tiệm trang điểm và nhà hát.
- Sàn 3,2 m; cửa 0,9 m trong lỗ 0,98 m; pivot cửa đặt ở bản lề.
- Lưới phố 64 m; đường 14 m = 4 làn × 3,5 m; vỉa hè 3 m; có đèn giao thông, bảng,
  lan can, công viên, khu chơi, highway, ga hai phía và ray hai chiều.
- Biển kéo dài sau vùng chơi, bãi cát dốc `atan(2/30)`, bến có hai thuyền; collision
  chặn rìa bản đồ. Nước dùng normal động opaque, không mô phỏng fluid.

## Tối ưu render/FPS

- HISM nhóm theo mesh/material và ô 64 m; actor tĩnh không tick.
- LOD giữ 100% / 50% / 20% tam giác; đồ nhỏ suy cull từ kích thước chiếu.
- Đồ nhỏ tắt collision/bóng/distance field khi không cần; xe chỉ tick khi có người lái.
- Lumen software, hardware ray tracing tắt, TSR 900p → 1080p = 83,33%, nước một pass.
- Ngân sách 60 FPS là `1000/60 = 16,667 ms`.
- R6 headless offscreen đo 5 camera: CPU p95 8,67–9,61 ms, GPU p95 5,54–6,10 ms.
  Có spike CPU 300–359 ms khi chụp/streaming; số này không phải bằng chứng 60 FPS
  headed. Cần một lượt benchmark headed/player có log mới trước khi chốt 60 FPS.

## Lỗi đã tìm và sửa

- `BindAxisKey(MouseX/MouseY)` assert `AxisKey.IsAxis1D()` trong UE 5.8: đổi sang
  mapping có tên `CoastLookYaw/CoastLookPitch` và `BindAxis`.
- Query thang máy tự tính cả bảng điều khiển và bảng đối diện: bỏ actor hiện tại,
  tắt collision riêng cho mesh `kind=4`, dời cặp bảng vào vùng trống `(x, y-8)`.
- Xe và thuyền bị block ngay frame đầu: giảm hộp collision theo chiều cao; r6 đã đạt
  `W_key_drives_vehicle`, `W_key_rows_boat`, hai lối xuống an toàn.
- Chọn tương tác dùng khoảng cách 3D để không chọn nhầm tầng; bản sửa này mới build
  thành công, chưa chạy lại CoastalQA sau thay đổi.

## Chưa làm được và kế hoạch còn lại

- Chưa có 5 góc kiểm bố trí trong player cho từng phòng; ảnh hiện tại là camera QA.
- Chưa có World Partition/HLOD/streaming district; tầng trên phần lớn là mặt dựng.
- Xe/thuyền còn kinematic; chưa có Chaos Vehicle, hoạt ảnh chèo, thủy lực hay lái bay.
- NPC mới hội thoại; chưa có AI đi lại/lịch sinh hoạt.
- Arcade/rạp phim/dịch vụ chưa có minigame, phim phát, kinh tế hoặc save ra đĩa.
- Nội thất và chất liệu còn đơn giản; ảnh overview cho thấy mật độ/kết nối đô thị chưa
  đạt mức photoreal/AAA.
- Cần lượt tiếp theo: chạy lại QA sau binding 3D mới, cải thiện material/lighting,
  tăng mật độ có kiểm soát, rồi mới làm benchmark headed/player và HLOD.

## Bằng chứng và lệnh

- `Saved/Upgrade/baseline-map.json`, `city-layout.json`, `import-readback.json`.
- `Saved/Upgrade/ModelViews/coverage.json`, `review-page-1.jpg` … `review-page-9.jpg`.
- `Saved/Upgrade/build-city-r9.log`, `build-interaction-final.log`, `runtime-r6.log`.
- Lệnh đã chạy: `Validate-ANANTA.ps1`, `Build-ANANTA.ps1 -MaxParallelActions 2`,
  `python Tools/Upgrade/ComposeModelReviews.py`, BuildCoastalCity commandlet và
  UnrealEditor-Cmd `-CoastalQA -RenderOffscreen`.

## Cập nhật 2026-10-15 — quality gate và render budget

- Đã thêm `Tools/Upgrade/AuditCoastalQuality.py` để kiểm tra độc lập manifest,
  8 hướng/model, 5 góc cho từng review unit, hash FBX, LOD và collision.
- Audit hiện tại đạt `COASTAL_QUALITY_OK manifest_models=55 review_units=36 warnings=0`;
  báo cáo mới là `Saved/Upgrade/coastal-quality-report.json`.
- `Tools/Upgrade/coastal_scene.py` đã sửa quy đổi cull từ mét sang cm Unreal,
  gom band 5 m và fade 120%. Đây là tối ưu visibility/draw cost theo kích thước,
  không phải bằng chứng FPS.
- `Config/DefaultEngine.ini` giữ DX12/SM6, Lumen software/VSM và TSR; tắt hardware
  ray tracing, bật HZB/occlusion/instance culling và loại khóa trùng.
- Build Development exit 0 trong 20.37 s; `Validate-ANANTA.ps1` exit 0.
- Quick gameplay headless mới ghi `COASTAL_QA_COMPLETE failures=0 views=122` trong
  `Saved/Upgrade/runtime-r6-quick.log`; spawn, cửa, dịch vụ, NPC, item, rìa biển,
  đi bộ, xe và xuồng đều PASS.
- Chưa benchmark headed 60 FPS; con số 16.667 ms chỉ là ngân sách mục tiêu.
  Chưa có World Partition/HLOD, lịch NPC, lái bay, minigame, kinh tế/save đầy đủ
  hoặc visual acceptance Unreal headed. Xem handoff ngày 15/10 để biết kế hoạch.


## Cập nhật 2026-10-15 — tranche 65 model và micro props

- Thêm Tools/Upgrade/coastal_micro_props.py với 10 model nhỏ: KitchenKnifeBlock,
  BathroomBin, BedroomClock, ToyBlocks, BarGlassRack, TrafficCone, FireHydrant,
  ParkingMeter, AirportCart và Lifebuoy. Các model dùng primitive low-poly, pivot
  nền ổn định và được đưa vào generator, phòng, đường phố, sân bay và bến biển.
- Generator đạt COASTAL_MODELS_OK 65 models; max triangles=9678. Review đạt
  MODEL_VIEW_COVERAGE_OK 65 models x 8 views và MODEL_REVIEWS_OK 65 models,
  520 rendered views.
- Import commandlet exit 0 với 65 model readback. BuildCoastalCity đạt
  COASTAL_MAP_OK 23 enterable buildings, 6947 instances / 969 HISM batches;
  map check 0 Error(s), 0 Warning(s). Hai cảnh báo còn lại là API Unreal deprecated
  và UE-MCP Slate startup, không phải lỗi nội dung.
- ReviewRoomGeometry đạt ROOM_GEOMETRY_VIEWS_OK 180 views cho 36 review unit;
  đây là kiểm tra hình học phòng, không phải visual acceptance headed.
- Audit engine-free đạt COASTAL_QUALITY_OK manifest_models=65 review_units=36
  warnings=0; import_readback=65, layout_buildings=23, review_views=180.
- Quick gameplay bounded mới chạy trên CoastalCity với
  -game -CoastalQA -NullRHI và ghi COASTAL_QA_COMPLETE failures=0 views=122
  trong Saved/Upgrade/runtime-r7-quick.log. Đây là kiểm tra logic ngắn, không phải
  benchmark/soak và không chứng minh 60 FPS headed.
- Giữ mục tiêu render 16.667 ms cho 60 FPS, TSR và Lumen software; chưa có log
  headed ghi GPU/VRAM/frame-time percentile. Chưa có World Partition/HLOD,
  lịch NPC, lái máy bay, hoạt ảnh chèo, minigame hoặc save/kinh tế đầy đủ.


## Cập nhật 2026-10-15 — lịch NPC và QA chuyển động

- Thêm lịch nhẹ cho resident NPC Kind=2: 23 actor giữ anchor, di chuyển dao động
  nhỏ mỗi 0,1 giây trong phạm vi 120 cm. Các actor còn lại không bật tick.
- Unreal Python dùng set_editor_property cho schedule_enabled, schedule_radius và
  schedule_speed; cách này tránh lỗi AttributeError khi đặt UPROPERTY bool.
- Build Development exit 0; map commandlet log tuyệt đối đạt
  COASTAL_MAP_OK 23 enterable buildings, 6906 instances / 928 HISM batches,
  Python script executed successfully và 0 error(s), 2 warning(s).
- QA r9 đạt 23_npcs_scheduled, npc_schedule_moves, micro_props_respond và
  COASTAL_QA_COMPLETE failures=0 views=122.
- Bằng chứng vẫn là NullRHI bounded QA, không thay thế headed material, visual,
  GPU, VRAM hoặc 60 FPS acceptance.

## Cập nhật 2026-10-15 — đèn giao thông runtime nhẹ

- 36 giao lộ có 72 actor `ACoastalInteractable` Kind=6 dùng mesh TrafficLight. Signal actor không sinh collision riêng, giúp giữ giao lộ thông thoáng và chuyển logic trạng thái ra runtime.
- `SignalPeriod` mặc định 12 giây, tối thiểu 3 giây. `SignalState` tuần tự Green, Yellow, Red theo 55%, 10%, 35% chu kỳ; pha khởi tạo lấy từ tọa độ để tránh mọi giao lộ đổi đồng thời.
- Tick 0,1 giây chỉ được bật cho resident schedule và signal; các actor tĩnh/HISM không bị chuyển thành tick actor.
- Build Development thành công; map commandlet ghi `COASTAL_MAP_OK 23 enterable buildings, 6834 instances / 892 HISM batches`, Python script executed successfully và 0 error(s), 2 warning(s). Hai warning là Slate startup và API save level deprecated.
- Quick gameplay QA r10 exit 0 với `traffic_signals_present PASS`, `npc_schedule_moves PASS`, `micro_props_respond PASS` và `COASTAL_QA_COMPLETE failures=0 views=122` trong `Saved/Upgrade/runtime-r10-signal.log`.
- Kết quả này chỉ xác nhận logic bounded bằng NullRHI. Chưa có headed visual/material review, kiểm tra màu đèn, đo GPU/VRAM hoặc benchmark 60 FPS; các bước đó vẫn nằm trong kế hoạch hero slice.

## Cập nhật 2026-10-15 — sáu prop nội thất mới

- Bộ model tăng từ 65 lên 71 với `MakeupKit`, `SaucePan`, `BathroomTowel`, `SofaCushion`, `ToyDoll` và `Laptop`. Tất cả dùng primitive low-poly, pivot nền, hướng `+X`, 3 LOD và tối đa 9.678 tam giác theo generator report.
- Blender 8-view review đạt `MODEL_VIEW_COVERAGE_OK 71 models x 8 views`; compose đạt `MODEL_REVIEWS_OK 71 models, 568 rendered views`. Import readback Unreal đạt `COASTAL_IMPORT_OK 71 models with 3 LODs; dimensions verified`.
- Phòng home/hotel/beauty gọi `place_interactive_prop` cho vanity, bếp, phòng tắm, sofa, đồ chơi và laptop; tất cả là Kind=5, message ngắn, không tạo tick riêng và giữ khoảng trống lối đi.
- Map commandlet đạt `COASTAL_MAP_OK 23 enterable buildings, 6834 instances / 892 HISM batches`; Build Development exit 0 trong 18,63 giây.
- QA r11 exit 0 đạt `11_micro_props_present PASS`, `micro_props_respond PASS`, `traffic_signals_present PASS`, `npc_schedule_moves PASS` và `COASTAL_QA_COMPLETE failures=0 views=122`.
- Đây là kiểm tra logic bounded NullRHI. Chưa có headed visual/material acceptance, đo frame-time/GPU/VRAM hoặc benchmark 60 FPS; các giới hạn này vẫn được giữ trong kế hoạch.

## Cập nhật 2026-10-15 — gate tàu hai hướng

- `coastal_transit.py` dựng hai ray song song, hai platform, cầu vượt và hai `ACoastalTrain` độc lập. `Train_0` chạy về phía đông (`Direction=+1`), `Train_1` chạy về phía tây (`Direction=-1`).
- `CoastalTrain.cpp` giữ chuyển động kinematic nhẹ 650 cm/s, dwell 6 giây tại ga X=0 và vòng lại ở cuối tuyến. Cách này giữ chi phí thấp, nhưng chưa phải hệ thống tín hiệu/AI railway hoàn chỉnh.
- QA bổ sung `train_two_way_present` để đếm hai actor và xác nhận đủ một hướng mỗi chiều. Build Development exit 0 trong 11,15 giây.
- QA r12 exit 0 đạt `train_two_way_present PASS`, `11_micro_props_present PASS`, `traffic_signals_present PASS`, `npc_schedule_moves PASS` và `COASTAL_QA_COMPLETE failures=0 views=122` trong `Saved/Upgrade/runtime-r12-train.log`.
- Đây là proof runtime bounded bằng NullRHI. Chưa có headed review tàu/ga, collision/player boarding, signal control, âm thanh tàu, schedule giao thông hoặc frame-time/GPU 60 FPS.
