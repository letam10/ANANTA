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
- Chuyển 113.907 instance khối đục sang Nanite, giữ nguyên geometry/material/collision.

## Kết quả kiểm chứng

| Kiểm tra | Kết quả và giới hạn |
| --- | --- |
| Editor build + automation | PASS, 17/17; gồm Coach qua góc và tuyến NPC cuối vỉa hè |
| Bố cục nguồn | PASS, không chồng nhà/lấn đường/thiếu mesh |
| Va chạm map sau thay vòng quay | PASS, 10.401 component / 47.809 instance chặn Pawn |
| Mặt đường | PASS 3.992 điểm; không đại diện mọi quỹ đạo người chơi |
| Cửa căn hộ/cà phê | PASS bốn đoạn CharacterMovement hai chiều |
| Bốn cửa civic | PASS tám lượt vào/ra bằng W/Shift, bốn tương tác E, 51,26 giây |
| Fixture 11 phương tiện | PASS cửa bị chặn, đợi vật cản, lên xe, đi >=49 m, xuống/dọn actor |
| Tuyến Coach thật | PASS lên/qua góc rẽ/xuống bến tiếp, 3.315 lần kiểm tiếp đất |
| Tám tuyến đường bộ | PASS 16 xe, vòng khoảng 925 m/xe, đủ bốn bến lên/xuống, 140,86 giây |
| Ba tuyến tàu ở cảng thật | PASS khoảng 219 m khứ hồi/loại, trở lại bến và NPC xuống |
| Import/đọc lại map | PASS các mesh mới, 19 đồ sinh hoạt, 16 đèn |
| Ảnh GPU civic | Đã xem tám ảnh mới sau Nanite; không thấy mất mặt tiền/nền/cầu tàu/vòng quay |
| Save/config thường | Checksum không đổi sau QA |
| Reload save dịch vụ | PASS tiến trình GPU mới, đủ tám địa điểm trên bản 3,4 km |

## Giới hạn còn lại

- Cần thử người chơi đi tại cảng và tương tác trong EXE mới.
  Fixture phương tiện đã đạt không thay cho kiểm chứng trên mọi tuyến thực tế.
- Kiểm cảng là fixture NullRHI có dời observer và nạp vùng: không thêm sàn giả,
  không đổi tốc độ/vị trí cầu tàu/collision; chưa phải nghiệm thu hình ảnh hoặc đi bộ tại cảng.
- Cảnh còn trống, bờ biển/nước và nội thất cần tinh chỉnh; chưa nghiệm thu đồ họa cuối.
- Max native 1080p mới: 62,57 FPS trung bình / p95 18,90 ms trong 281,61 giây.
  Hoàn tất tám dịch vụ sau sửa tuyến NPC; chưa đạt 90 FPS/11,11 ms.
  Giữ đủ 17.621 frame, gồm 22 frame trên 33,3 ms và sáu frame trên 50 ms.
- Đã sửa tuyến NPC quá ngắn ở cuối vỉa hè: regression từ 57 lỗi về 0; gameplay đi qua được.
- D3D12 PageFault/Nanite/VSM khởi động chưa được kết luận đã sửa.
- Trước chuyển Nanite: Max và NonNanite.Batch=0 đều PageFault.
  VSM tắt hoàn tất gameplay 282,62 giây/55,71 FPS, chỉ là lượt chẩn đoán.
  Hai lượt Max sau chuyển Nanite chưa crash; chưa đủ kết luận sửa triệt để.
- HLOD cũ lỗi thời; chưa dựng đầy đủ proxy mới cho 3,4 km.
- Cube Nanite đã áp dụng, body/3.992 điểm đường và tám ảnh đã kiểm; cần HLOD mới.
- Chưa có EXE mới cho 3,4 km. CitySettingsPreview vẫn là map 1,7 km/menu cũ đã kiểm.

## Vòng tiếp theo

1. Commit/push checkpoint Nanite và các kiểm tra đã đạt.
2. Kiểm người chơi tại cảng, tuyến đường còn lại, cửa/dịch vụ và collision khi streaming.
3. Quan sát Max bằng gameplay ngắn, xác định phần render tốn thời gian và thử sửa có đối chiếu.
4. Dựng HLOD đầy đủ; build/cook/package thành EXE mới và chạy QA cô lập.
5. Tiếp tục chất lượng cảnh vật và 90 FPS; không coi build/test là nghiệm thu toàn game.

## Bằng chứng và khôi phục

- Saved/QA/CityAutomation/index.json, CityWholeMapCollision.txt, CityFleetCheck/Report.txt.
- Saved/QA/CityTransitCheck/Report.txt, CityMobilityMapReadback.json, CityExpansionApplied.json.
- Saved/QA/CityHarborCheck/Report.json: ba tàu đạt, tổng 78,28 giây sau world sẵn sàng.
- Saved/QA/CityMobilityAssets, CityLivingAssets, CityFerrisAssets, CityCivic.
- Assets/City/*_manifest.json ghi nguồn/giấy phép/hash/tam giác/texture.
- Backup trước mở rộng: Saved/Backups/CityBeforeMobility_20261008_225729,
  7.556 file / 569.205.616 byte. Không xóa backup hoặc save thường.
- Hợp đồng API/phân việc: CITY_MOBILITY_EXPANSION_CONTRACT.md.
- Checkpoint mở rộng 4b18a76 đã push/đối chiếu remote; không đưa save/log máy lên Git.
