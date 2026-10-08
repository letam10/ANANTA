# ANANTA — tiến độ thành phố

Cập nhật: 2026-10-08. Mục tiêu đang thực hiện, chưa hoàn tất.
File này là bản tóm tắt hiện hành; bằng chứng chi tiết nằm trong Saved/QA và Saved/Logs.
Mỗi vòng làm việc phải cập nhật file này và commit/push checkpoint lên GitHub.

## Mục tiêu hiện hành

- Mở rộng gấp đôi, tăng mật độ, kiến trúc, kích thước, cảnh quan và địa điểm tương tác.
- Giữ nguyên model nhân vật; nhà nền chỉ có vỏ, tập trung nội thất vào nhà vào được.
- Một bản đồ liên tục, tối ưu streaming/HLOD, đồ họa đẹp với mục tiêu khoảng 60 FPS.
- Chỉ thử chơi ngắn vài phút, không benchmark.
- Mặc định: gấp đôi diện tích, khoảng 1,70 × 1,70 km; chờ lựa chọn khác nếu có.

## Bản trước đã pass

- Thành phố 1,2 × 1,2 km, 397 nhà nền, hai nội thất, 110.549 instance, 152 HLOD.
- World Partition/OFPA; mở lại kiểm tra mesh/material không lỗi.
- Build và đóng gói Windows Development thành công.
- Input controller: đi bộ, vào quán, lái/phanh/rời xe, F5; nhiệm vụ đầy đủ khoảng 205 giây.
- Ba manh mối, ba địch, mảnh vỡ, thưởng đúng một lần; tiến trình khác tải lại trạng thái/vị trí.
- Recast có đường hoàn chỉnh; 16 ảnh đóng gói ngày/chiều xanh 1080p đã được xem.
- Bằng chứng này thuộc bản trước, không tự động chứng minh bản mở rộng.

## Đã thay đổi trong vòng hiện tại

- Nguồn bố cục: 196 ô phố, 1.472 nhà nền, bảy kiểu mặt tiền, nhiều kiểu khối/cao độ.
- Bổ sung sân trong, công viên, cây, quầy hàng, trạm chờ và vật dụng đường phố.
- Sáu địa điểm mới: hiệu sách, phòng khám, cửa hàng, phòng tranh, xưởng xe, trung tâm giao thông.
- Mã dịch vụ: nghỉ/hồi phục, nhận tiếp tế một lần, đọc/ghi nhận địa điểm và lưu trạng thái.
- Mở giới hạn save, tuyến NPC và đèn theo lưới mới; không sửa model nhân vật.
- Đã dựng và nhập 11 model kiến trúc/cảnh quan, dùng PBR từ bộ tài nguyên hiện có.
- Có script nhập kit và cập nhật hình học trong map World Partition hiện tại.
- Đã thêm 177 vật thể cho tám nội thất và 73 vật thể cho ba quảng trường.
- Thêm cửa sổ có ánh sáng/rèm theo từng ô kính, dùng một tham số shader chung.
- Giảm độ gắt 16 đèn nội thất và giới hạn khoảng cách xử lý ánh sáng phòng.

## Kiểm chứng mới

- PASS: kiểm tra nguồn không có nhà chồng nhau, đường hoặc vùng cửa vào.
- PASS: đủ 1.472 nhà, bảy loại mặt tiền và sáu địa điểm mới trong dữ liệu thiết kế.
- PASS: cú pháp các script Python mới.
- PASS: sao lưu map/actor/object, 1.845 file / 413.367.217 byte.
- PASS: biên dịch Editor; sáu Unreal automation test, không thất bại hay bỏ qua.
- PASS: 11 FBX roundtrip, UV/material/hash/triangle budget và ảnh model đã kiểm tra.
- PASS: nhập kit và áp dụng map; các mốc nhiệm vụ/người/xe được giữ nguyên.
- PASS: mở lại map độc lập, 7.000 actor, 281.266 instance, 92 material graph, không lỗi.
- PASS: biên dịch lượt thử tám dịch vụ; sửa ghi nhận đủ tám loại địa điểm, sáu test chạy lại đều pass.
- PASS: lượt chơi 293,524 giây qua tám cửa/dịch vụ, nhận tiếp tế một lần, nhấn E lặp và F5.
- PASS: tiến trình khác tải lại đủ tám lượt thăm, một tiếp tế và vị trí người chơi.
- Quan sát lượt chơi: 32.444 frame, trung bình 8,985 ms, p95 10,423 ms; 3 frame >33,3 ms.
- PASS: tám ảnh ngày và tám ảnh chiều xanh 1080p. Ảnh cho thấy nội thất còn trống, bóng phố quá tối.
- Một lần khởi tạo chiều xanh gặp GPU page fault khi dựng bóng Nanite; lần sau pass, chưa rõ nguyên nhân.
- PASS: lưu/mở lại 250 vật thể trang trí, 16 đèn và tám dịch vụ, không lỗi mesh/material.
- PASS: build gộp mã C++; sửa xung đột tên hàm phụ giữa hai bộ QA.
- PASS: 7/7 automation, gồm đọc file save cũ thật trước khi có Services; giữ nhiệm vụ/thưởng/vị trí.
- PASS: ảnh GPU ngày/chiều xanh sau chỉnh đèn và tám ảnh góc trang trí mới.
- PASS: tuyến dịch vụ sau trang trí 293,487 giây, tám địa điểm, một tiếp tế; tải lại giữ đúng vị trí.
- Phát hiện/sửa: FBX đảo trục Y làm mặt tiền/ban công quay vào trong; 238.666 instance và tám cửa đã sửa.
- PASS: mở lại 1.544 nhóm, 4.631 mẫu transform và tám cửa đúng hướng; ảnh GPU hiện rõ chi tiết mặt tiền.
- PASS: NavMesh lưu đúng 860 m mỗi phía; truy vấn Recast ở khu mới trả đường đầy đủ dài 16 m.
- Sửa runner GPU: bắt buộc dấu hoàn tất trong log, không nhận mã thoát 0 là đủ.
- HLOD bản mở rộng đang dựng: 288 cụm, bắt đầu 10:33 ngày 08-10; chưa hoàn tất hoặc đóng gói.
- Chuẩn bị lượt hoàn thiện: sofa nhung HOUSE có tác giả Wayfair/Eric Chadwick, giấy phép CC BY 4.0.
- PASS nguồn: hai bộ sàn Poly Haven CC0, tám ảnh PBR 2K, checksum khớp API; đã xem ảnh màu.
- Terrazzo dành cho phòng khám/chợ/trung tâm giao thông; bê tông sơn mòn dành cho xưởng xe.
- Script áp dụng và đọc lại bốn sàn đã qua kiểm tra cú pháp; chưa chạy Unreal trong lúc HLOD dựng.
- HLOD tại 10:59 vẫn ở cụm 6/288, CPU tiếp tục tăng; đang rà soát chi phí tạo proxy bằng mã engine.

## Còn tồn đọng / chưa đạt

1. Kiểm tra kit trong game, đặc biệt va chạm trạm chờ và lối vào các phòng.
2. Chỉnh mảng tường/phần giữa phòng còn trống; tiếp tục giảm chi tiết còn mang dáng prototype.
   Đang dựng sofa/thảm/rèm; nhập và áp dụng sàn mới sau khi HLOD hiện hành kết thúc.
3. Dựng lại HLOD; kiểm tra streaming và đường đi trong khu mở rộng.
4. Chơi ngắn kiểm tra cửa mới, dịch vụ, vật phẩm, xe, nhiệm vụ, lưu/tải và save cũ.
5. Xem ảnh ngày/đêm, sửa bố cục lặp, ánh sáng và nội thất thiếu chi tiết.
6. Đánh giá frame trong lần chơi bình thường, tối ưu điểm nghẽn thực tế; chưa chứng minh 60 FPS.
7. Đóng gói và xác nhận lại bản cuối; không dùng build cũ để nhận bản mở rộng đạt.
8. Đã push 6513f16 lên origin/codex/city-expansion, gồm trang trí/ánh sáng/hướng mặt tiền/NavMesh.
   Remote SHA khớp local; 1.831 đối tượng LFS / 50 MB. Commit tiếp theo cập nhật trạng thái này.

## Bằng chứng và đường dẫn

- Bản chơi đã kiểm chứng trước mở rộng: Saved/Builds/City/Windows/ANANTA.exe.
- Backup: Saved/Backups/CityBeforeExpansion_20261008_055644.
- Bố cục mới: Saved/QA/CityExpansionSourceAudit.json.
- Build mới: Saved/Logs/CityExpansionBuild.log.
- Hợp đồng: Docs/CITY_EXPANSION_CONTRACT.md.
- Dịch vụ: Saved/QA/CityServiceJourney/Report.txt và Reload.txt.
- Log GPU lỗi đã giữ: Saved/Logs/CityGPUCaptureBlueHour.Failure1.log.
- Trang trí: Saved/QA/CityDressingReadback.json; ảnh Saved/QA/CityDressing và CityGPUBlueHour.
- Save cũ: Tools/QA/Fixtures/CityBeforeServices.sav; báo cáo Saved/QA/CityAutomation/index.json.
- Hướng mặt tiền: Saved/QA/CityFacadePlacementReadback.json; NavMesh: Saved/Logs/CityGPUNavigationCheck.log.
- HLOD đang chạy: Saved/Logs/CityHLOD.log và CityHLODConsole.log.
- Nguồn sàn: Assets/City/interior_finish_catalog.json; kiểm tra Saved/QA/CityInteriorTextures.json.
- Script sàn chưa chạy: Tools/Editor/ApplyCityFloorFinishes.py và VerifyCityFloorFinishes.py.

Input QA qua PlayerController.InputKey; bàn phím desktop thực chưa được xác nhận.
Đồ họa cuối và 60 FPS vẫn là mục tiêu đang làm, chưa đủ bằng chứng để xác nhận.
