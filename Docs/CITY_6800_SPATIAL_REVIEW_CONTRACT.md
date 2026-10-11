# Hợp đồng rà HISM / streaming 6,8 km

## Mục tiêu

Rà độc lập bounds, transform và World Partition trong nguồn đã tạo map.
Chỉ ghi bằng chứng hoặc giả thuyết; không tự nhận đây là nguyên nhân PageFault.

## Dữ liệu dùng chung

- Repo: D:\GAME\ANANTA, Unreal 5.8.3, branch codex/city-expansion.
- CityScene.py instance_group(group, index): group.cell = [cx, cy].
- group.origin nếu có thay origin mặc định; origin là tọa độ world theo cm.
- group.instances chứa location world, scale và yaw; add_instances world_space=True.
- HISM nhóm theo cell; actor is_spatially_loaded=True trừ biển lớn hoặc actor quản lý riêng.
- Apply 6,8 km: 85.386 nhóm, 1.660.761 instance; HLOD readback PASS 3.557 proxy.
- Tools/Editor/CityScene.py và các module City* đặt geometry.
- Assets/City/*manifest.json, Saved/QA/CityMapBuild.json, CityExpansionApplied.json là evidence.
- Nếu schema khác mô tả: ghi trường thực đã thấy, không đoán cấu trúc.
- EXE/native capture đang PageFault; runner QA riêng giữ personal save.

## Phân công

Agent chỉ được tạo Docs/CITY_6800_SPATIAL_REVIEW.md, tối đa khoảng 150 dòng.
Đọc source, manifest và JSON hiện có; đọc engine source nếu cần.
Root sở hữu các source/runner khác và status/integration docs.

## Kiểm chứng

- Nêu source line và các sai lệch world/local, origin, cây HISM/bounds hoặc actor luôn nạp.
- Đối chiếu phân nhóm thực từ dữ liệu có sẵn nếu khả thi; không scan binary bằng suy đoán.
- Phân biệt bounds nguồn với descriptor thật chưa đọc được.
- git diff --check -- Docs/CITY_6800_SPATIAL_REVIEW.md phải PASS.
- Báo cáo một lần tối đa 15 dòng, gồm file/checks/open issues.

## Không làm

Không chạy Unreal, game, Blender, build, commandlet hoặc benchmark.
Không sửa config/source/map/save, không commit/push, không spawn agent khác.
Không suy ra GPU hay hình ảnh đạt từ cấu trúc; không lặp các gate đã PASS.
