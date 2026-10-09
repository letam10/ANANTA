# Hợp đồng rà soát vòng tiếp theo

Cập nhật 2026-10-09. Checkpoint nguồn hiện tại: b99f3956f.
Root đang dựng HLOD đầy đủ và đẩy checkpoint; không sửa Content trong lúc này.

## Dữ liệu chung

- Unreal 5.8.3, Python authoring, C++ gameplay; đơn vị tọa độ cm.
- CityScene.instance_group(group, index): HISM theo cell/mesh/material/collision.
- group: cell, mesh, material, collision, instances; instance: location, scale, yaw.
- CityCivicDistrict.generate(layout); layout.add(mesh, location, yaw=0, collision=True).
- layout.box(material, center, size, collision=True); xác minh chữ ký ở CityLayout trước khi dùng.
- SITES, FLOOR_Z, ENTRY_CLEAR_WIDTH, access_lanes() trong CityCivicDistrict.py là nguồn tọa độ.
- Không thay nhân vật, save thường, giới hạn chất lượng Max hoặc tốc độ gameplay.
- Max: Epic 3, 1920x1080 native 100%, VSync off, cap 90; mục tiêu 90 chưa đạt.
- Saved/QA/CityMaxGraphics/Summary.json và FrameTimes.csv là số liệu mới, đủ tám dịch vụ.
- Saved/QA/CityCivic/View_00.png tới View_07.png là ảnh GPU hiện hành sau Nanite.

## Phân quyền

1. Render review chỉ được tạo Docs/CITY_RENDER_COST_REVIEW.md.
   Đọc source/engine source/log/profile; đề xuất tối đa ba thay đổi có bằng chứng.
   Không sửa code, cấu hình, Content hoặc chạy engine/benchmark.
2. Civic art review chỉ được tạo Docs/CITY_CIVIC_DRESSING_SPEC.md.
   Xem ảnh và asset bounds; đưa bố trí cụ thể cho bar/arcade, giữ làn vào/ra rộng 480 cm.
   Tái sử dụng asset chi tiết có sẵn, ngân sách instance và nhóm; không thêm đèn động tùy tiện.
   Không sửa code, asset, Content hoặc chạy Blender/Unreal.

Mỗi báo cáo dưới 200 dòng; ghi nguồn file/dòng và giới hạn bằng chứng.
Không tự spawn subagent. Tự kiểm file tồn tại/line budget rồi báo một lần, tối đa 15 dòng.

## Triển khai nội thất tiếp theo

- Civic implementation chỉ sở hữu Tools/Editor/CityCivicDressing.py, dưới 300 dòng.
- Đọc CITY_CIVIC_DRESSING_SPEC.md và hợp đồng này; tạo generate(layout) và furnish().
- generate(layout) đặt vật thể có va chạm bằng layout.add/box, không chặn access_lanes().
- furnish() chỉ tạo chi tiết không va chạm, actor prefix Living_CivicDressing_.
- Dùng CityScene helpers và asset có sẵn; không sửa source khác, Content hoặc chạy Unreal/Blender.
- Root tự tích hợp call vào CityCivicDistrict và ApplyCityExpansion sau khi HLOD đã kiểm xong.
- Tự kiểm bằng py_compile, kiểm tọa độ/bounds và line budget; ghi giới hạn bounds chưa xác minh.
