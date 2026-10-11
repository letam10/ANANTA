# Hợp đồng sửa sàn thuyền và xem tám hướng

## Mục tiêu / nguồn đã xác nhận

Repo D:\GAME\ANANTA; Blender 5.2 pipeline Tools/CityAssets, UE 5.8.3.
Model Rowboat hiện 3.732 tris, bounds cm min [-208.8749,-90.5,0], max [208.8749,90.5,88.7].
Actor ở WaterLevel=-120 cm; BodyMesh relative Z=-25 cm; keel floor top khoảng 5,5 cm local.
Ảnh native View_15..19 cho thấy nước cắt qua sàn. Không đổi actor/collider/draught để che lỗi.
Thêm sàn trong kín trên local waterline=25 cm, mặt đi lại cao hơn nước khoảng 10 cm.
Sàn phải nằm trong thành vỏ, giữ keel dưới nước; tránh lỗ/gap làm lộ mặt nước.
Ưu tiên texture gỗ PBR đã có trong living_manifest.json; giữ shared texture, không tải asset.

## Interface / dữ liệu chung

- metro_boat.rowboat() trả merged mesh tên Rowboat, +X front/+Z up, pivot base center.
- metro_build.export(obj) trả record/audit; mesh_audit yêu cầu UV, không tri/UV suy biến.
- manifest schemaVersion=1, meshes đủ năm ID, cm, sourceFiles sha256; importer đọc material ID.
- Ngân sách Rowboat <=5.000 tris, <=5 material slots; bounds/origin giữ sai số <=0,03 cm.
- Bốn FBX khác phải byte/hash giữ nguyên; chỉ Rowboat được export lại.
- Giữ nguyên actor và đường asset đang dùng trong CityScene/importer, không đổi tên hoặc đường dẫn.
- Root sở hữu mọi code Unreal, Tools/Editor, camera QA và status/integration docs.

## Phân công độc quyền

Agent được sửa Tools/CityAssets/metro_boat.py, metro_build.py, metro_render.py,
ba bản copy tương ứng Assets/City/MetroDetails/Sources/Generator/, metro_manifest.json,
Assets/City/MetroDetails/MetroDetails.blend và Meshes/Rowboat.fbx.
Được tạo Docs/CITY_ROWBOAT_DRY_FLOOR_ROUND.md và evidence dưới Saved/QA/CityMetroAssets.
Chỉ thêm CLI --asset Rowboat nếu cần build/render riêng; mặc định full pipeline giữ hành vi cũ.
Không sửa shared geometry/material module hoặc model khác, không đổi texture byte.

## Done / kiểm chứng

- Geometry/UV/hash/FBX roundtrip PASS; kiểm mặt sàn cao hơn local waterline và nằm trong hull.
- Báo cáo triangles/materials/bounds, hash bốn FBX khác giữ nguyên, texture provenance.
- Render tám hướng mới của Rowboat bằng Cycles CPU, hai thread; giữ ảnh các model khác.
- Parent sẽ mở ảnh, import Unreal, kiểm physics và năm góc; agent không nhận visual/gameplay cuối.
- Python compile và git diff --check trên file sở hữu PASS; mỗi file khoảng <300 dòng/<120 cột.
- Không chạy Unreal/game, không compile C++, commit/push, hoặc spawn agent.
- Báo cáo một lần tối đa 15 dòng: files/checks/render paths/open issues.
