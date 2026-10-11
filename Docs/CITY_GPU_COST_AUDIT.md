# Kiểm toán chi phí GPU cho cấu hình City Max

## Kết luận đo được

- Mục tiêu là 1920x1080 native, 100%, VSync tắt, cap 90 FPS; ngân sách mỗi frame là 11,11 ms.
- Ở quan sát gameplay 282,17 giây, 14.206 frame, trung bình đạt 50,34 FPS.
- `p95WallMs=24,979`, `meanWallMs=19,863`, `gpu_ms=18,735`, `render_ms=19,622`.
  Mốc GPU trung bình vượt ngân sách mục tiêu 7,62 ms; dữ liệu nghiêng rõ về giới hạn GPU.
- `game_ms=7,886` và `rhi_ms=3,780` không vượt mức GPU trung bình; các counter có thể trễ một frame.
- 52 frame vượt 33 ms, 10 frame vượt 50 ms, max 268,825 ms. Đuôi giật cần được đánh giá riêng.
- Báo cáo ghi đủ mọi frame và không chấp nhận ổn định 90 FPS. Không suy ra chất lượng/hiệu năng
  cho khu vực thành phố 6,8 km chưa được đo.

## Dấu vết ProfileGPU

- `CityMaxGraphicsPackagedProfile.log` ghi một frame Compute (1197) và một frame Graphics (1238),
  không cùng frame. Compute root là 9,654 ms; Graphics root là 14,748 ms.
- Compute nổi bật: `LumenScreenProbeGather` 6,425 ms (66,6%), gồm tích hợp 1,846 ms,
  ShortRangeAO 1,006 ms và trace/radiance cache 0,754 ms.
- Các mục Compute khác: `LumenSceneLighting` 1,851 ms (19,2%); `TranslucencyVolumeLighting`
  0,699 ms (7,2%). Đây là phân rã của frame 1197, không cộng với Graphics.
- Graphics nổi bật: `PostProcessing` 3,485 ms (23,6%), `LumenReflections` 1,568 ms (10,6%),
  `VirtualShadowMapProjection` 1,312 ms (8,9%). Đây là một frame đơn, không đại diện toàn bộ gameplay.
- Queue Compute và Graphics chồng lấn bất đồng thời. Không cộng các root 9,654 + 14,748 ms,
  cũng không đối chiếu trực tiếp ProfileGPU này với trung bình packaged gameplay.
- Log có metadata resolution 1280x720 lúc khởi động, sau đó ghi 1920x1080 trước profile.
  Đối chiếu `RenderConfig.txt` và metadata tại thời điểm capture trước khi dùng profile làm baseline.

## Vật liệu kính và Nanite

- `Assets/City/manifest.json`: FacadeResidential, FacadeCommercial và FacadeTower dùng slot
  `City_Glass`; vật liệu này không khai báo `opacity`. `CityMaterials.py` vì vậy tạo material Opaque
  và đánh dấu usage Nanite. Với điều kiện không có slot khác translucent, importer bật Nanite.
- `ImportCityAssets.py` chỉ bật Nanite ngoài nhóm `House_*` khi mọi material slot Opaque hoặc Masked.
  Các mesh `House_*` hiện bị loại khỏi nhánh bật Nanite, kể cả khi vật liệu opaque.
- `InteriorGlass` được tạo với `opacity` và `BLEND_TRANSLUCENT`; mesh dùng slot này không qua
  điều kiện Nanite. Kính phòng có tương tác nên giữ nguyên hình ảnh và hành vi.
- Cơ hội giả kính chỉ dành cho kính trang trí trên nhà ngoài không thể vào: thay bằng kính opaque/
  masked có màu tối, độ bóng và phản xạ phù hợp; sau đó mới cân nhắc bật Nanite có chọn lọc.
  Hiện chưa có phép đo chứng minh cách này tăng FPS; facade chính đã dùng `City_Glass` opaque.

## Tối đa ba thử nghiệm nhỏ

1. **Lumen GI:** trong `Config/DefaultScalability.ini`, thử
   `r.Lumen.ScreenProbeGather.DownsampleFactor=32` thay cho 24 ở `GlobalIlluminationQuality@3`.
   Đây là giá trị đã dùng ở quality@2. Đo lại cùng tuyến, độ phân giải, thời lượng và cvar; so
   `gpu_ms`, p95 và ProfileGPU. Đổi lại, ánh sáng gián tiếp và chi tiết AO có thể thô hơn.
2. **Lumen reflections:** thử `r.Lumen.Reflections.DownsampleFactor=4` ở quality@3 thay cho 2.
   Cvar đã có trong cấu hình; giá trị 4 là giả thuyết thử nghiệm. Đo cùng điều kiện và kiểm tra
   bề mặt kính/kim loại trong cảnh. Đổi lại, phản xạ nhỏ và biên phản xạ có thể kém nét.
3. **VSM directional:** thử `r.Shadow.Virtual.ResolutionLodBiasDirectional=0` ở quality@3,
   thay cho -1.5; giá trị 0 đã dùng ở quality@2. Đo lại GPU và chụp cùng góc có bóng xa/gần.
   Đổi lại, bóng xa có thể ít chi tiết hơn; nếu thời gian Projection không giảm thì bỏ thay đổi.

## Nguồn kiểm tra

- Số liệu tổng hợp và cvar thực chạy: `Saved/QA/CityMaxGraphicsNaniteReservedOff/Summary.json`,
  `Saved/QA/CityMaxGraphicsNaniteReservedOff/RenderConfig.txt`.
- Một frame ProfileGPU: `Saved/Logs/CityMaxGraphicsPackagedProfile.log`, các dòng quanh 1003–1243.
- Cấu hình thử nghiệm: `Config/DefaultScalability.ini`.
- Quy tắc graph vật liệu: `Tools/Editor/CityMaterials.py`; quy tắc bật Nanite:
  `Tools/Editor/ImportCityAssets.py`.
- Slot kính và khuyến nghị LOD facade: `Assets/City/manifest.json`.
