# Review settings runtime — City 6800

## Phạm vi

- Đọc settings backend/UI, đổi ngôn ngữ, HUD/FPS, persistence, automation và runner.
- Không mở Unreal, build hoặc chạy workload theo hợp đồng review.
- Không thấy bằng chứng nguồn đủ để kết luận lỗi áp dụng/lưu/nạp ngôn ngữ hoặc FPS khác.

## Finding có thể tái hiện

1. **[P2] Mức giới hạn FPS hợp lệ có thể không có lựa chọn được đánh dấu trong UI.**
   - Backend chấp nhận mọi giá trị hữu hạn 30–240 FPS: `ANANTAGraphicsSettings.cpp:37-44`.
   - UI chỉ tạo lựa chọn `0, 30, 60, 90, 120, 144, 165, 180, 240`;
     selected index dùng `IndexOfByKey`: `SCitySettingsPanelControls.cpp:125-146`.
   - Với cấu hình hợp lệ `FrameRateLimit=200`, nhãn hiện “200 FPS” nhưng danh sách
     không đánh dấu mục đang chọn. Người chơi không thể chọn/khôi phục mức 200 qua UI.
   - Tái hiện tập trung: đặt `FrameRateLimit=200` trong section
     `[/Script/ANANTA.ANANTAGraphicsSettings]`, nạp settings, mở Display & Language;
     xác nhận nhãn 200 FPS và dropdown không có radio entry được chọn.
   - Test hiện hành bao phủ cap 30/90/144/240 (`CityGraphicsSettingsTests.cpp:146-152`),
     chưa bao phủ cap hợp lệ nằm giữa các lựa chọn như 200.

## Chưa được xác nhận / bằng chứng còn thiếu

- Không có runtime mới trong lượt review này để xác nhận persistence qua lần khởi động
  thực tế, cập nhật culture trên toàn bộ HUD/nhiệm vụ, hoặc độ chính xác của FPS meter.
  Source cho thấy meter lấy số frame theo đồng hồ thực (`ANANTACityControllerSettings.cpp:99-117`),
  nhưng review tĩnh không chứng minh số đo trong Player.
- Mục tiêu native 1920×1080, render scale 100%, khoảng 90 FPS không được xác nhận
  bởi `FrameRateLimit=90`, preset Epic hay nhãn mục tiêu trên HUD. Cần lượt chơi trên
  map mới, ghi độ phân giải/render scale có hiệu lực và frame-time/FPS thực tế.
- Khuyến nghị kiểm thử: thêm case cap 200 cho selected UI, rồi chạy packaged
  settings Check + Reload trên config riêng; kiểm tra UI và giá trị sau tiến trình mới.
