# ANANTA Art and Water Contract

Version: V1 + W2/W3, 2026-10-20

## Current receipt — 2026-10-20

- W1/W2 fresh bounded browser gate: 68/68 contract checks, check/build/spec
  validator PASS, three 10-second reports, orbit/free/foam/boundary controls,
  zero warning/error console entries. Browser timing is not Unreal FPS evidence.
- W3 isolated contract map `/Game/ANANTA/WaterW3_20261020/W3_Comparison` now has
  `MF_WaveSpec` (13 nodes) and opaque `M_WaveSpec_Opaque`, with actual readback of
  BaseColor/Normal/Roughness/Emissive and exact four hashed wave tuples. Function
  inputs are WorldPositionCm/TimeSeconds; wave values are generated literals from
  the pinned JSON, not an editable runtime Wave[] array.
- Convert world position as `UEcm = 100 * (Three.X, Three.Z, Three.Y)`; HLSL
  uses `P.xy/100`. Normal is world-space; tangent_space_normal is false. Collision
  is four separate BlockAll actors. Native rays hit x=+/-70000 and y=+/-40000 cm.
- Three/Unreal coast, beach_boat and offshore images use matching transforms,
  1422x800 and vertical FOV 48 degrees. UE horizontal FOV is
  `2*atan(tan(48/2)*1422/800) = 76.7157600295933` degrees. Reference camera
  actors use 16:9 and corresponding horizontal FOV 76.72447378326581 degrees.
- Evidence: `Tools/Continuation_20261020/W3_native_readback.json`, `W3_review.json`
  and six W3_Three/W3_UE images. This is an isolated normal-only shader port:
  no WPO, physics or buoyancy. Lighting/time/color differ between renderers;
  wave-band direction is comparable, not pixel-identical or AAA art acceptance.
- Existing City/Coastal maps and materials remain unchanged. Boundary rays do
  not replace gameplay boat/camera traversal. Native city integration, hero art,
  normal-input streaming and headed 60 FPS remain unverified.
- V1 rules below remain fixed. A1/A2 source audit found missing native hero
  import/review and a historical AO-as-Normal assignment in pre-existing untracked
  A1 output. Do not adopt that output or expand the map before a corrected hero
  package has material/channel readback, fresh eight-direction shading review
  and five-angle placement review from actual transformed bounds.

The dated W1-W3 receipts below are historical context; this current receipt and
its linked evidence take precedence for the 2026-10-20 isolated W3 scope.

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
## V1 — Visual bible: hiện đại + anime có kiểm soát

Trạng thái: **CONTRACT DONE; hero sample UNVERIFIED**. Phần này khóa ngôn ngữ
hình ảnh cho mẫu hero trước khi mở rộng toàn map.

### Ranh giới phong cách

- Kiến trúc, đường phố, xe, rail, ga, sân bay, biển, thuyền và props môi trường
  dùng hiện đại, bán thực tế: hình khối có bevel hợp lý, PBR, vật liệu có scale
  thật, ánh sáng và bóng tiếp xúc đọc được. Không dùng cel ramp hoặc outline anime
  cho môi trường.
- Character/NPC dùng anime có kiểm soát qua silhouette, tỉ lệ khuôn mặt, tóc và
  màu accent. Bàn chân, chiều cao, bóng, exposure và mức roughness vẫn phải khớp
  với mặt đường, nội thất, xe và ánh sáng của thế giới.
- Anime là thuộc tính của character/NPC, không lan sang nhà, venue, rail, ga,
  sân bay, phương tiện, biển hoặc props. Asset nào cố ý lệch chuẩn phải ghi rõ
  lý do trong manifest và review package.

### Palette cố định

Palette là điểm bắt đầu chung cho hero review; texture và ánh sáng được phép tạo
biến thiên trong cùng family, không được đổi sang phong cách phẳng hoặc neon ngoài
accent đã ghi.

| Nhóm | Màu tham chiếu | Quy tắc |
| --- | --- | --- |
| Asphalt/road | `#272C31` | Dark neutral, roughness cao, có variation nhẹ theo wear |
| Concrete/sidewalk | `#A7ABA7` | Neutral lạnh, normal nhỏ, không đen viền |
| Facade stone/plaster | `#D1C7B6` | Warm neutral, value trung bình để bắt bóng |
| Dark metal/rail | `#34434A` | PBR metal, edge wear tiết chế |
| Glass/water reflection | `#4B7480` | Blue-gray, phản xạ theo lighting reference |
| Vegetation | `#43604A` | Green tự nhiên, không toon green |
| Sand/coast | `#C6AA78` | Warm muted, nối với palette đường phố |
| Wayfinding/safety | `#E05A47` | Accent có chủ đích cho biển báo, không phủ toàn scene |
| Character accent | `#D77A6A`, `#6A8FD4`, `#E5B84B` | Chỉ dùng cho cloth, hair hoặc accessory của character/NPC |

### Material rules

- World materials dùng BaseColor, Normal, Roughness và metallic/specular theo
  PBR. Asphalt, concrete và facade cần roughness/normal variation theo scale,
  không dùng một màu phẳng cho cả block.
- Character material phải có các nhóm riêng: `skin`, `hair`, `cloth`, `eye` và
  `accessory`. Skin giữ highlight mềm và không wax; hair giữ hướng sợi hoặc
  anisotropy khi pipeline hỗ trợ; cloth có weave/seam normal; eye tách cornea,
  iris và highlight; accessory dùng vật liệu kim loại/nhựa PBR đúng loại.
- Outline/rim chỉ là tùy chọn cho character/NPC khi giúp tách silhouette. Nó phải
  cùng exposure với scene, mảnh và ổn định theo khoảng cách; không dùng outline
  để che lỗi topology, thiếu shadow hoặc sai scale.
- Character và NPC dùng cùng tone mapping, key/fill balance, contact shadow và
  exposure với thế giới. Không tăng saturation/emissive để làm anime nổi bật một
  cách tách rời khỏi ánh sáng chung.
- Trước khi tạo texture mới, tìm material/texture hiện có theo material key,
  kích thước, màu space, semantic và hash. Nếu texture tương đương, reuse asset
  hiện có; nếu khác, ghi lý do và hash mới trong manifest.

### Scale reference

Mốc đo chuẩn là character rig cao `1.75 m`, với eye height review `1.60 m`. Các
bounds dưới đây là reference để kiểm tra transform, không thay thế readback sau
yaw/scale:

- Cửa người: cao `2.10 m`, rộng `0.90 m`; bậc/cửa phải cho NPC 1.75 m đứng đúng
  mặt đất và có clearance được ghi trong placement review.
- Curb sidewalk: `0.15 m`; lane đường: `3.50 m`; vạch và bollard phải được đo
  theo lane/curb, không scale bằng mắt.
- Sedan hero: khoảng `4.60 x 1.80 x 1.50 m`; bus/xe tải ghi bounds riêng theo
  model và collision, không copy scale sedan.
- Rail dùng gauge reference `1.435 m`; platform height, gap và boarding marker
  ghi theo readback của ga cụ thể.
- Camera ngang tầm người đặt eye height `1.60 m` trước khi chụp street, coast,
  traffic hoặc NPC. Camera trên cao chỉ là view bổ sung, không phải bằng chứng
  hero duy nhất.

### Lighting reference

- Day street: sun/sky physically motivated, neutral white balance, shadow/contact
  rõ ở curb, cửa, bánh xe và chân NPC; không dùng toon ramp cho world.
- Interior: key light có nguồn trong phòng, fill mềm, bounce/occlusion vừa đủ;
  exposure phải nối được với cửa ra street trong cùng review sequence.
- Coast: key direction phải làm đọc được crest, normal và foam; nước giữ cùng
  tone mapping với sand/seawall và không phát sáng giả.
- Traffic: camera thấp ngang người/xe, headlight và phản xạ mặt đường chỉ là
  accent theo nguồn sáng; không để emissive biến phương tiện thành biển màu.
- NPC: key/fill/rim có thể hỗ trợ silhouette anime nhưng không được tách NPC khỏi
  shadow/contact và color response của mặt đường, xe hoặc nội thất.
- Mỗi capture ghi camera transform, lens/FOV, exposure, renderer, resolution và
  lighting preset cùng asset manifest để review có thể tái lập.

### Hero review cameras và danh sách asset

Mỗi hero sample bắt buộc có camera ngang tầm người ở năm ngữ cảnh: `street`,
`interior`, `coast`, `traffic`, `npc`. Mỗi model vẫn giữ review tám hướng; mỗi
placement quan trọng giữ năm góc sinh từ transform và transformed bounds.

| Asset ID | Vai trò | Phong cách | Camera hero | Interaction/dressing |
| --- | --- | --- | --- | --- |
| `Hero_Street_Block_Modern01` | block kiến trúc và mặt tiền | hiện đại bán thực tế | street | door/service prompt hoặc static dressing |
| `Hero_Interior_Lobby01` | lobby, cửa và vật liệu nội thất | hiện đại bán thực tế | interior | enter/exit hoặc static dressing |
| `Hero_Coast_Seawall01` | seawall, sand, foam edge | hiện đại bán thực tế | coast | boundary/shore dressing, collision ghi riêng |
| `Hero_Traffic_Sedan01` | xe sedan và wheel/road contact | hiện đại bán thực tế | traffic | drive/board hoặc static dressing |
| `Hero_Rail_Station01` | ga, platform, rail signal | hiện đại bán thực tế | traffic/street | signal/boarding hoặc static dressing |
| `Hero_NPC_Civilian_A01` | character dân cư | anime có kiểm soát | npc/street | schedule/prompt hoặc static dressing |
| `Hero_NPC_Transit_B01` | NPC nhà ga/sân bay | anime có kiểm soát | npc/traffic | schedule/boarding hoặc static dressing |
| `Hero_Prop_StreetFurniture01` | sign, bench, bollard, lamp | hiện đại bán thực tế | street | interaction hoặc static dressing |

Mỗi asset trong bảng phải có manifest gồm `AssetId`, provenance/source URI,
licence, import revision, pivot, bounds trước và sau yaw/scale, LOD0/LOD1/LOD2,
triangle budget, collision policy, material keys, texture SHA-256 và perceptual
hash. Texture đã tương đương phải trỏ tới asset dùng chung thay vì tạo bản sao.
Review package phải lưu camera transforms, ảnh tám hướng, năm placement views và
kết quả đọc transformed bounds.

### V1 gate trước khi mở rộng map

V1 chỉ đạt khi hero sample có đủ:

- palette và material rules ở trên được áp dụng nhất quán cho world và
  character/NPC;
- scale reference có human/NPC, door, curb, lane, vehicle và rail readback;
- lighting reference có day street, interior, coast, traffic và NPC;
- camera review có góc ngang tầm người, không chỉ camera trên cao;
- hero asset list có provenance/licence, pivot, transformed bounds, LOD,
  collision và texture hashes;
- texture reuse audit không tạo texture trùng khi material tương đương đã tồn tại.

Cho tới khi checklist này có ảnh/readback mới, không mở rộng toàn map hoặc gọi
visual bible là visual AAA acceptance. Đây là contract V1; implementation review
và chất lượng hero sample vẫn phải được ghi riêng trong handoff của pha sau.
