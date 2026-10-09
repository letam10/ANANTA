# Vòng mở rộng, va chạm và phương tiện

Cập nhật 2026-10-09; nhánh codex/city-expansion. Vòng đang thực hiện.
Yêu cầu đã chốt: 3,4 × 3,4 km, gấp đôi hai chiều, bốn lần diện tích bản cũ.
Giữ model nhân vật/save thường; gameplay ngắn, chạy ngầm, không benchmark.

## Đã làm

- Bố cục liên tục 3.394,11 m mỗi chiều, 784 ô, 3.534 nhà; tám dạng khối/bảy bộ mặt tiền.
- Map đọc lại bằng tiến trình mới: 25.021 nhóm, 602.953 instance, 12 dịch vụ.
- Có cảnh sát/cứu hỏa/bar/arcade, công viên vòng quay, biển và cảng cùng map.
- Civic 348 / coastal 3.505 instance; 15 vật liệu. Bốn phòng có cửa rộng 480 cm.
- 11 phương tiện và sáu props đường phố: 197.536 tam giác tổng nguồn, texture PBR và LOD.
- 11 đồ sinh hoạt/vui chơi: 73.844 tam giác, 19 vị trí đã import/ghi map.
- Vòng quay 40.068 tam giác thay 282 khối cũ; tám cabin, vành/nan/khung chi tiết.
- Thêm 16 đèn phòng giới hạn khoảng hiển thị; vật liệu theo kích thước thế giới.
- NPC đi đến cửa, ẩn trong cabin, hiện và đi ra sau khi kiểm điểm xuống.
  Chưa có animation mở cửa/ngồi mới; vòng quay là cảnh vật tĩnh.
- Tối đa tám xe hoạt động gần người chơi; tuyến cố định, chờ vật cản/mặt đường chưa tải.
- Sửa biên lái xe, kiểm xoay, thoát xe dưới mái thấp, mantle, capsule khôi phục.
- Sửa cửa xe nhận nhầm nóc vật cản là sàn; xe dài kẹt hướng lái tại góc vỉa hè.
- Xe khởi đầu chuyển sát lề; không di chuyển xe đã lưu trong save thường.
- Mesh có kính translucent dùng LOD thường để giữ vật liệu đúng.

## Kết quả kiểm chứng

| Kiểm tra | Kết quả và giới hạn |
| --- | --- |
| Editor build + automation | PASS, 16/16; có regression Coach qua góc vỉa hè |
| Bố cục nguồn | PASS, không chồng nhà/lấn đường/thiếu mesh |
| Va chạm map sau thay vòng quay | PASS, 10.401 component / 47.809 instance chặn Pawn |
| Mặt đường | PASS 3.992 điểm; không đại diện mọi quỹ đạo người chơi |
| Cửa căn hộ/cà phê | PASS bốn đoạn CharacterMovement hai chiều |
| Fixture 11 phương tiện | PASS cửa bị chặn, đợi vật cản, lên xe, đi >=49 m, xuống/dọn actor |
| Tuyến Coach thật | PASS lên/qua góc rẽ/xuống bến tiếp, 3.315 lần kiểm tiếp đất |
| Import/đọc lại map | PASS các mesh mới, 19 đồ sinh hoạt, 16 đèn |
| Ảnh GPU civic | Đã xem tám ảnh; sửa lớp sàn và kiểm lại bar/arcade hết mảng loang |
| Save/config thường | Checksum không đổi sau QA |

## Giới hạn còn lại

- Cần chạy đủ ba tuyến tàu ở bến thật, các tuyến xe khác và cửa civic mới.
  Fixture phương tiện đã đạt không thay cho kiểm chứng trên mọi tuyến thực tế.
- Cảnh còn trống, bờ biển/nước và nội thất cần tinh chỉnh; chưa nghiệm thu đồ họa cuối.
- Mục tiêu Max native 1080p 90 FPS chưa đạt, cần <=11,11 ms/frame ổn định.
  Số cũ 52,56 FPS trung bình / p95 23,46 ms thuộc bản 1,7 km, không phải bản này.
- D3D12 PageFault/Nanite/VSM khởi động chưa được kết luận đã sửa.
- HLOD cũ lỗi thời; chưa dựng đầy đủ proxy mới cho 3,4 km.
- Cube đục sang Nanite mới có script thử, chưa áp dụng hoặc xác nhận lợi ích.
- Chưa có EXE mới cho 3,4 km. CitySettingsPreview vẫn là map 1,7 km/menu cũ đã kiểm.

## Vòng tiếp theo

1. Cập nhật tài liệu, commit/push checkpoint; sửa sàn đã kiểm ảnh đạt.
2. Kiểm tuyến tàu thật, tuyến đường còn lại, cửa/dịch vụ và collision khi streaming.
3. Quan sát Max bằng gameplay ngắn, xác định phần render tốn thời gian và thử sửa có đối chiếu.
4. Dựng HLOD đầy đủ; build/cook/package thành EXE mới và chạy QA cô lập.
5. Tiếp tục chất lượng cảnh vật và 90 FPS; không coi build/test là nghiệm thu toàn game.

## Bằng chứng và khôi phục

- Saved/QA/CityAutomation/index.json, CityWholeMapCollision.txt, CityFleetCheck/Report.txt.
- Saved/QA/CityTransitCheck/Report.txt, CityMobilityMapReadback.json, CityExpansionApplied.json.
- Saved/QA/CityMobilityAssets, CityLivingAssets, CityFerrisAssets, CityCivic.
- Assets/City/*_manifest.json ghi nguồn/giấy phép/hash/tam giác/texture.
- Backup trước mở rộng: Saved/Backups/CityBeforeMobility_20261008_225729,
  7.556 file / 569.205.616 byte. Không xóa backup hoặc save thường.
- Hợp đồng API/phân việc: CITY_MOBILITY_EXPANSION_CONTRACT.md.
- Checkpoint trước vòng này a26ca25; không đưa save/log máy lên Git.
