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
