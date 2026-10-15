# ANANTA Master Roadmap

Ngày cập nhật: 2026-10-15
Checkout: `D:\GAME\ANANTA`
Engine: Unreal Engine 5.8.3
Nhánh làm việc: `codex/coastal-interiors-20261014`

Tài liệu này là roadmap duy nhất của chương trình ANANTA. Trạng thái từng chat,
lệnh và evidence mới nằm trong [ANANTA_CURRENT_HANDOFF.md](ANANTA_CURRENT_HANDOFF.md).
[COASTAL_FINAL_HANDOFF_20261015.md](COASTAL_FINAL_HANDOFF_20261015.md) chỉ là
snapshot lịch sử của tranche coastal và không được sửa để biến thành evidence mới.
Các handoff cũ khác là tài liệu lịch sử.

## Mục tiêu chương trình

- Thành phố nguyên bản, bán thực tế, có nhiều building vào được và có tương tác.
- Model/prop có pivot, hướng trục, vật liệu, LOD, collision và provenance rõ ràng.
- Model mới hoặc model sửa có review 8 hướng.
- Placement quan trọng có review 5 góc từ transform và transformed bounds.
- Thành phố có biển rộng nhưng khóa biên, đường phố, phương tiện, rail hai chiều,
  ga, sân bay, nhà hàng, khách sạn, opera, cinema, cafe, bar, công viên, hồ bơi,
  helipad, factory, police/fire/clinic và prop nhỏ trong nhà.
- Tối ưu và đo riêng cho RTX 3050 và RTX 4060 Laptop.
- Chỉ gọi một gate đạt khi có lệnh, exit code và evidence mới phù hợp với gate đó.

## Bất biến

- Không sửa, stage, xóa hoặc commit `AGENTS.md`; giữ mọi dirty map/ExternalActors có sẵn.
- Headless là mặc định. Build, static parse, Blender render và NullRHI không thay thế
  headed visual, material graph, GPU/VRAM, frame-time hoặc 60 FPS proof.
- Giữ quy ước `+X` là hướng tiến, `+Z` là hướng lên. Yaw, wheel/vehicle/rail và
  chuyển động phải suy ra từ transform; placement sát tường phải kiểm bằng bounds sau
  yaw/scale.
- Asset mới phải có nguồn/licence, pivot, bounds, LOD, triangle budget và collision policy.
- Không mở rộng map hoặc làm pha sau khi gate pha hiện tại chưa đạt.
- Không force-push, reset mù hoặc tự merge remote commit chưa được đọc.

## P0 — Khóa baseline, Git và ngữ cảnh

**Mục đích:** khóa một baseline có thể truy nguyên trước khi sửa nội dung.

**Gate:**

- Có local HEAD, branch, dirty-state và remote ref đã đối chiếu.
- Roadmap và handoff ghi rõ DONE, PARTIAL, UNVERIFIED và BLOCKED.
- `Validate-ANANTA.ps1` và `git diff --check` có kết quả mới.
- Không claim runtime/FPS từ source gate.

P0 ngày 2026-10-15 đã đạt sau khi đọc parent history và fast-forward an toàn từ
`dcc05d8...` lên remote merge `9057c9...`. `AGENTS.md` không nằm trong diff và hai Docs P0 không nằm trên remote nên được giữ nguyên; không có reset mù hoặc force-push.

## P1 — Asset, prop nhỏ và geometry pipeline

**Phạm vi:** source/generator/import-readback/review/placement; chưa mở rộng toàn map.

- Giữ 72 model đã đạt gate; chỉ sửa lỗi có evidence hoặc thêm nhóm còn thiếu.
- Ưu tiên sidewalk, sign, railing, monument, playground, traffic light, factory,
  police/fire/ambulance, station, airport, boat, restaurant, hotel, opera, cinema,
  cafe, park, pool, helipad, highway, beach và prop nội thất nhỏ.
- Mỗi model ghi AssetId, category, source, licence, pivot, `+X`, bounds,
  LOD0/1/2, triangle count, material slots và collision policy.
- Sinh/review 8 yaw; placement review dùng 5 camera transform và transformed bounds.
- Import Unreal phải đọc lại dimensions, LOD, material và collision.
- Small prop không tick và collision=false nếu không cần tương tác.

**Gate:** generator/audit, 8-view coverage, 5-view placement, transformed-bounds không
lỗi, import readback, `py_compile`/build cần thiết đạt. Chưa claim headed visual hoặc FPS.

## P1 checkpoint — 2026-10-15

P1 source/review gate đạt trên baseline `9057c9...`:

- `ReviewModels.py` và `ReviewRoomGeometry.py` có fallback `BLENDER_EEVEE` cho Blender 5.2;
  không đổi asset geometry.
- Blender headless tạo lại 72 model x 8 hướng (576 PNG + coverage hash mới).
- Blender headless tạo lại 36 review unit x 5 góc (180 PNG) tại
  `Saved/Upgrade/RoomGeometry/20261015-092127`.
- `AuditCoastalQuality` chạy read-only exit 0: manifest=72, coverage=72,
  import_readback=72, layout_buildings=23, review_units=36, room_coverage_files=4,
  errors=0, warnings=0.
- AST parse 130 script exit 0. Đây là source/geometry evidence; chưa phải headed
  visual/material/FPS acceptance.
## P2 — Hero slice, material graph và headed visual

**Phạm vi:** một hero slice 200–300 m, không nhân rộng district trước khi hình ảnh đạt.

- Readback graph/output thật cho BaseColor, Roughness, Normal và Emissive.
- Dựng nền/đường liên tục, mặt dựng có chiều sâu, ánh sáng, exposure và camera cố định.
- Capture headed chỉ trong gate được phép; lưu preset, resolution, renderer và ảnh mới.

**Gate:** ảnh day/blue-hour đọc được chất liệu, bóng, phản xạ, scale người; graph output
không null; không dùng ảnh Blender/editor-only hoặc NullRHI làm visual acceptance.

## P2 checkpoint — 2026-10-15

P2 hero slice is **PASS for the bounded visual gate**; GPU tier/FPS remains unverified:

- `Tools/Upgrade/coastal_materials.py` now guarantees connected BaseColor, Roughness,
  Normal and Emissive inputs for every generated material and the ocean material.
- `Tools/Upgrade/coastal_detail.py`, `coastal_scene.py` and
  `InspectCoastalMaterials.py` use the same four-output contract. Readback exit 0 reports
  19 materials with BaseColor 19/19, Roughness 19/19, Normal 19/19 and Emissive 19/19,
  non-null package SHA-256 values and `packagesUnchanged=True`.
- `BuildCoastalCity.py` exit 0 recorded `MapCheck` 0 errors/0 warnings and
  `COASTAL_MAP_OK 23 enterable buildings, 6745 instances / 816 HISM batches`.
- `CoastalQA` now supports `-CoastalHeroOnly` and `-CoastalBlueHour`. Five fixed cameras
  (`hero_day`, `hero_blue_hour`, `hero_street`, `hero_interior`, `hero_coast`) were captured
  headed at 1280x720. Day and BlueHour runs each ended `COASTAL_QA_COMPLETE failures=0 views=5`;
  fresh PNGs and metadata are under `Saved/Upgrade/Runtime/2026.10.15-12.58.16` and
  `Saved/Upgrade/Runtime/2026.10.15-13.00.11`.
- The capture proves the bounded headed visual gate only. RTX 3050/4060 frame-time,
  VRAM and 60 FPS acceptance were not run, and no benchmark or soak was performed.
## P3 — Streaming và mở rộng thành phố

**Phạm vi:** chỉ sau P2.

- Chuyển persistent map sang World Partition, OFPA và runtime hash phù hợp.
- Tách Data Layers cho day/night, traffic và mission; dựng HLOD/PCG có seed cố định.
- Đo streaming source, loading range, HLOD identity và boundary khi đi qua district.

**Gate:** không gap/pop-in nghiêm trọng; có readback World Partition/HLOD/Data Layers/PCG
và evidence mới ở ranh giới district.

## P4 — Gameplay và mobility

**Phạm vi:** gameplay thật sau khi geometry/streaming ổn.

- Hoàn thiện aircraft control, rowing animation và railway signal control.
- Hoàn thiện interaction state, save/load, economy và nhiệm vụ vertical slice.
- Kiểm tra input, collision cảm nhận, boarding, respawn, persistence và UI trong headed/PIE
  khi prompt pha cho phép.

**Gate:** test runtime phù hợp có log/evidence mới; không suy ra từ C++ compile hoặc NullRHI.

## P5 — Performance và 60 FPS

- Tách tier RTX 3050 và RTX 4060 Laptop, ghi preset/resolution/renderer.
- Thu headed `stat unit`, `stat gpu`, `stat sceneRendering`, `stat initviews`,
  `stat levels`, VRAM và frame-time percentile ở downtown/interior/traffic.
- Ngân sách 60 FPS là `1000/60 = 16.667 ms`; đây chỉ là mục tiêu cho tới khi số đo
  headed mới đạt.

**Gate:** số đo GPU/CPU/VRAM và percentile đạt ngưỡng đã ghi cho từng tier, không hitch
shader/streaming, có log mới. Không dùng target cấu hình hoặc NullRHI để tuyên bố 60 FPS.

## P6 — AAA toàn map và closure

- Review visual toàn map, material consistency, lighting, collision, navigation,
  density, audio và regression sau các pha trước.
- Lặp lại source/import/runtime/performance gates; chốt provenance và package inventory.
- Chỉ đóng chương trình khi mọi mục UNVERIFIED/BLOCKED đã có evidence hoặc được ghi rõ
  quyết định loại khỏi scope.

## Baseline đã xác nhận

- Local HEAD sau baseline sync: `9057c9beecd2ef1e1cc433eb4f672b9130343e79`.
- Remote ref sau fetch: `9057c9beecd2ef1e1cc433eb4f672b9130343e79`.
- Remote commit là merge `main` vào branch, parents là `dcc05d8fc3...` và
  `77c9ba76fe67834730d3989781c4bea6e51575f3`.
- Fetch exit 0; `git merge-base --is-ancestor` và `git merge-tree` không có conflict;
  `git merge --ff-only origin/codex/coastal-interiors-20261014` exit 0; không reset mù hoặc force-push.
- Foundation validation exit 0: BridgeDescriptor và WorkflowConfig đúng, không thiếu file/plugin.
- Tranche coastal: 72 FBX/model, `max triangles=9678`, model 8-view coverage;
  36 review unit/180 room placement views; 23 building, 6745 instance và 816 HISM;
  r15 bounded NullRHI `COASTAL_QA_COMPLETE failures=0 views=122`.
- Các con số trên không chứng minh headed visual/material/FPS.

## Evidence hygiene

- `Saved/Upgrade/ModelViews/coverage.json` hiện có 72 entries.
- `Saved/Upgrade/coastal-quality-report.json` là audit cũ với `manifest_models=65`;
  không dùng nó làm proof mới của 72 model.
- `Saved/Upgrade/city-layout.json` là source layout cũ có 195 review views; room
  geometry proof hiện hành được tách ở coverage 180 views. Không trộn hai số này.
- Hai warning commandlet còn được giữ trong handoff: UE-MCP Slate startup và API
  `save_current_level` deprecated; chúng không được ghi thành content PASS.

## Thứ tự chat

1. P0 đã khóa baseline `9057c9...`; bắt đầu P1 bằng audit source/readback/review, chưa mở rộng map.
2. P1 đã đạt asset/geometry review gate; giữ 72 model và evidence mới.
3. Chỉ chuyển P2, P3, P4, P5, P6 khi gate pha trước đạt.
4. Mỗi chat cập nhật roadmap này và handoff hiện hành; không tạo roadmap cạnh tranh.

## P4C — Persistence (2026-10-15)

P4C đạt bounded PASS cho versioned save schema 2. Save cũ schema 1 được đọc và migrate; save thiếu trường dùng default hợp lệ; unknown schema, invalid IDs/counts/transforms và corrupted truncated payload bị reject mà không ghi đè slot. Quick Check/Reload trên `ANANTA_City` chứng minh snapshot interaction door/prop/district, NPC schedule, vehicle/transit, service/inventory/economy và day/night tồn tại sau process reload với `Saved/QA/CityPersistence/Report.txt` và `Reload.txt`.

Giới hạn phải giữ: runtime này là fixture state API (`fixture_mode=true`), chưa phải native Coastal actor hook hoặc backend economy thật; không suy ra headed visual, GPU/VRAM hay FPS từ gate này. P5 performance vẫn chưa thực hiện.

## W1 — Three.js water prototype priority (2026-10-16)

W1 là nhánh ưu tiên trước mọi port shader/parameters nước sang Unreal. Prototype
nằm riêng tại `Prototypes/ThreeWater/`, dùng Three.js ES modules, một mặt lưới
cố định, tối đa bốn wave ở preset thấp, foam/shore fade và boundary preview.
Contract kỹ thuật nằm ở `Docs/ANANTA_ART_AND_WATER_CONTRACT.md`.

- P2 là bounded visual pass; nó chưa đạt chất lượng nghệ thuật AAA toàn map.
- P4A/P4B trong lượt W1 này là **PARTIAL** cho mục đích handoff: không có fresh
  Unreal runtime log mới trong lượt này và không được biến build/map evidence cũ
  thành runtime PASS.
- W1 gate cần `npm run check`, `npm run build` và browser smoke có camera
  orbit/free, sóng không seam khi di chuyển camera, foam/shore fade, boundary
  preview, overlay frame-time/render-info và console sạch.
- 60 FPS là mục tiêu chính, ngân sách `1000/60 = 16.667 ms`. Ghi chú 90 FPS
  cũ (nếu xuất hiện trong evidence lịch sử) không tự động thay thế mục tiêu này;
  chỉ headed frame-time mới trên tier GPU đã ghi mới có thể đóng P5.
- W1 không sửa file Unreal, không claim native interaction/persistence, và
  không dùng config, build hoặc NullRHI để tuyên bố FPS.

## W2 — Coastal water quick visual QA (2026-10-16)

Phase ID: W2 — sóng ven bờ, foam, boundary và quick visual QA.
Trạng thái: **DONE** cho source/spec/build/browser quick QA; chưa phải AAA art,
Unreal native collision hoặc F1 performance acceptance.

- Biển prototype dùng boundary rộng `[-700,700] x [-400,400]`, camera margin 14 m
  và boat margin 8 m. `CoastBoundary` hỗ trợ box/polygon, contains, distance và
  clamp; `ShoreFoam` dùng một mặt phẳng cố định với distance-to-edge shader.
- `wave-spec.json` v2 ghi schema version, SHA-256
  `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f`, units,
  axes, bốn wave tuple, foam width 6 m, shoreline depth 16 m, boundary và ba
  preset camera. Preset thấp đặt `cpuMeshRebuild=false`.
- Auto sequence chạy `coast`, `beach_boat`, `offshore`, mỗi cảnh 10 giây. Browser
  cache-bust run mới: coast `avg 17.67 / p95 18.60 / max 23.50 ms`, beach/boat
  `17.72 / 18.40 / 19.20 ms`, offshore `17.73 / 18.50 / 19.40 ms`; cả ba
  `outliers=0`, console error rỗng, overlay có boundary/foam và 4 waves.
- `npm run check` exit 0; `npm run build` exit 0 (Vite chỉ cảnh báo chunk >500 kB);
  `python Tools/QA/ValidateThreeWaterSpec.py` exit 0; `git diff --check` exit 0
  ngoài cảnh báo line-ending; WaveField runtime smoke exit 0.

**DONE:** W2 gate source/spec/browser quick QA.
**PARTIAL:** visual chỉ là prototype water slice; chưa review AAA toàn thành phố,
  interaction/static-dressing toàn map hoặc native Unreal collision.
**UNVERIFIED:** F1 GPU/CPU/VRAM frame-time và 60 FPS.
**BLOCKED:** không có blocker cho W2; Unreal port gate chuyển sang W3.

## W3 — Unreal water contract (2026-10-16)

Phase ID: W3 — port contract nước sang Unreal.
Trạng thái: **PARTIAL/UNVERIFIED**.

- Đã tạo `public/unreal-water-contract.json` và
  `Docs/ANANTA_UNREAL_WATER_CONTRACT.md`, giữ nguyên bốn wave và mapping
  `Three.X→UE.X`, `Three.Z→UE.Y`, `Three.Y→UE.Z`; material function contract là
  opaque `BaseColor/Normal/Roughness/Emissive`, foam rẻ, boundary collision riêng.
- Validator kiểm tra source hash, schema, units, axes, wave tuples, boundary,
  scene labels và `fpsClaim=false`.
- Chưa có Unreal material graph readback thật cho bốn output, native boundary
  collision evidence hoặc ảnh Three.js/Unreal cùng camera. Không sửa Unreal trong
  lượt này và không gọi W3 graph gate là PASS.

**DONE:** contract artifact và validator.
**PARTIAL:** tài liệu/parameter mapping đã sẵn sàng cho port.
**UNVERIFIED:** graph readback, native boundary, camera comparison và visual
  direction equivalence trong Unreal.
**BLOCKED:** Unreal port acceptance đến khi có các evidence trên.

## Current acceptance priority

- P2 là bounded visual pass và chưa đạt chất lượng nghệ thuật AAA toàn map.
- P4A/P4B tiếp tục ghi **PARTIAL** nếu chưa có fresh Unreal runtime log; build,
  map commandlet và NullRHI không biến thành runtime PASS.
- Three.js water W2/W3 là nhánh ưu tiên mới trước mọi shader/parameter port.
- 60 FPS là mục tiêu chính với ngân sách `1000/60 = 16.667 ms`; ghi chú 90 FPS
  cũ không tự động thay thế mục tiêu này. Chỉ F1 headed GPU/CPU/VRAM evidence
  mới được dùng để kết luận.