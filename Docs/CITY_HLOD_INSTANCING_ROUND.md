# Vòng HLOD và vật thể lặp

Cập nhật 2026-10-09. Checkpoint nguồn b99f3956f đã push và đối chiếu SHA remote.

## Kết quả và giả định

- ISM/HISM giảm lệnh vẽ cho mesh/vật liệu giống nhau; Ctrl+D không tự tạo instancing.
- Map đã có 25.021 nhóm và 602.953 instance; số này không chứng minh đạt 90 FPS.
- Max hiện đo 62,57 FPS trong hành trình dịch vụ; mục tiêu 90 chưa đạt.
- Lượt Mesh Simplify đầy đủ dừng, không có marker hoàn tất; log chỉ ghi bốn proxy đã lưu trên 962.
- Chưa xác định nguyên nhân dừng; không kết luận crash hay thành công từ việc mất process.
- Instancing HLOD tái sử dụng mesh và vật liệu nguồn; giữ Nanite, không lọc bỏ instance.
- Giữ cell 256 m và loading range 1,2 km; cần kiểm ảnh và chi phí runtime sau dựng.
- PASS mẫu Instancing: một actor, 495 instance, không thiếu mesh/material; build proxy khoảng một giây sau nạp map.
- PASS bounds thực từ Unreal và bố trí 5 nhóm / 54 instance / 43 collider cho bar và arcade.
- Bổ sung 11 bàn, 22 ghế, 4 sofa, 11 thảm; thay sáu máy arcade dạng khối bằng asset chi tiết.
- Kiểm room containment, lối đi cộng bán kính capsule 38 cm, chồng đồ mới và bàn ghế cũ đạt.
- HLOD đầy đủ PASS 962/962; đọc lại 591.633 instance, không thiếu mesh/material.
- Sau bố trí mới: tám lượt qua cửa/four services PASS; đã xem đủ tám ảnh GPU civic.
- Build/cook/package EXE CityExpanded PASS; menu Apply PASS, reload lỗi GPU PageFault khi dựng bóng Nanite/VSM.
- EXE Max native 1080p: 47,71 FPS, p95 37,87 ms, 13.523 frame/283,46 giây; giữ mọi frame.
- Mục tiêu 90 FPS chưa đạt; profile riêng đang dùng để xác định chi phí, không thay số đo thường.
- Yêu cầu mới tăng tiếp lên 6,8 km và chuẩn tám hướng model/năm góc đặt: CITY_6800_CONTRACT.md.

## Tiêu chí kiểm chứng

1. Đổi lớp, đọc builder là HLODBuilderInstancingSettings, lưu đúng asset.
2. Dựng một proxy; log hoàn tất duy nhất, đọc lại mesh/instance/material không lỗi.
3. Nếu mẫu đạt, dựng toàn bộ; xác nhận 962 actor hoặc số mới từ Setup, log không thiếu thứ tự.
4. Đọc lại tất cả proxy, chụp ảnh đường phố và chạy hành trình thường vài phút ở Max.
5. Chỉ ghi FPS mới khi đo đủ hành trình, giữ mọi frame; chưa coi 90 FPS là đạt.
6. Cập nhật trạng thái, commit/push sau khi có kết quả cụ thể.

## Bằng chứng dự kiến

- Saved/Logs/CityHLODSample.log; Saved/QA/CityHLODInstancesSample.json.
- Saved/Logs/CityHLOD.log; Saved/QA/CityHLODInstances.json.
- Saved/QA/CityMaxGraphics/Summary.json và ảnh GPU sau khi dựng hoàn tất.
- Không sửa save thường, nhân vật hoặc tốc độ gameplay.
