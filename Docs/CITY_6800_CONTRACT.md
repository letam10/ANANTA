# Hợp đồng vòng thành phố 6,8 km

Cập nhật 2026-10-09 theo yêu cầu tăng gấp đôi mỗi chiều lần nữa.

## Chuẩn chung

- Unreal 5.8.3; centimet; +Z lên, +X phía trước của model mới.
- GRID_EXTENT = 336000; WORLD_EXTENT = 240000 * sqrt(2); BLOCK = 12000.
- Chiều dài/rộng 6788,2251 m, gấp đôi bản 3394,11255 m; diện tích gấp bốn.
- Giữ SEED 81026 và tọa độ nhiệm vụ, dịch vụ, bến tàu đang có.
- Layout.add(mesh, location, scale=(1,1,1), yaw=0, material=None, collision=True, hidden=False).
- Layout.box(material, location, size, collision=True); Layout.collider(location, size, yaw=0).
- Layout.export schemaVersion 2, units cm; groups gồm cell/origin/mesh/material/collision/hidden/instances.
- HISM theo cell 120 m, dùng chung mesh/material; nhà không vào được chỉ có vỏ.
- Biển nối vùng cảng ra mép đông và nam, mặt nước có thể vượt ranh giới để tạo chân trời.
- Không để mặt đất/vành đai chắn ngang vùng biển. Có collider kín ở rìa phạm vi chơi.
- Không sửa nhân vật hoặc save thường; QA dùng ANANTA_City_QA.
- Kiểm tám hướng model: yaw 0/45/90/135/180/225/270/315, nhìn hơi cao để thấy bề mặt.
- Kiểm năm góc bố trí: trước/sau/trái/phải/trên chéo; ảnh phải từ scene thực.
- Chỉ đánh dấu kiểm thị giác khi đã xem ảnh; render xong chưa phải duyệt đẹp.
- Max native 1920x1080, 100%, VSync off, cap 90; giữ mọi frame trong hành trình vài phút.
- Không dùng benchmark, không đổi tốc độ gameplay để tăng FPS.

## Phân công độc lập, không ghi đè

### Thành phố và bờ biển

- Được sửa CityExpansionData.py, CityExpansionLayout.py, CityExpansionLandscape.py, CityCoastalDistrict.py.
- Được thêm Tools/Editor/CityMetroDistrict.py và Tools/QA/VerifyCity6800Layout.py.
- Module metro chỉ dùng Layout API; cung cấp RESERVES và generate(layout), không import Data ở cấp module.
- Thêm khu nhà ga hai đường ray và hai sân ga, sân bay nhỏ/helipad, khách sạn/nhà hàng/nhà hát/rạp phim.
- Bố trí mới ngoài lõi cũ; không cắt đường chính, lối vào rộng ít nhất 220 cm.
- Các model mới dùng đúng ID: FireEngine, PassengerTrain, Helicopter, CivilianPlane, Rowboat.
- Khu nhà máy dùng geometry chia sẻ, không dựng chi tiết bên trong nhà không vào được.
- Chỉ tạo source/audit trong Saved; không chạy Unreal, không sửa Content hay C++.
- Self-check: Python py_compile; VerifyCity6800Layout.py PASS; kiểm dimensions, coast, lối đi/bounds.

### Model giao thông và tám hướng

- Chỉ tạo Tools/CityAssets/metro_*.py, Assets/City/MetroDetails/**, Assets/City/metro_manifest.json.
- Tạo năm model ID trên, có hình dáng/chức năng dễ nhận ra, PBR dùng chung, UV và kích thước thật.
- Budget tris: FireEngine 18000; PassengerTrain 22000; Helicopter 16000; CivilianPlane 22000; Rowboat 5000.
- FBX cm, origin đáy giữa, max 5 material slots; không thay model nhân vật hay asset đã có.
- Manifest tương thích living_manifest.json: schemaVersion/units/upAxis/forwardAxis/meshes/materials/sourceFiles.
- meshes gồm id/file/boundsCm/triangles/materialSlots/sha256/source/license, budget và forwardAxis.
- Render thực tám hướng mỗi model vào Saved/QA/CityMetroAssets, contact sheet đọc rõ model/hướng.
- Viết audit số lượng/triangles/UV/material/hash; không gọi render là visual acceptance.
- Self-check Blender background build + audit exit 0; năm FBX và 40 ảnh thực có đủ.
- Không chạy Unreal, không sửa Content, C++ hay module city expansion; không commit/push.

## Main agent

- Native EXE baseline, C++ giới hạn/va chạm, import và apply map, kiểm năm góc bố trí.
- Thuyền chèo và tàu chạy là gameplay riêng, model tĩnh chưa chứng minh chơi được.
- Build/HLOD/runtime/collision/save/reload/GPU rồi ghi kết quả và commit/push từng checkpoint.
- Không khẳng định 90 FPS khi chưa đạt; không ghi các tính năng chưa test thành đã hoàn thành.
