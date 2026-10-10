# Hợp đồng rà runtime khi đang apply

Repo D:\GAME\ANANTA, Unreal 5.8.3, nhánh codex/city-expansion.
Apply đang chạy; không mở Unreal, không build, không chạy workload hay sửa asset/map.
Không sửa model nhân vật hoặc save người chơi. Không tạo agent con.

## Hằng số và ý nghĩa chung

- RoadExtent = 336000 cm, spacing = 12000 cm; chiều rộng ranh giới = 678822.51 cm.
- Vùng biển cắt lưới ở x >= 120000 và y <= -120000.
- Sân bay cắt đường phố trong 180000 < x < 276000, 180000 < y < 228000.
- Capsule nhân vật 38/92 cm; đi bộ 350 cm/s; giữ nguyên các thông số.
- Mục tiêu mới: Max tùy chỉnh, native 1920x1080/100%, khoảng 90 FPS.
- Lượt gameplay cũ Editor 3,4 km đạt 50,34 FPS; không dùng làm bằng chứng map mới/90 FPS.
- Mỗi báo cáo phân biệt lỗi có bằng chứng, khả năng chưa được chứng minh và kiểm chứng còn thiếu.

## Phạm vi độc lập

- NPC: chỉ viết Docs/CITY_6800_NPC_RUNTIME_REVIEW.md, dưới 100 dòng.
  Đọc Crowd, pedestrian/transport routes, sea/airport cutouts và source test.
  Tìm tuyến sai, vị trí spawn nguy hiểm hoặc vùng mới không có NPC; ghi file/dòng/test tái hiện.
- Settings: chỉ viết Docs/CITY_6800_SETTINGS_RUNTIME_REVIEW.md, dưới 100 dòng.
  Đọc Settings/UI/HUD/language/save/QA runner, tìm lỗi thay đổi/lưu/nạp cài đặt và FPS hiển thị.
  Tìm bằng chứng cụ thể, không hứa hẹn đạt FPS từ frame cap hay preset.

Không chỉnh mã, không commit/push, không kiểm tra lại model/ảnh đã nghiệm thu nguồn.
Tự kiểm git diff --check, số dòng và dòng dài; báo một lần tối đa 15 dòng.
Báo cáo phải nêu tối đa ba lỗi có tác động thật với vị trí chính xác và cách kiểm chứng.
