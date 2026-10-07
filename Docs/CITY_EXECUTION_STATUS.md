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
- Đang chụp cảnh mở rộng và chạy lượt input thử dịch vụ; chưa xác nhận kết quả runtime.
- Chưa dựng lại HLOD hay đóng gói bản mở rộng.

## Còn tồn đọng / chưa đạt

1. Kiểm tra kit trong game, đặc biệt va chạm trạm chờ và lối vào các phòng.
2. Biên dịch lượt thử dịch vụ, kiểm tra ảnh khu mở rộng và nội thất.
3. Dựng lại HLOD; kiểm tra streaming và đường đi trong khu mở rộng.
4. Chơi ngắn kiểm tra cửa mới, dịch vụ, vật phẩm, xe, nhiệm vụ, lưu/tải và save cũ.
5. Xem ảnh ngày/đêm, sửa bố cục lặp, ánh sáng và nội thất thiếu chi tiết.
6. Đánh giá frame trong lần chơi bình thường, tối ưu điểm nghẽn thực tế; chưa chứng minh 60 FPS.
7. Đóng gói và xác nhận lại bản cuối; không dùng build cũ để nhận bản mở rộng đạt.
8. Checkpoint trên nhánh codex/city-expansion; cập nhật kết quả push và runtime trong vòng tiếp theo.

## Bằng chứng và đường dẫn

- Bản chơi đã kiểm chứng trước mở rộng: Saved/Builds/City/Windows/ANANTA.exe.
- Backup: Saved/Backups/CityBeforeExpansion_20261008_055644.
- Bố cục mới: Saved/QA/CityExpansionSourceAudit.json.
- Build mới: Saved/Logs/CityExpansionBuild.log.
- Hợp đồng: Docs/CITY_EXPANSION_CONTRACT.md.

Input QA qua PlayerController.InputKey; bàn phím desktop thực chưa được xác nhận.
Đồ họa cuối và 60 FPS vẫn là mục tiêu đang làm, chưa đủ bằng chứng để xác nhận.
