# Cài đặt đồ họa và ngôn ngữ

## Cách dùng

- **Esc / F10**: mở hoặc đóng menu cài đặt, game tạm dừng khi menu mở.
- **Giữ Alt**: hiện chuột để bấm nút Cài đặt góc trên phải.
- **F8**: bật/tắt thanh FPS ngay trong game.
- Chọn thông số rồi bấm **Áp dụng**. **Đóng / Hủy**, Esc hoặc F10 bỏ thay đổi chưa áp dụng.
- **Mặc định** chỉ đổi bản nháp; cần Áp dụng để lưu.
- **Tab / Enter**: chọn và xác nhận control; cuộn xuống để thấy ngôn ngữ.
- Có **Tiếng Việt / English**, áp dụng ngay cho menu, HUD, nhiệm vụ và lời nhắc tương tác.

## Các mức chất lượng

| Mức | Nhóm UE | TSR khi chọn preset |
| --- | --- | --- |
| Thấp | 0 | Theo lựa chọn preset trong menu |
| Trung bình | 1 | Theo lựa chọn preset trong menu |
| Cao | 2 | 83,33% |
| Tối đa · Epic | 3 | 100% |

Có thể chỉnh riêng tầm nhìn, khử răng cưa, bóng, GI, phản chiếu, hậu kỳ, texture,
hiệu ứng, cây cỏ và shading; khi khác preset, menu hiển thị tùy chỉnh.
TSR cho phép 50–100%; 100% tại đầu ra 1080p là dựng thật 1920×1080.
Giới hạn FPS và VSync là lựa chọn riêng, không làm máy tự đạt được số FPS đã chọn.
Texture pool Epic/High cùng 3 GB; hardware ray tracing tắt theo thiết kế dự án.

## Thanh FPS

- Lấy số frame theo thời gian đồng hồ thực, cập nhật trung bình mỗi 0,5 giây.
- Hiển thị FPS và ms/frame; thanh đầy tại mốc mục tiêu 90 FPS.
- Không dùng FPS cap hoặc thời gian mô phỏng để tạo số đo.
- Số tại một ảnh chụp không thay thế đánh giá cả lượt chơi.

## Kiểm chứng ngày 2026-10-08

- Build Editor đạt; 11/11 automation đạt, gồm chuyển cấu hình cũ và giới hạn giá trị.
- QA input mở/đóng, tạm dừng, chặn di chuyển, bỏ bản nháp, áp dụng, đổi ngôn ngữ và F8 đạt.
- Đọc lại cấu hình ở tiến trình mới đạt; kiểm tra giao diện/các dấu tiếng Việt ở 1080p và 720p.
- QA kích hoạt nút bằng keyboard Slate; chuột desktop vật lý chưa được kiểm tra.
- Hai save thường và cấu hình thường giữ đúng SHA-256 sau vòng kiểm tra cuối.
- Lỗi runner automation cũ chạm cấu hình đã khôi phục đúng checksum và sửa sang config QA riêng.

### Mục tiêu 90 FPS: chưa đạt ở Tối đa

Máy kiểm tra: RTX 4060 Laptop 8 GB, Ryzen 7 8845H, RAM 16 GB.
Lượt chơi tám địa điểm khoảng 295,6 giây, không benchmark, Epic (3), native 1080p, cap 90:

| Quan sát | Kết quả |
| --- | --- |
| FPS trung bình theo thời gian frame | 52,56 |
| Frame trung bình / p95 / p99 | 19,02 / 23,46 / 28,79 ms |
| Frame chậm nhất | 119,77 ms |
| Frame >33,3 / >50 ms | 52 / 9 |
| GPU trung bình | 18,18 ms |
| Luồng render trung bình | 18,94 ms |
| Game thread trung bình | 7,12 ms |

Bộ quan sát độc lập thu 15.486 mẫu; báo cáo tuyến dịch vụ thu 15.429 mẫu do cửa sổ bắt đầu/kết thúc khác nhau.
Các bộ đếm CPU/GPU có thể trễ một frame; không cộng các luồng song song thành tổng thời gian frame.
HLOD bản mở rộng chưa hoàn tất. Còn lỗi GPU PageFault rời rạc khi khởi tạo Nanite/VSM đang chẩn đoán.
Không dùng kết quả cấu hình Cao trước đó để nhận mức Tối đa đã ổn định 90 FPS.

## Bằng chứng và công cụ

- Saved/QA/CitySettings1080p: ảnh menu/FPS và báo cáo Check/Reload.
- Saved/QA/CitySettings: ảnh menu đọc lại ở 720p, config QA và bản bảo toàn cấu hình cũ.
- Saved/QA/CityMaxGraphics: RenderConfig.txt, FrameTimes.csv, Summary.json và Report.txt.
- Tools/Build/Test-CitySettings.ps1: kiểm tra menu; thêm -Reload, -Height 720 cho lượt đọc lại.
- Tools/Build/Test-CityMaxGraphics.ps1: một lượt chơi tám dịch vụ ở Epic/1080p, lưu toàn bộ frame.
- Docs/CITY_EXECUTION_STATUS.md: tiến độ hiện hành và việc tiếp theo.
