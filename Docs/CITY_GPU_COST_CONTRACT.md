# Hợp đồng đọc chi phí render cho vòng tiếp theo

Chỉ phân tích đọc, không chạy Unreal/GPU/test/build và không sửa code trong lúc main ghi map.
Mục tiêu người dùng: Max tùy chỉnh native 1920x1080, 100%, VSync off, cap 90.
Không benchmark, giữ mọi frame; chưa có số đo bản 6,8 km.

## Dữ liệu đã có và định dạng

- Saved/QA/CityMaxGraphicsNaniteReservedOff/Summary.json: averageFps, p95WallMs,
  game_ms/render_ms/rhi_ms/gpu_ms, frames và observedSeconds.
- Saved/QA/CityMaxGraphicsNaniteReservedOff/RenderConfig.txt: cvar=value, output=WxH.
- Saved/Logs/CityMaxGraphicsPackagedProfile.log: profile một frame gameplay, các queue chồng nhau.
- Config/DefaultScalability.ini: @3 là Max tùy chỉnh, không còn Epic stock.
- Tools/Editor/CityMaterials.py, ImportCityAssets.py, Assets/City/*manifest.json: vật liệu/mesh.
- Có HISM/World Partition/Nanite Cube/LOD; reserved resources=0 mới chỉ có một Editor pass.
- Lumen/VirtualShadowMaps/Nanite Epic docs và source engine local là nguồn primary.

## Output và phạm vi

- Chỉ tạo Docs/CITY_GPU_COST_AUDIT.md, dưới 150 dòng, tiếng Việt ngắn rõ.
- Xác định bottleneck đã đo, không cộng async GPU queues hoặc so Editor với EXE như cùng môi trường.
- Kiểm facade/material translucent có làm mesh không dùng Nanite và có cơ hội glass giả
  riêng nhà không vào được; kính phòng tương tác phải giữ đúng hình ảnh.
- Đề xuất tối đa ba thử nghiệm nhỏ có cvar/files/phép đo và đánh đổi ảnh cụ thể.
- Không khẳng định 90 FPS/chất lượng tương đương trước khi đo; không tạo cvar không có trong UE 5.8.
- Khi browse, chỉ primary Epic docs; dẫn link gần kết luận. Source code có đường dẫn rõ.
- Self-check mọi con số/cvar được đối chiếu nguồn. Báo một lần tối đa 15 dòng.
- Không chạy workload, không edit code/asset/config/Docs file khác, spawn con hoặc commit/push.
