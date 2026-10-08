# Nghiên cứu tối ưu render — 2026-10-08

Phạm vi: Unreal Engine 5.8.3, thành phố liên tục, giữ model nhân vật.
Đây là nghiên cứu và thứ tự kiểm chứng; chưa phải kết quả tăng FPS do thay đổi mới.
Tiến độ thực thi duy nhất: [CITY_EXECUTION_STATUS.md](CITY_EXECUTION_STATUS.md).

## 1. Cơ chế người dùng mô tả

| Cơ chế | Công việc được giảm | Giới hạn cần kiểm tra |
| --- | --- | --- |
| Frustum culling | Bỏ phần ngoài khung nhìn camera khỏi lượt vẽ chính | Vẫn cần một số dữ liệu cho bóng/phản chiếu |
| Occlusion culling | Bỏ vật bị tường/nhà che kín | Bounds sai hoặc quay nhanh có thể làm vật xuất hiện trễ |
| Nanite | Chọn và cull cụm hình học theo mức chi tiết cần trên màn hình | Không xóa chi phí shader/ánh sáng/overdraw |
| LOD/HLOD | Dùng hình học đơn giản, gộp cụm xa thành proxy | Phải giữ silhouette, vật liệu và cửa sổ sáng |
| World Partition | Nạp/dỡ các ô theo nguồn streaming | Cần nạp trước; không dỡ ngay mỗi khi quay lưng |
| Distance culling | Ngừng vẽ đồ nhỏ ở xa | Không áp dụng khoảng cách ngắn cho nhà mốc lớn |
| Texture streaming | Chỉ giữ mip cần thiết theo khoảng cách | Pool thiếu gây texture mờ/nạp lại liên tục |

Unreal có frustum culling và hardware occlusion queries mặc định.
Hardware query có thể đọc kết quả trễ một frame; không cam kết mọi vật xuất hiện tức thì tuyệt đối.
Frustum culling không đợi nạp asset từ đĩa nếu asset vẫn nằm trong vùng đã nạp.
Không viết vòng lặp SetActorHiddenInGame theo hướng camera: dễ ảnh hưởng bóng, phản chiếu và logic khác.
Culling ở renderer không đồng nghĩa xóa vật thể hoặc ngừng mọi mô phỏng gameplay.
HZB là một kỹ thuật kiểm tra che khuất; không đồng nhất cvar HZB của primitive thường với culling Nanite.

Nguồn: [Epic — Visibility and Occlusion Culling][culling], [Nanite][nanite], [World Partition HLOD][hlod].

## 2. “12 tia xuống 3–4”

Không có số tia mặc định chung cho tất cả ánh sáng, engine hoặc mức chất lượng.

- Nếu là **Max Bounces** trong Blender/Cycles: đó là số lần bật của đường đi ánh sáng.
  Giảm 12 xuống 4 có thể rút ngắn render nhưng thay đổi ánh sáng gián tiếp, kính và phản xạ nhiều lớp.
  Chưa có ảnh thiết lập gốc của người dùng nên đây là cách diễn giải, không khẳng định nguồn con số.
- Với **Virtual Shadow Maps / SMRT** của Unreal: Epic ghi mức Epic dùng 8 rays cho local/directional.
  Rays ít hơn có thể tăng nhiễu vùng bóng mềm; samples trên mỗi ray ít hơn giới hạn độ mềm đạt được.
  Tài liệu nêu 4–8 samples/ray thường phù hợp; không phải chỉ dẫn hạ mọi hiệu ứng về 4.
- Bốn cvar liên quan: `r.Shadow.Virtual.SMRT.RayCountLocal`, `RayCountDirectional`,
  `r.Shadow.Virtual.SMRT.SamplesPerRayLocal`, `SamplesPerRayDirectional`.
  Hai tên viết ngắn cùng dùng tiền tố `r.Shadow.Virtual.SMRT.`.
- Với **Lumen**: ưu tiên nhóm scalability High và ngân sách GI/reflection phù hợp.
  Mục tiêu 60 FPS trong hướng dẫn Epic là ngân sách thiết kế, không bảo đảm FPS của game này.

Nguồn: [Blender — Light Paths][bounces], [Epic — Virtual Shadow Maps][vsm], [Lumen Performance Guide][lumen].

## 3. “4096 samples xuống 1024”

Samples trong Cycles/Path Tracer là số mẫu tính cho pixel/ảnh, không phải số mẫu mặc định của từng model.
4096 xuống 1024 giảm trần mẫu còn một phần tư; không suy ra FPS toàn game tăng bốn lần.
Thời gian thực tế còn phụ thuộc adaptive sampling, denoise, shader, cảnh và phần chuẩn bị render.
Giảm samples có thể đủ cho ảnh preview; cần xem nhiễu, mất chi tiết hoặc nhấp nháy trong chuyển động.

Game này đang chọn Lumen phần mềm và tắt hardware ray tracing trong cấu hình dự án.
Chỉnh samples của ảnh Cycles hoặc Path Tracer không tự làm model FBX nhẹ hơn khi chơi Unreal.
Muốn model nhẹ hơn: kiểm soát mesh/LOD/Nanite, số material, shader, collision và kích thước texture.
Nếu 4096/1024 là độ phân giải texture hoặc shadow map thì đó lại là thông số khác.
Không giảm đồng loạt texture 4K xuống 1K: giữ độ nét vật gần, để mip streaming phục vụ vật xa.

Nguồn: [Blender — Sampling][sampling], [Epic — Path Tracer][pathtracer].

## 4. Đối chiếu game và việc tiếp theo

- `Config/DefaultEngine.ini`: Lumen GI/reflection, mesh distance fields, Virtual Shadow Maps;
  `r.RayTracing=False`, DX12/SM6.
- `Config/DefaultScalability.ini`: GI downsample 32, reflection downsample 2 ở High;
  texture pool 3000 MB, TSR history 100, điều chỉnh LOD bias bóng.
- User settings chọn quality 2 (High). Preset UE 5.8.3 ở mức này: VSM directional 8 rays x 4 samples/ray;
  local 4 rays x 4 samples/ray. Đèn local đã dùng mức 4 rays trong preset, không có bước giảm 12 xuống 4.
- Không tìm thấy control dự án cho 12 rays hoặc 4096 samples. Giá trị 4096 trong log là số trang VSM
  hoặc kích thước surface cache Lumen; không đổi chúng như số mẫu render.
- Đã ghi cvar sau khi bản runtime hiện tại sẵn sàng: `Saved/QA/CityFinishing/RenderConfig.txt`.
  Occlusion queries bật; Nanite frustum/HZB đều 1. `r.HZBOcclusion=0` của primitive thường
  không có nghĩa tắt toàn bộ occlusion. Quality shadow/GI/reflection đều 2; texture pool 3000 MB.
  VSM xác nhận directional 8 rays/local 4 rays, cả hai 4 samples/ray; hardware RT tắt.
  TSR xuất 1080p, `r.ScreenPercentage=83.3333`, tương ứng nội bộ khoảng 1600 × 900.
- Map đã có World Partition, HISM và Nanite cho các mesh phù hợp.
- HLOD mở rộng có 288 cụm; lượt cũ dừng để sửa vật liệu, chưa có toàn bộ proxy cuối được nghiệm thu.
- Shader/template HLOD đã mở lại kiểm tra PBR và NightAmount; mẫu X0_Y0 đã bake và đọc lại đủ bốn kênh.
  Texture emissive thực có dữ liệu biến thiên; toàn bộ 288 cụm và chuyển tiếp ngày/đêm còn cần kiểm chứng.
- Không sửa render config trong vòng nghiên cứu này; cần phân biệt cvar có hiệu lực với giá trị cấu hình.

Thứ tự thực hiện và điều kiện nhận:

1. Đã ghi cvar thực tế sau scalability; giữ log này làm mốc đối chiếu cho các lượt tối ưu tiếp theo.
2. Kiểm tra một proxy HLOD với vật liệu mới, rồi dựng đầy đủ và thử chuyển ô khi đi bộ/lái xe.
3. Quan sát một lượt chơi ngắn: quay 180°, nhìn qua góc nhà, vào/ra nội thất, chạy nhanh ngày/chiều xanh.
4. Dùng `stat initviews`, thống kê Nanite, CPU/GPU frame time và streaming để xác định điểm nghẽn.
5. Chỉ thử giảm rays/samples khi phần bóng/GI là điểm nghẽn; so ảnh và chuyển động trước/sau.
6. Giữ thay đổi khi giảm frame time mà không mất nhà, bóng nhấp nháy hoặc texture nạp trễ rõ rệt.
7. Cập nhật tiến độ, commit/push; đóng gói lại trước khi nhận chất lượng bản phát hành.

Không dùng benchmark. Lượt chơi hiện có chưa chứng minh lợi ích của các thay đổi chưa thực hiện.

## Nguồn chính thức đã truy cập

[culling]: https://dev.epicgames.com/documentation/en-us/unreal-engine/visibility-and-occlusion-culling-in-unreal-engine
[nanite]: https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
[hlod]: https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine
[vsm]: https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
[lumen]: https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-performance-guide-for-unreal-engine
[pathtracer]: https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine
[bounces]: https://docs.blender.org/manual/en/latest/render/cycles/render_settings/light_paths.html
[sampling]: https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
