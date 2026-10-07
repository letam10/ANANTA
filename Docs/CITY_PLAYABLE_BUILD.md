# Bản thành phố có thể chạy

Cập nhật: 08/10/2026. Đây là bản Development dùng để kiểm tra và phát triển tiếp.

## Mở game

Chạy `D:\GAME\ANANTA\Saved\Builds\City\Windows\ANANTA.exe`.
Giữ nguyên các thư mục bên cạnh executable khi di chuyển bản chơi.
Game mặc định mở bản đồ `ANANTA_City`.

## Điều khiển

- WASD: đi bộ hoặc lái xe; chuột: nhìn quanh.
- Shift: chạy nhanh; Space: nhảy hoặc phanh xe.
- E: tương tác, vào hoặc ra xe; chuột trái: tấn công.
- F: trèo/vượt; F5: lưu; Esc: tạm dừng.

## Nội dung hiện có

- Thành phố 1,2 x 1,2 km với khu thương mại, dân cư và transit trên một bản đồ.
- 397 tòa nhà dạng vỏ; chỉ quán cà phê và căn hộ có nội thất được bố trí.
- World Partition, 152 HLOD, vật liệu PBR và đèn đường giới hạn theo khoảng cách.
- Một xe điều khiển, người đi bộ và xe lưu thông gần người chơi.
- Nhiệm vụ điều tra ba manh mối, đánh ba kẻ địch, lấy mảnh dị thường và báo lại.

## Đã kiểm chứng

- Build, cook và đóng gói Windows thành công.
- Bản đóng gói chạy đúng map mặc định; đi vào quán và sử dụng xe đạt kiểm tra.
- Hoàn thành nhiệm vụ, nhận thưởng đúng một lần, lưu và tải lại qua tiến trình mới đạt kiểm tra.
- Truy vấn Recast trả về đường đi hoàn chỉnh.
- Đủ 16 ảnh ban ngày/chiều tối ở độ phân giải 1920 x 1080, đã kiểm tra hình ảnh.
- Các phép thử dùng slot QA riêng và input của engine; không chạy vòng benchmark.

## Phần cần tiếp tục

Mặt tiền còn lặp, nhân vật vẫn dùng mannequin và nội thất tương tác còn thưa.
Hình ảnh hiện là prototype của thành phố liên thông, chưa đạt chất lượng các game tham chiếu.
Mục tiêu 60 FPS ổn định khi chơi và thao tác bàn phím desktop trực tiếp chưa được xác nhận.

Log và trạng thái chi tiết: `Docs/CITY_EXECUTION_STATUS.md`.
