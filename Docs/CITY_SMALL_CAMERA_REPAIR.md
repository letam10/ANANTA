# Sửa camera QA props nhỏ — 2026-10-10

## Bằng chứng và phạm vi

- Đọc `Saved/QA/CitySmallNativeBounds.json`: persisted map, không sửa map,
  36 bounds từ 67 source actors; fixture test chép các số đo cần thiết, làm tròn sáu chữ số cm.
- `CookingPot` front cũ cắt AABB ấm; rear cũ cắt AABB microwave.
  Mép nồi và ấm cách nhau 2,955458 cm theo X, không cần di chuyển model.
- `MakeupCompact` left cũ cắt `Dressing_Apartment_BedroomVase` tại Y 2904,388–2915,612.
  Đây là bình trang trí, không phải `TableLamp`; ảnh native cũ `View_22.png` phù hợp với bounds.
- `Saucepan` rear cũ có ấm lớn ở tiền cảnh (`View_06.png`), nhưng ray tâm không cắt AABB ấm.
  Không tạo regression giả rằng tâm chảo bị che; đưa camera gần hơn để giảm đồ tiền cảnh.

## Thay đổi

API `CitySmallPlacementCameras.cameras(name, location, size, yaw)` giữ năm hướng và target
ở origin Z + 45% chiều cao. Yaw vẫn theo local yaw của prop. Bốn override dùng cm:

| Prop / hướng | Bán kính ngang | Cao hơn target | Lý do |
| --- | ---: | ---: | --- |
| CookingPot / front | 12 | 40 | Eye trước mép ấm X +13,955458; nâng cao để thấy toàn nồi |
| CookingPot / rear | 35 | 25 | Eye trước mép microwave X −41,949999 |
| Saucepan / rear | 32 | 30 | Eye trước mép gần ấm X −33,955469; nâng cao để thấy lòng chảo |
| MakeupCompact / left | 28 | 12 | Eye trước mép bình Y −34,388020 |

Những camera khác giữ công thức cũ. Không thay FOV, actor, mesh, material, graphics hoặc cvar.
Các override áp dụng cho bố trí hiện tại; nếu dời prop/đồ lân cận cần cập nhật fixture và review lại.

## Kiểm chứng

- `python Tools/QA/TestCitySmallPlacementCameras.py`: bảy test; tái hiện ba ray cũ bị chắn,
  kiểm 15 ray tâm mới không cắt các hàng xóm trong fixture và 32 ray tới góc bounds
  ở bốn hướng đã sửa không cắt vật che tương ứng.
- Kiểm riêng phép giao đoạn/AABB, thứ tự năm hướng, hướng nhìn đúng target, roll 0,
  local yaw, và các prop không bị ảnh hưởng giữ camera cũ.
- `python -m py_compile Tools/QA/CitySmallPlacementCameras.py Tools/QA/TestCitySmallPlacementCameras.py`.
- `git diff --check -- Tools/QA/CitySmallPlacementCameras.py Tools/QA/TestCitySmallPlacementCameras.py`
  và file ghi chú này.

Bounds là kiểm tra bảo thủ với một tập hàng xóm, không phải mesh visibility hoặc proof hình ảnh.
Root cần tích hợp helper vào small scope, chụp native và mở ảnh năm hướng để kiểm crop,
near plane, silhouette, vật thể khác và ánh sáng trước khi nghiệm thu. Chưa chạy Unreal trong subtask.
