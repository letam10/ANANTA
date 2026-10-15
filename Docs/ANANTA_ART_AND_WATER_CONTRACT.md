# ANANTA Art and Water Contract

Version: W2/W3, 2026-10-16

## Hình ảnh thành phố

- Thành phố hiện đại, bán thực tế/AAA: kiến trúc, đường, vật liệu, ánh sáng,
  phương tiện và props giữ tỷ lệ và bề mặt thực tế.
- Chỉ character và NPC dùng phong cách anime. Không áp phong cách anime lên
  nhà, venue, rail, ga, sân bay, phương tiện, thuyền hoặc props môi trường.
- Mục tiêu hình ảnh là đẹp và khoảng 60 FPS. Ngân sách tham chiếu là
  `1000 / 60 = 16.667 ms` mỗi frame; đây là mục tiêu cho tới khi có headed
  frame-time mới trên tier GPU đã ghi.

## Review model và placement

- Model mới hoặc model sửa phải có review tám hướng yaw (`0, 45, 90, 135,
  180, 225, 270, 315` độ), cùng model id, bounds và source manifest.
- Placement quan trọng phải có năm góc camera sinh từ transform, sau khi áp yaw
  và scale. Review phải đọc transformed bounds, pivot, mặt đất, collision và
  hướng chính; không dùng bounds trước transform làm bằng chứng.
- Source, import/readback, visual headed và performance là các gate riêng.
  Build, config, static parse hoặc NullRHI không thay cho visual/FPS acceptance.

## Interaction và static dressing

Mỗi nhóm content phải ghi rõ interaction thật hoặc nhãn `static dressing` trong
manifest/hand-off của pha:
| Nhóm | Interaction tối thiểu hoặc nhãn |
| --- | --- |
| Nhà, venue | Cửa/service prompt, enter/exit hoặc `static dressing` nếu chỉ làm nền |
| NPC, character | Schedule/state/prompt thật hoặc `static dressing` |
| Prop | Dùng được với response/failure hoặc `static dressing` |
| Phương tiện, thuyền, xuồng | Điều khiển, boarding/exit, bounds hoặc `static dressing` |
| Rail, ga | Signal/stop, boarding/alighting hoặc `static dressing` |
| Sân bay | Aircraft/heli state, route/boarding hoặc `static dressing` |

Fixture hoặc prototype phải ghi rõ giới hạn và không được gọi là gameplay native.

## W1 water prototype contract

Prototype nằm tại `Prototypes/ThreeWater/` và phải đạt gate trước khi port sang
Unreal.

- Three.js ES modules, dependency được pin bằng `package-lock.json`.
- Một `PlaneGeometry` cố định cho nước; vertex/fragment shader cập nhật uniform,
  không rebuild geometry trong mỗi frame.
- Preset thấp có tối đa bốn sine/Gerstner-like waves. Không FFT, không buoyancy
  vật lý và không mô phỏng chất lỏng nặng.
- Three.js dùng Y-up: vị trí ngang là XZ, height là Y.
- Với `horizontalPosition = (x, z)`, direction đã chuẩn hóa và wave descriptor,
  dùng đúng công thức:
  ```text
  phase = 2π * (dot(normalize(direction), horizontalPosition) / wavelength
                - speed * time / wavelength) + phaseOffset
  height += amplitude * sin(phase)
  ```

- Normal được tính từ đạo hàm của cùng phase:
  `dHeight/dx = amplitude * (2π / wavelength) * cos(phase) * direction.x`,
  tương tự cho Z, sau đó chuẩn hóa `(-dHeight/dx, 1, -dHeight/dz)`.
- Foam/shore fade là lớp hiển thị tối thiểu theo boundary. Boundary preview và
  clamp rectangle chặn rìa map prototype; đây chưa phải collision gameplay.
- Boat trong prototype bob theo height/normal để kiểm tra thị giác, được phân
  loại là visual fixture/static dressing, không phải hệ buoyancy.

## Quy đổi Three.js sang Unreal

Contract mặc định giữ hướng ngang theo mapping:
```text
X_unreal = X_three
Y_unreal = Z_three
Z_unreal = Y_three
```

Vì vậy vector direction Three `[dx, dz]` thành hướng ngang Unreal `[dx, dy]`.
Wavelength, amplitude, speed và phaseOffset giữ cùng đơn vị; kiểm tra lại dấu
heading/handedness trong map Unreal trước khi chép shader.

## W1 gate và bằng chứng

Gate đạt khi `npm run check`, `npm run build` và browser smoke exit 0; browser
thấy sóng rõ, không seam khi camera di chuyển, orbit/free camera, foam/shore
fade, boundary preview, overlay frame-time/render-info và console sạch. Browser
smoke chỉ chứng minh prototype chạy; không tự chứng minh 60 FPS, GPU tier, AAA
toàn map hoặc Unreal runtime.

## W2 coastal water extension

- Biển prototype là một vùng rộng theo box boundary `minX=-700`, `maxX=700`,
  `minZ=-400`, `maxZ=400`; camera và boat bị clamp bằng margin lần lượt 14 m và
  8 m. Boundary preview là visual QA, còn collision gameplay native vẫn là gate
  riêng.
- `public/wave-spec.json` schema `ananta.three-water.wave-spec.v2` có SHA-256
  `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f`, bốn wave,
  units/axes, foam width 6 m, shoreline depth 16 m và ba cảnh cố định.
- Foam dùng một geometry cố định và fragment shader tính distance tới cạnh bờ;
  preset thấp không rebuild CPU mesh. Auto quick QA chạy `coast`, `beach_boat`
  và `offshore`, mỗi cảnh 10 giây.
- Browser run cache-bust mới kết thúc đủ ba report: coast `avg 17.67 ms,
  p95 18.60 ms, max 23.50 ms, outliers 0`; beach/boat `17.72/18.40/19.20 ms,
  0`; offshore `17.73/18.50/19.40 ms, 0`. Console error rỗng; đây là quick QA
  frame-time, chưa phải chứng nhận 60 FPS GPU.

## W3 Unreal water handoff

- `public/unreal-water-contract.json` giữ nguyên direction, wavelength,
  amplitude, speed và phase từ wave spec; mapping là `Three.X → UE.X`,
  `Three.Z → UE.Y`, `Three.Y → UE.Z`.
- Material Function `MF_AnantaWater` dự kiến trả `BaseColor`, `Normal`,
  `Roughness`, `Emissive` cho opaque water, normal động và foam rẻ. Boundary
  collision là actor/component riêng, không nằm trong shader; không có physics
  hoặc buoyancy trong pha này.
- W3 hiện **PARTIAL/UNVERIFIED**: contract và validator đã có, nhưng chưa có
  Unreal material graph readback thật, boundary collision readback native hoặc
  ảnh so sánh Three.js/Unreal cùng camera. Không claim 60 FPS trước F1.