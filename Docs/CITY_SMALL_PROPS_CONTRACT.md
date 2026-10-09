# Hợp đồng đồ nhỏ trong phòng

Vòng 6,8 km; đọc cùng CITY_6800_CONTRACT.md. Unreal 5.8.3, Blender 5.2.

- Chỉ tạo Tools/CityAssets/small_*.py, Assets/City/SmallDetails/** và small_manifest.json.
- Không sửa các file của bộ MetroDetails, living, finishing hay C++/Content.
- Tám ID: CookingPot, Saucepan, KitchenBowl, CoffeeMug, MakeupCompact, ToyBlocks, RoomVase, BathroomSoap.
- Props ít để ý: hình học đơn giản, đúng tỷ lệ và dễ nhận ra, không cần chi tiết không thấy.
- CookingPot đường kính 22 cm; Saucepan thân 18 cm/tay 18 cm; KitchenBowl đường kính 17 cm.
- CoffeeMug cao 10 cm/đường kính 8 cm; MakeupCompact rộng 7 cm; ToyBlocks cụm 20 cm.
- RoomVase cao 22 cm; BathroomSoap hộp/khay rộng 12 cm.
- Mỗi model dưới 2.000 tris, tối đa ba material slots, origin đáy, FBX cm, +X trước, +Z lên.
- Reuse vật liệu/texture 1K của living_manifest.json; không nhân bản texture đã có.
- Manifest tương thích schemaVersion 1, units cm, upAxis Z, forwardAxis X, meshes/materials/sourceFiles.
- Mesh có id/file/boundsCm/triangles/materialSlots/sha256/source/license và lodRecommendation.
- Blender background, Cycles CPU tối đa hai thread, render tám yaw 0..315 bước 45 độ.
- Mỗi model tám ảnh thật và contact sheet gắn tên/hướng trong Saved/QA/CitySmallAssets.
- Audit hash, bounds, UV không rỗng/không suy biến, normals, ngân sách tris/material, 8 FBX và 64 ảnh.
- Không gọi render là duyệt thị giác; main agent xem ảnh, nhập và kiểm năm góc bố trí.
- Không chạy Unreal, không sửa save/model nhân vật, không commit/push, không tạo agent con.
- Source mỗi file dưới khoảng 300 dòng và 120 cột; report một lần tối đa 15 dòng sau self-check.
