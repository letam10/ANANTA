# Factory dressing source round 2026-10-10

## Source change

- Sửa đúng điểm tích hợp `Tools/Editor/CityMetroDistrict.py`, hàm `factory(layout, x, y, height, material)`.
- Giữ nguyên reserve `(-46700, 216900, -37300, 226700)` tương ứng footprint hiện tại; không đổi shell,
  đường, actor nhân vật, save cá nhân hoặc collision của map đã lưu.
- Dời ngôn ngữ loading về mặt phố `-Y`: apron rộng 3.600 x 1.200 cm, bốn cọc bảo vệ,
  hai cửa cuốn 920 x 1.160 cm, dầm canopy liên tục và dải cảnh báo lặp.
- Các chi tiết dùng `Layout.box`/mesh Cube và được nhóm theo material, cell, collision; chi tiết trang trí
  đặt `collision=False` để giữ chi phí thấp khi lặp trong thành phố.

## Kiểm chứng

- `python -m py_compile Tools/Editor/CityMetroDistrict.py` đạt.
- Kiểm tra source giữ API factory và không thay đổi hằng `AIRPORT`, `RESERVES`, `SITES`.
- Chưa chạy `ApplyCityExpansion.py` trong Unreal, chưa tạo PNG mới và chưa nhận mỹ thuật cuối.
- Cần chạy layout/readback, capture năm góc native, kiểm AABB/đường vào, rồi mới xem chi tiết loading đã thẳng
  với shell hay chưa. Không suy ra 60 FPS từ source compile.

## Còn mở

- Sân bãi công nghiệp vẫn cần thêm thùng hàng/xe nâng ở mức prototype nhẹ sau khi placement pass.
- Airport cần capture gần mặt đất theo `PrepareFacilityCloseViews.py`.
- Collision, nội thất tương tác, gameplay NPC và hiệu năng native 60 FPS chưa được nghiệm thu ở vòng này.
