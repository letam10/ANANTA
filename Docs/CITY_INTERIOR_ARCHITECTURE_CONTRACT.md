# Nội thất kiến trúc — hợp đồng tích hợp 2026-10-08

Mục tiêu: thay quầy hộp, thêm chi tiết tường có chủ đích trong tám phòng vào được.
Không đổi nhân vật, dịch vụ, save, đường đi hoặc map qua Unreal khi root đang dựng HLOD.

## Dữ liệu chung

- Đơn vị cm, Z lên; mesh tâm X/Y và đáy Z=0; mặt trước Blender -Y, sau nhập UE +Y.
- Manifest `Assets/City/interior_architecture_manifest.json`: schemaVersion=1, units=cm;
  `meshes` và `materials` cùng định dạng finishing_manifest.json hiện có.
- Mỗi mesh: id, file (tương đối Assets/City), boundsCm {min,max,size}, materialSlots,
  triangles, sha256, source, license, visibleFront, lodRecommendation khi cần.
- Material dùng định dạng CityMaterials.create_material; texture PNG tối đa 2K.
- Mesh đã xuất phải đúng bounds dưới đây, dung sai 0,1 cm; không lấn ra ngoài để đặt an toàn.

| ID | Bounds cm | Vai trò | Trần tam giác |
| --- | --- | --- | --- |
| InteriorServiceDesk | [-55,-35,0] đến [55,35,85] | Quầy cửa/tay nắm/chân/viền bevel | 6000 |
| InteriorSlatPanel | [-120,-4,0] đến [120,4,220] | Nan gỗ trên nền tối, viền mảnh | 5000 |
| InteriorGalleryFrame | [-70,-3,0] đến [70,3,110] | Khung bevel, passe-partout, tranh gốc | 3000 |
| InteriorBotanicalFrame | [-70,-3,0] đến [70,3,110] | Cùng khung, tranh cây gốc khác | 3000 |

Material mới phải có tiền tố Arch_; không ghi đè material cũ.
Tranh tự thiết kế, có UV mặt in đúng, không dùng ảnh bản quyền không rõ nguồn.
Tận dụng PBR gỗ/kim loại hiện có khi phù hợp; ghi nguồn và giấy phép đầy đủ.

## Phân công độc lập

Agent assets chỉ sửa/tạo:
- Assets/City/InteriorArchitecture/** và interior_architecture_manifest.json.
- Tools/CityAssets/interior_architecture_*.py (mỗi file dưới 300 dòng).
- Tools/Editor/ImportCityInteriorArchitecture.py.
- Bằng chứng Saved/QA/CityInteriorArchitectureAssets/**.

Agent layout chỉ sửa/tạo:
- Tools/Editor/CityInteriorArchitecture.py.
- Tools/Editor/CityInteriorFinishes.py.
- Tools/QA/VerifyCityVenueDressing.py.
- Bằng chứng Saved/QA/CityInteriorArchitectureLayout*.json.

Root sở hữu HLOD, Content, runner/QA runtime, Docs tiến độ, import/map integration và Git.

## Hàm và bố trí

`CityInteriorArchitecture.apply_architecture(items, rooms) -> list[dict]` thuần Python.
Schema item giữ nguyên: label, mesh, location, yaw, scale, collision, material (tùy chọn).
Gọi ở cuối finish_items, giữ nhãn Dressing_<Room>_* và không sửa actor dịch vụ.
Thay ServiceTop/ServiceBase bằng một InteriorServiceDesk tại vị trí tương ứng;
đáy Z=15, scale Z theo chiều cao quầy gốc; collision=False để không chặn điểm E.
Thêm mảng ốp và tranh ở tường đặc của phòng phù hợp, tránh cửa sổ/cửa vào và đồ hiện có.
Không ép tất cả phòng cùng bố cục; tối đa 240 item nội thất tổng cộng.
Giữ hành lang giữa phòng 440 cm, không có đồ cản đường đi hoặc vươn ra ngoài tường.

## Kiểm chứng và báo cáo

Assets: headless Blender 5.2, --factory-startup --python-exit-code 1; CPU render để tránh tranh GPU.
Đọc skill Blender phù hợp, kiểm bounds/UV/degenerate/material slots/hash/FBX roundtrip và xem ảnh thật.
Không mở GUI, không chạy Unreal, không benchmark, không thêm agent, không commit.
Layout: kiểm tra thuần Python bằng bounds hợp đồng trước khi manifest thật có;
sau đó verifier tự nhận manifest thật. Không ghi manifest giả vào Assets.
Giữ các kiểm tra bounds/overlap/lối đi hiện có; chỉ loại cặp chồng hợp lệ có lý do cụ thể.
Mỗi agent hoàn thành và tự kiểm, báo cáo một lần tối đa 15 dòng; ghi rõ phần chưa kiểm trong UE.
