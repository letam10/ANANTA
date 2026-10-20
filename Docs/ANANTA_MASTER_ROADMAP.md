# ANANTA Master Roadmap

> Current continuation 2026-10-20: R0, W1/W2 and isolated W3 contract gates complete.
> W3 is a separate comparison map; City/Coastal integration and hero art are unverified.
> Main only, incremental phase commits/pushes authorized. P2 is a historical bounded
> visual pass, not AAA art acceptance. P4A/P4B remain PARTIAL until fresh runtime.
> Primary acceptance target is 60 FPS (16.667 ms); legacy 90 FPS UI/config notes
> do not replace it. Source/build/NullRHI never imply headed FPS acceptance.

Ngày cập nhật: 2026-10-20 (các receipt 2026-10-15 bên dưới là lịch sử)
Checkout: `D:\GAME\ANANTA`
Engine: Unreal Engine 5.8.3
Nhánh làm việc hiện tại: `main`

## Current phase gates — 2026-10-20

| Phase | Current evidence | Status / next gate |
| --- | --- | --- |
| R0 | Ownership manifest; Source/Config baseline; current main/remote; old P4 diff classified | DONE bounded; AGENTS and unrelated untracked work protected |
| W1/W2 | 68 contract checks; check/build/spec; three 10-second browser reports; controls and clean console | PASS bounded prototype; not Unreal FPS |
| W3 | New MF_WaveSpec/M_WaveSpec_Opaque and W3_Comparison; actual four outputs, exact tuples, four native collision rays, three matching-camera image pairs | PASS isolated contract; no city integration, WPO, physics, buoyancy or art acceptance |
| V1 | Palette/material/scale/lighting/hero rules locked in Art and Water Contract | CONTRACT DONE; hero visual package pending |
| A1/A2 | Fresh source audit of original kit and historical untracked tranches | PARTIAL; historical AO-as-Normal assignment, incomplete provenance and native hero import/review must be resolved before expansion |
| S1 | Separate City/Coastal source audit; City has WP/OFPA/HLOD history; Coastal evidence differs | PARTIAL; fresh native identity/cells/Data Layers/PCG/normal-input route required |
| G1/P4A/P4B | Native input/API/fixture distinctions audited | PARTIAL; flight altitude, train E/ride, rowing animation, availability and actor persistence remain gaps; fresh runtime still required |
| F1 | Target 60 FPS / 16.667 ms | UNVERIFIED; no headed city CPU/GPU/VRAM/stat evidence in this continuation |
| C1 | Foundation/spec/diff checks pass; full repository LFS audit found 88 pre-existing unexpectedGitObject entries | PARTIAL; source/import/runtime/performance closure remains separate |

Evidence lives in `Tools/Continuation_20261020/`: W2_browser.json, W2_math.json,
W3_native_readback.json, W3_review.json, the six W3 images and A1_hero_audit.md,
S1_source_audit.md, G1_source_audit.md. W3 uses a new Content folder only.
The historical P2 pass below is a bounded material/visual result, not final art
quality. Keep the 60 FPS primary target; old 90 FPS notes do not replace it.

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

### Fresh W2 browser smoke continuation (2026-10-16)

- `npm ci --ignore-scripts` exit `0`; `npm run check` exit `0`; `npm run build`
  exit `0` với warning chunk 731 kB và npm advisory vulnerabilities (1 moderate,
  1 high); không chạy automatic audit fix.
- Root contract validator exit `0`, giữ hash
  `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f`.
- Browser `127.0.0.1:4178` đạt `qaReady=true`, hoàn tất cả ba scene. Fresh report:
  coast `avg 7.60 / p95 8.20 / max 96.30 ms, outliers=1`; beach_boat
  `7.60 / 8.20 / 11.10 ms, outliers=0`; offshore `7.64 / 8.20 / 16.50 ms,
  outliers=0`.
- Key smoke xác nhận `1/2/3` đổi scene; `B` đổi boundary và drawCalls `4→3`;
  `F` đổi foam và drawCalls `3→2`, sau đó cả hai trở lại on. Console warn/error
  không có entry.
- Đây vẫn là prototype/browser evidence; không đóng F1 60 FPS, native Unreal
  graph readback, boundary collision hoặc W3 camera comparison.

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

### Fresh W3 Unreal readback continuation (2026-10-16)

- UE-MCP khởi động editor Unreal cho project `D:/GAME/ANANTA/ANANTA.uproject` thành công; engine 5.8, bridge kết nối port `60765`, editor ready khoảng 52.9 giây. Phiên này chỉ read-only, không sửa `.uasset`, map hoặc ExternalActors dirty.
- Readback ghi vào `Tools/W3/ReadbackEvidence.json` cho `M_Ocean` và `M_DistrictWater`: cả hai opaque, có normal động qua Custom expression, và có bản ghi BaseColor/Normal/Roughness/Emissive theo graph hiện tại.
- Hai Custom expression không map chính xác direction/wavelength/amplitude/speed/phase từ `Prototypes/ThreeWater/public/wave-spec.json`; chưa có `MF_AnantaWater` hoặc foam output. `Tools/W3/ValidateReadback.py` xác nhận source hash `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f` và `fpsClaim=false`.
- Native boundary collision, cùng camera Three.js/Unreal và headed performance chưa có evidence mới.

**DONE:** fresh read-only graph evidence và validator.
**PARTIAL:** opaque water + dynamic normal tồn tại nhưng chưa đạt material-function contract.
**UNVERIFIED:** native boundary collision, camera comparison, hướng sóng tương đương trong Unreal và F1.
**BLOCKED:** exact port cần thay đổi Unreal asset trong khi dirty-file boundary yêu cầu giữ nguyên; chưa gọi W3 là PASS.

- Kiểm tra sau cùng: `python Tools/W3/ValidateReadback.py` exit `0`; `Tools/Build/Validate-ANANTA.ps1` exit `0`; `Tools/Build/Build-ANANTA.ps1 -MaxParallelActions 2` exit `0` sau khi dừng editor W3. `git diff --check` exit `0` với cảnh báo line-ending thông thường.
- `git lfs fsck` exit `1` do nhiều `unexpectedGitObject` trong `Assets/CoastalUpgrade/*` thuộc tree remote `5268d9a15649fd5ad59e5bc5d6878131834ddacf`; giữ nguyên để tránh sửa ngoài pha.

## Current acceptance priority

- P2 là bounded visual pass và chưa đạt chất lượng nghệ thuật AAA toàn map.
- P4A/P4B tiếp tục ghi **PARTIAL** nếu chưa có fresh Unreal runtime log; build,
  map commandlet và NullRHI không biến thành runtime PASS.
- Three.js water W2/W3 là nhánh ưu tiên mới trước mọi shader/parameter port.
- 60 FPS là mục tiêu chính với ngân sách `1000/60 = 16.667 ms`; ghi chú 90 FPS
  cũ không tự động thay thế mục tiêu này. Chỉ F1 headed GPU/CPU/VRAM evidence
  mới được dùng để kết luận.

## A1 — Blender model và texture pipeline (2026-10-16)

A1 bổ sung pipeline headless cho smooth shading, selective bevel/weighted normal,
7 texture channels, reuse theo material key và review evidence. Blender 4.5.1
không còn `Mesh.use_auto_smooth`; Smooth by Angle asset/operator được thử bằng
API hiện hành và fallback `GeometryNodeSetShadeSmooth` phải được ghi rõ khi asset
trả `CANCELLED`. A1 đã có bounded evidence cho 72 object, 8-direction model
review và 5-angle placement review bằng transformed bounds.

- P2 vẫn là bounded visual pass, chưa đạt chất lượng nghệ thuật AAA toàn map.
- P4A/P4B vẫn **PARTIAL** vì chưa có fresh Unreal runtime log; build, config,
  headless render và NullRHI không biến thành runtime/visual/FPS PASS.
- Three.js water W2/W3 tiếp tục là nhánh ưu tiên trước mọi port shader/parameter;
  A1 không sửa Unreal.
- 60 FPS là mục tiêu chính, ngân sách `1000/60 = 16.667 ms`; ghi chú 90 FPS
  lịch sử không tự động thay thế mục tiêu mới. Chỉ F1 headed GPU/CPU/VRAM
  evidence mới được dùng để kết luận.

### A1 status

**DONE:** source scripts, 5×7 channel texture manifest/hash, Blender API branch,
72-object shading report, full bounds math và bounded fresh render evidence.

**PARTIAL:** `CoastalSurface` chưa có explicit surface-key mapping; Smooth by Angle
asset fallback không chứng minh angle threshold; headless render chưa là AAA gate.

**UNVERIFIED:** full model/placement render, hero camera ngang tầm người, native
Unreal material readback, provenance/licence audit, GPU/VRAM và 60 FPS.

**BLOCKED:** full-map AAA acceptance và native Unreal/F1 acceptance chờ headed
runtime evidence; không được suy ra từ build hoặc NullRHI.

## A2 — Hero district và venue thật (2026-10-16)

A2 được thực hiện theo tranche; lượt này chỉ khóa tranche 1:
`street_civic` (street kit và civic block). Không mở rộng toàn map và không sửa
Unreal/map dirty files.

### Tranche order

1. Street kit và civic block — lượt hiện tại.
2. Rail station, road và transit.
3. Coastal beach và waterfront.
4. Police, fire, clinic và factory.
5. Restaurant, hotel, opera, cinema, cafe, bar và arcade.
6. Interiors và props nhỏ.

Mỗi venue bắt buộc có đúng một state: `enterable + interactive`,
`enterable + static dressing` hoặc `shell-only`. Actor tồn tại không đủ để gọi
interactive; phải có entry/room, id/kind/description và runtime service path
được nhận diện.

### A2 evidence

- `Tools/A2/VerifyVenueStates.py --dry-run` exit `0`: 18 venue, state summary
  10 interactive, 7 static dressing, 1 shell-only. Sáu expansion venue được
  source-classified interactive nhưng chưa có runtime pass riêng; bảy venue có
  service id chưa được C++ state nhận diện nên giữ static dressing.
- `Tools/A2/BuildStreetCivicHero.py` normal run exit `0`: bounded manifest
  `Saved/QA/A2/street-civic-hero.json`, source gate PASS, street components là
  static dressing, civic có 5 site và 5 camera (4 camera eye-level 1.60 m).
- Fresh `Tools/Build/Test-CityCivic.ps1` exit `0` với
  `CITY_CIVIC_CHECK_OK services=4 legs=8`; đây là authored-map physics/input
  fixture, không phải visual/FPS proof.
- `Tools/A2/ReviewStreetCivic.py` normal run exit `0`: source hash gate và
  runtime interaction gate PASS; 5 transformed placement bounds tính từ 8 local
  corners theo `scale -> yaw -> translation`; `visualPass=false` vì chưa headed
  capture.

### Status and gates

**DONE:** bounded tranche contract, venue-state classifier, street/civic source
manifest, 5-camera plan, transformed-bounds review và fresh civic interaction
fixture.

**PARTIAL:** street kit là static dressing; visual review chỉ là plan/source
evidence; expansion interaction chưa được native runtime verify.

**UNVERIFIED:** headed visual/native placement readback, all expansion venue
interactions, material/provenance quality, GPU/VRAM/frame-time, 60 FPS và AAA
quality. P2 vẫn là bounded visual pass, chưa đạt nghệ thuật AAA.

**BLOCKED:** tranche 2 trở đi chờ street/civic headed visual gate. Chỉ commit/
push file A2 khi gate đó đạt; không suy ra runtime/FPS từ build, config hoặc
NullRHI.

## F1 — Performance gate và C1 closure (2026-10-16)

F1 là phase đo nhanh khoảng 60 FPS ở `downtown_traffic`, `interior_alley` và `coast_streaming`. Mục tiêu chính vẫn là 60 FPS với ngân sách `1000/60 = 16.667 ms`; ghi chú 90 FPS lịch sử không tự động thay thế mục tiêu mới. Chỉ headed CPU/GPU/VRAM frame-time mới được dùng để kết luận.

### Trạng thái roadmap và ownership

- P2 chỉ là bounded visual pass, chưa đạt chất lượng nghệ thuật AAA toàn map.
- P4A/P4B vẫn **PARTIAL** vì chưa có fresh Unreal runtime log; build, config, map commandlet và NullRHI không biến thành runtime PASS.
- Three.js water W2/W3 là nhánh ưu tiên trước shader/parameter port sang Unreal; F1 không sửa Unreal water.
- F1 chỉ thêm `Tools/F1/HeadedF1Probe.ps1` và `Tools/F1/SummarizeF1Evidence.py`; không sửa Source, map, ExternalActors hoặc Unreal dirty files.

### Evidence và gate

- Ba lần runner thật đều fail-closed exit `3` vì chưa có scene selector template chứa `{scene}`. Run IDs: `20261016_003233521_aa7ef274`, `20261016_003234682_94f08879`, `20261016_003235746_ba3a508c`.
- Metadata có `headed=true`, `nullRhi=false`, `offscreen=false`, `1280x720`, `internalScale=1`, nhưng không launch và không có renderer/scalability, stat, CPU/GPU, VRAM hoặc streaming evidence.
- Source/build checks đạt: foundation validation exit `0`, city performance budget exit `0` với `sourceOnly=true`/`runtimeFpsVerified=false`, instance reuse exit `0`, build exit `0`, diff check exit `0`.
- `git lfs fsck` exit `1` với `unexpectedGitObject` trong `Assets/CoastalUpgrade/*`; lỗi có sẵn của repo và không được rewrite/xóa trong F1. Remote `origin/main` vẫn `5268d9a15649fd5ad59e5bc5d6878131834ddacf`.

### Classification

**DONE:** F1 runner/parser contract, fail-closed evidence, source/build checks và cập nhật handoff.

**PARTIAL:** source-level HISM/instance reuse/LOD evidence; chưa có bằng chứng runtime để chọn HLOD/LOD/Nanite, culling/streaming, material/shadow, texture pool, foliage/Niagara hoặc water draw optimization.

**UNVERIFIED:** headed frame-time, CPU/GPU, VRAM, `stat unit/gpu/sceneRendering/initviews/levels`, renderer/scalability và 60 FPS ở cả ba cảnh.

**BLOCKED:** thiếu headed scene selector/entrypoint; C1 delivery bị chặn thêm bởi `git lfs fsck` exit `1`. Không stage/commit/push khi F1 gate chưa đạt.

### Next prompt

```text
F1 follow-up — cung cấp headed scene selector hoặc entrypoint hỗ trợ {scene},
chạy mỗi cảnh khoảng 10 giây và thu stat/frame-time/VRAM mới. Giữ mục tiêu 60 FPS,
không dùng NullRHI/offscreen/config để claim, không sửa Unreal dirty files; sau đó
xử lý LFS pointer errors riêng bằng owner repo.
```

## F1 — Headed performance continuation and C1 recheck (2026-10-16)

This entry updates the earlier selector-blocked F1 result with fresh headed
runs. The phase boundary is unchanged: only `Tools/F1/` and QA evidence were
used; Unreal Source, map, ExternalActors and existing dirty files remain
untouched. The three-scene target remains 60 FPS, with a 16.667 ms frame budget.

### Fresh evidence

- Downtown run `20261016_012855295_832c39ce`: `ANANTA_City`,
  `-F1Scene=downtown_traffic`, headed DX12 High at 1280x720 and internal scale
  1.0. Runner exit `0`; bounded timeout closed the window gracefully. Fresh
  `FrameTimes.csv` has 3,615 CPU/render/GPU rows. CPU mean/p95/max is
  `5.606/7.505/70.758 ms`; render is `8.675/10.529/43.476 ms`; GPU is
  `5.812/6.305/12.487 ms`. VRAM evidence is 7,956 MB. The observer marker is
  `CITY_GRAPHICS_OBSERVATION_WRITTEN samples=3615`.
- Interior run `20261016_013431726_3ec7cd40`: `ANANTA_City`,
  `-F1Scene=interior_alley`, `CityServiceCheck` plus observer, same headed
  settings. Runner exit `0`; the service journey completed before the
  deadline. Fresh CSV has 3,281 rows. CPU mean/p95/max is
  `5.247/7.867/70.194 ms`; render is `7.585/10.120/95.608 ms`; GPU is
  `6.337/7.084/18.705 ms`. VRAM is 7,956 MB and the observer marker is
  `CITY_GRAPHICS_OBSERVATION_WRITTEN samples=3281`. This is a service-journey
  map proxy, not a fixed interior/alley camera proof.
- Coast run `20261016_013657832_5fea916a`: `ANANTA_CoastalCity`,
  `-F1Scene=coast_streaming`, `CoastalQA` and `CoastalHeroOnly`, headed DX12
  High at 1280x720 and scale 1.0. Runner exit `1`; the Unreal process itself
  exited `0`, but no fresh observer CSV or CPU/render/GPU sample exists. VRAM
  is 7,956 MB and the coast QA path completed its hero views. The coastal
  game mode does not instantiate `CityGraphicsObservation`, and hero-only mode
  omits the measure views, so coast frame-time remains UNVERIFIED.

The combined sanitized input at
`Saved/QA/F1/20261016_0137_combined_sanitized/` now reports exact sample counts
because `SummarizeF1Evidence.py` no longer appends a root document twice when
reading a `scenes` mapping. The parser command exited `1` with
`status=FAIL` and `fpsClaim=false`: downtown passes the GPU 16.667 ms
p95/max check, interior fails on its 18.705 ms GPU maximum, and coast has zero
samples. The runner metadata confirms the requested `stat unit`, `stat gpu`,
`stat sceneRendering`, `stat initviews` and `stat levels` commands and log
markers, but the logs only expose the stat help after `Empty stat command!`;
there is no numeric stat panel readback to call PASS.

Fresh logs confirm D3D12 on an NVIDIA GeForce RTX 4060 Laptop GPU with
7,956 MB dedicated VRAM, WorldPartition and ContentStreaming markers, and a
texture pool of 4,528 MB at startup followed by 3,000 MB after streaming.
These observations support retaining the existing source HISM/instance reuse
and LOD baseline. They do not identify a measured HLOD/Nanite, culling,
material complexity, shadow overlap, texture pool, foliage/Niagara or water
draw-cost change, so no speculative Unreal optimization was applied.

### Verification and delivery status

**DONE:** fresh headed downtown/interior capture, corrected parser, renderer
and scalability metadata, source reuse/LOD checks, foundation validation and
build. `HeadedF1Probe.ps1` AST exit `0`; Python compile exit `0`;
`Validate-ANANTA.ps1` exit `0`; both city QA verifiers exit `0`;
`Build-ANANTA.ps1 -MaxParallelActions 2` exit `0`; `git diff --check` exit
`0`.

**PARTIAL:** downtown and interior have real frame-time evidence, but the
interior GPU max exceeds the 60 FPS budget and both scenes have startup or
streaming spikes. Runtime optimization remains evidence-driven source
baseline only.

**UNVERIFIED:** coast CPU/GPU frame-time, numeric stat readback, equivalent
fixed cameras across all three scenes, native coastal observer integration and
the complete three-scene 60 FPS claim. A build, config, source metric or
NullRHI result is not used as an FPS claim.

**BLOCKED:** C1 stage/commit/push remains blocked because F1 is not a
three-scene PASS and `git lfs fsck` exits `1` with pre-existing
`unexpectedGitObject` entries under `Assets/CoastalUpgrade/`. Remote
`origin/main` remains `5268d9a15649fd5ad59e5bc5d6878131834ddacf`; no delivery
mutation was made.

The next required action is a bounded headed coastal measure-only observer,
then a rerun of all three scenes with numeric stat readback and the same camera
contract. Keep the phase boundary and old evidence intact.

## A3 — Hero art repair tranche (2026-10-16)

A3 là tranche bounded cho 17 asset có tác động hình ảnh lớn: phương tiện/transit,
hạ tầng đường phố, ParkTree, Monument, FactoryConveyor và OperaShells. Kế hoạch
chi tiết ở `Tools/A3/PLAN.md`; nguồn `Assets/CoastalUpgrade` chỉ được đọc, output
và review nằm trong `Saved/QA/A3ArtRepair`. Anime/stylized character và toy identity
được giữ nguyên ngoài tranche.

Repair dùng smooth shading, bevel theo góc, normal correction cho venue shell,
Principled PBR và texture reuse theo SHA-256 của map A1. Không tạo texture trùng,
không sửa Unreal Source/map/ExternalActors và không claim native Unreal readback.

### Evidence

- Blender repair v5 exit `0`: 17 objects, missing `[]`, 17 materials.
- Blender review v6 exit `0`: 136 model views (8 hướng/object), 85 placement
  entries (5 góc/object) từ transformed bounds.
- `ValidateArtRepair.py` exit `0`: schema, hashes, texture reuse, rendered paths
  và native-readback flags đạt.
- Fresh visual checks cho PoliceCar, FireEngine, TrafficLight, StreetSign,
  ParkTree và OperaShells: màu xe/đèn đã rõ hơn, bulb giao thông phát sáng và
  nhãn sign có mặt; ParkTree/Monument/OperaShells vẫn cần authored detail để đạt
  visual AAA.

### Classification

**DONE:** bounded A3 repair pipeline, plan, material/texture hash records, 17
object repair, 136 render review và 85 transformed-bounds placement review.

**PARTIAL:** chỉ hero tranche; chưa sửa toàn bộ 72 mesh/toàn map. Một số silhouette
vẫn low-poly; native wheel/window/light-bar, collision/LOD và venue detail chưa
được readback trong Unreal.

**UNVERIFIED:** native import/placement, camera ngang tầm người trong map,
interaction/persistence venue và 60 FPS/GPU cost. Headless render không phải
runtime acceptance.

**BLOCKED:** A3 artifact không bị block; broader delivery vẫn chờ F1 coastal
measure/stat evidence và `git lfs fsck` pre-existing exit `1` dưới
`Assets/CoastalUpgrade`. Không stage/commit/push khi các gate đó còn đỏ.

### Prompt tiếp theo

```text
A3 next — tiếp tục buildings/areas theo tranche street/civic, rail/airport,
waterfront, emergency/factory, venues và interiors. Mỗi venue ghi enterable +
interactive, enterable + static dressing hoặc shell-only; giữ review 8 hướng,
placement 5 góc từ transformed bounds và không claim native/AAA/60 FPS thiếu
headed evidence.
```

## A3B — Hero fidelity detail pass (2026-10-16)

A3B bổ sung chi tiết hình học có ownership rõ cho 13 hero asset từ A3 v5:
bánh/kính/lightbar/stripe cho phương tiện, cửa sổ transit, cockpit aircraft,
bench xuồng, visor đèn giao thông, label biển, foliage cluster, plaque monument
và glass/ribs venue. Output nằm trong `Saved/QA/A3BArtRepair`; source và Unreal
dirty files giữ nguyên.

### Evidence và gate

- Builder v4 exit `0`: 13 objects, 70 parts, missing `[]`.
- Review V4 exit `0`: 104 ảnh 8 hướng và 65 ảnh placement 5 góc.
- Validator exit `0`: schema, records, paths và native-readback flags đạt.
- `Tools/Build/Validate-ANANTA.ps1` exit `0`; `Tools/Build/Build-ANANTA.ps1
  -MaxParallelActions 2` process exit `0`, nhưng đây chỉ là source/build gate.
- `git diff --check` exit `0`; `git ls-remote origin refs/heads/main` exit `0`,
  remote vẫn ở `5268d9a15649fd5ad59e5bc5d6878131834ddacf`.
- `git lfs fsck` exit `1` do các `pointer: unexpectedGitObject` pre-existing
  dưới `Assets/CoastalUpgrade/*`; không được sửa/xóa trong A3B.
- Visual check ReviewsV4 xác nhận xe/đèn/biển đã có chi tiết nhận dạng; ParkTree
  có foliage cluster/nhánh và OperaShells có glass/ribs phía trước nhưng cả hai
  vẫn PARTIAL vì silhouette/material chưa đạt authored AAA.

**DONE:** bounded A3B detail pipeline, plan/contract, geometry ownership và
review evidence mới.

**PARTIAL:** chưa sửa toàn bộ city/map; chưa có authored foliage/venue geometry
đủ tự nhiên; chưa có camera ngang tầm người trong Unreal.

**UNVERIFIED:** native import/readback, collision/LOD, venue interaction và
60 FPS. Headless render chỉ chứng minh artifact/review fixture.

**BLOCKED:** broader delivery vẫn chờ coast frame-time/stat evidence của F1 và
pre-existing `git lfs fsck` exit `1`; không stage/commit/push.

### Prompt tiếp theo

```text
A3C — tiếp tục authored foliage/venue geometry và fixture street/transit/
waterfront; dùng A3B v4 làm evidence, giữ review 8 hướng, placement 5 góc và
phân loại venue rõ ràng.
```

## A3C — Authored foliage, venue và street-detail pass (2026-10-16)

A3C là tranche riêng trong `Tools/A3C/`, dùng A3B v4 làm đầu vào và không sửa
source Unreal/map/ExternalActors. Năm asset được xử lý là ParkTree, Monument,
OperaShells, TrafficLight và StreetSign. Output blend, manifest và ảnh review
được giữ trong `Tools/A3C/output/`; detail có ownership `a3c_owned`.

### Evidence và gate

- Builder Blender exit `0`: 5 objects, 45 authored parts, missing `[]`.
- Review Blender exit `0`: 40 ảnh 8 hướng và 25 ảnh placement 5 góc.
- Validator exit `0`: schema, source hash, bounds transform order và mọi path ảnh
  đều đạt; `nativeUnrealReadback=false` và
  `nativeUnrealPlacementReadback=false` được giữ nguyên.
- `Validate-ANANTA.ps1` exit `0`, `Build-ANANTA.ps1 -MaxParallelActions 2`
  exit `0`, `git diff --check` exit `0`.
- Visual check mới ghi nhận tán cây bất đối xứng, monument có bệ/cột/stone
  surface, OperaShells có facade X/Y, cửa kính và chữ OPERA, traffic LED lens
  và reflective sign edge.

**DONE:** authored-detail plan/module, artifact generation, 8+5 review và
validator/source/build evidence trong phạm vi 5 asset.

**PARTIAL:** ParkTree và OperaShells vẫn là bounded fixture, còn stylization và
neutral-light limitation; Monument chưa đạt hero AAA; chưa sửa toàn map hoặc
toàn bộ vehicle/venue catalogue.

**UNVERIFIED:** native import/readback, collision/LOD, camera ngang tầm người,
venue interaction/persistence, headed performance và 60 FPS.

**BLOCKED:** F1 vẫn thiếu headed stat/frame-time; pre-existing `git lfs fsck`
exit `1` dưới `Assets/CoastalUpgrade/*`. Không stage/commit/push A3C.

## A3D — Vehicle và transit fidelity pass (2026-10-16)

A3D là tranche riêng trong `Tools/A3D/`, dùng artifact A3C làm đầu vào và giữ
nguyên source Unreal/map/ExternalActors. Tám asset được xử lý: PoliceCar,
FireEngine, Ambulance, Train, CivilAirplane, Helicopter, AirportCart và Rowboat.
Output blend, manifest và ảnh review nằm trong `Tools/A3D/output/`; detail có
ownership `a3d_owned`.

### Evidence và gate

- Builder Blender exit `0`: 8 objects, 65 authored parts, missing `[]`.
- Review Blender exit `0`: 64 ảnh 8 hướng và 40 ảnh placement 5 góc.
- Validator exit `0`: schema, source hash, bounds transform order và mọi path ảnh
  đều đạt; native readback flags vẫn `false`.
- `Validate-ANANTA.ps1` exit `0`, `Build-ANANTA.ps1 -MaxParallelActions 2`
  exit `0`, `git diff --check` exit `0`.
- Visual check ghi nhận detail nhận dạng cho xe cứu hộ, transit, aircraft,
  helicopter, airport cart và rowboat; reviewer có fill/world riêng để không
  đánh giá sai vì fixture quá tối.

**DONE:** bounded vehicle/transit authored detail, material surface riêng,
review 8+5 và validator/source/build evidence.

**PARTIAL:** CivilAirplane/Helicopter vẫn là fixture headless; chưa có interior
cockpit, native Unreal lighting, toàn bộ phương tiện hoặc toàn map.

**UNVERIFIED:** native import/readback, collision/LOD, traffic/vehicle
interaction, camera ngang tầm người, headed performance và 60 FPS.

**BLOCKED:** F1 thiếu headed stat/frame-time; pre-existing `git lfs fsck` exit
`1` dưới `Assets/CoastalUpgrade/*`. Không stage/commit/push A3D.


## A4 — Street, civic và industrial fidelity tranche (2026-10-16)

A4 là tranche riêng trong `Tools/A4/`, dùng artifact A3D làm đầu vào và giữ
nguyên source FBX, Unreal Source/map/ExternalActors cùng dirty ownership hiện tại.
11 asset được xử lý: StreetLamp, Railing, ParkBench, StreetBin, ParkingMeter,
TrafficCone, FireHydrant, FactoryBarrel, FactoryCrate, FactoryConveyor và
FactoryControl. Detail mới mang `a4_owned`, target material dùng shared procedural
PBR family và không tạo raster texture trùng.

### Evidence và gate

- Builder Blender 4.5.1 exit `0`: 11 objects, 59 authored parts, `missing=[]`.
- Review Blender exit `0`: 88 ảnh 8 hướng và 55 ảnh placement 5 góc; mọi placement
  bounds ghi target + child detail sau `matrix_world`/scale/yaw/translation.
- Validator exit `0`: `A4_VALIDATION_OK {"objects":11,"modelViews":88,"placementViews":55}`.
- Save/reopen readback exit `0`: collection tồn tại, 59 object tag `a4_owned`,
  11 target material keys. Ownership bug phát hiện ở lượt đầu đã được sửa trước
  receipt cuối; không dùng receipt cũ.
- Visual check mới cho thấy silhouette/recognition của street furniture, safety props
  và factory kit rõ hơn; đây vẫn là neutral headless fixture.

**DONE:** bounded A4 authored geometry, shared material pass, 8+5 review và
reopen ownership evidence.

**PARTIAL:** cone/hydrant/barrel/crate và toàn bộ A4 chưa đạt AAA visual gate
trong context street/factory với lighting ngang tầm người.

**UNVERIFIED:** native Unreal import/readback, collision/LOD, interaction hoặc
static dressing classification, headed camera review, GPU/VRAM/frame-time và
60 FPS.

**BLOCKED:** không sửa Unreal dirty để port A4; F1 headed evidence và LFS lỗi
pre-existing vẫn là gate riêng. Không stage/commit/push A4 cho tới khi pha native
review/performance đạt.


### A4 fresh repository checks (2026-10-16)

- Foundation validation exit `0`; `Validate-ANANTA.ps1` không thiếu plugin/file.
- `Build-ANANTA.ps1 -MaxParallelActions 2` exit `0`; ANANTA build completed và
  target up to date. Compiler warning về preferred version không phải content error.
- `git diff --check` exit `0`, chỉ warning line-ending của Docs.
- `git lfs fsck` exit `1` với cùng `unexpectedGitObject` pre-existing trong
  `Assets/CoastalUpgrade/*`, tree remote `5268d9a15649fd5ad59e5bc5d6878131834ddacf`;
  không sửa repository LFS trong A4.
- A4 chưa đạt native Unreal/interaction/F1 gate, vì vậy không stage, commit hoặc push.


## A5 — Interior và venue prop fidelity tranche (2026-10-16)

A5 là tranche riêng trong `Tools/A5/`, dùng artifact A4 làm đầu vào và giữ nguyên
source FBX, Unreal Source/map/ExternalActors cùng dirty ownership hiện tại. 12 asset
được xử lý: Sofa, Table, Chair, Bed, KitchenCounter, Stove, Fridge, ArcadeCabinet,
Door, Bookshelf, FloorLamp và TVConsole. Detail mới mang `a5_owned`; target dùng
shared procedural PBR material và không tạo raster texture trùng.

### Evidence và gate

- Builder Blender 4.5.1 exit `0`: 12 objects, 61 authored parts, `missing=[]`.
- Review Blender exit `0`: 96 ảnh 8 hướng và 60 ảnh placement 5 góc; placement
  bounds ghi target + child detail sau `matrix_world`/scale/yaw/translation.
- Validator exit `0`: `A5_VALIDATION_OK {"objects":12,"modelViews":96,"placementViews":60}`.
- Save/reopen readback exit `0`: collection tồn tại, 61 object tag `a5_owned`,
  12 target material keys và 12 fixture records rõ `static dressing`.
- Visual check mới cho thấy cushion/panel/handle/screen/shelf/lamp detail đọc được;
  đây vẫn là neutral headless fixture.

**DONE:** bounded A5 interior/venue prop geometry, material pass, 8+5 review và
reopen ownership evidence.

**PARTIAL:** chưa đạt AAA interior/venue lighting hoặc camera ngang tầm người trong
map; asset vẫn là fixture độc lập.

**UNVERIFIED:** native Unreal import/readback, LOD/collision, enterable state,
interaction/persistence, headed performance và 60 FPS.

**BLOCKED:** native apply vẫn ngoài dirty Unreal boundary; không stage/commit/push A5
trước native interaction/performance gate.


### A5 fresh repository checks (2026-10-16)

- Foundation validation exit `0`; `Validate-ANANTA.ps1` không thiếu plugin/file.
- `Build-ANANTA.ps1 -MaxParallelActions 2` exit `0`; ANANTA build completed và
  target up to date; không dùng receipt này để claim 60 FPS.
- `git diff --check` exit `0`, chỉ warning line-ending của Docs.
- `git lfs fsck` exit `1` với cùng `unexpectedGitObject` pre-existing trong
  `Assets/CoastalUpgrade/*`, tree remote `5268d9a15649fd5ad59e5bc5d6878131834ddacf`;
  không sửa repository LFS trong A5.
- A5 chưa đạt native Unreal/interaction/F1 gate, vì vậy không stage, commit hoặc push.

## R0 rebaseline — 2026-10-20

- Baseline main/local/origin: `9b295109e280752bd3d1ff7640be3bad02f6dc1e`.
- Full required documents read; unchanged hashes confirm the roadmap/handoff
  remain the versions read in full during the architecture audit.
- `git diff -- Source Content Config ANANTA.uproject` is empty. There are no
  current dirty Unreal files to isolate or overwrite. P4A/P4B interaction/transit
  implementation is already in committed history; current acceptance is PARTIAL
  because this continuation has no fresh runtime log.
- Preserve AGENTS.md, previous untracked art/F1/W3 scripts and ArchitectureAudit.
  Two existing Docs diffs are reviewed historical evidence; this R0 commit
  records them with this dated current-state addendum, without changing old
  receipts to fresh PASS. Ownership: `Tools/Continuation_20261020/ownership.json`.
- W1/W2 priority: reuse the existing independent ThreeWater prototype; first fix
  the verified beach_boat camera/spec mismatch, execute source/spec/math gates,
  then fresh HTTP browser smoke for orbit/free, waves/foam/boundary and three
  10-second scenes. No Unreal changes before that gate.
- W3, V1 hero acceptance, A1/A2 native art, S1 streaming, G1 actor persistence,
  F1 and C1 remain pending new evidence. Existing A1–A6 fixtures are not native
  import or full-map art acceptance. No full-map expansion before hero acceptance.
- User now authorizes fresh bounded headed runtime/F1 checks as described in
  the current request; historical no-launch statements remain historical.
- Delivery: stage phase-owned allowlists only, commit/push on main, compare
  git ls-remote after each push. An incomplete later gate is reported PARTIAL,
  rather than preventing delivery of an independently verified earlier phase.

## W1/W2 fresh gate — 2026-10-20

- R0 committed/pushed on main as `2a481d89b4222cafa965821d7c3ec41180fc1f71`;
  git ls-remote matched local HEAD.
- Fixed verified beach_boat camera/spec target mismatch (-34 -> -42) and box
  boundary precedence. Previously eight corner/margin checks failed; after the
  fix all 68 checks pass, including seven height/analytic-normal comparisons.
- `npm run check`, `npm run test:contract`, `npm run build` and the canonical
  ThreeWater spec validator exit 0; a deliberately wrong camera is rejected.
- Fresh HTTP browser run completed coast/beach_boat/offshore for 10 seconds each.
  Console warn/error empty. Scene avg/p95/max ms: coast 6.06/7.30/135.50 (one
  startup outlier), beach_boat 6.08/6.90/15.80, offshore 6.06/6.20/7.20.
- Orbit drag, free camera, scene keys and foam/boundary toggles verified; two
  fresh local images saved. No visible seam in reviewed views. Seven geometries
  remain fixed. Browser measurements are observations, not Unreal FPS proof.
- Receipt: `Tools/Continuation_20261020/W2_browser.json`; math checks and coast/
  orbit PNGs in the same folder. No Unreal source/content/config change in W1/W2.
- W3 may now consume the pinned spec. Native material function/readback, separate
  collision boundary and same-camera image comparison remain required; no W3
  PASS is inferred from this prototype. V1/A1/A2/S1/G1/F1/C1 broader gates remain.
- R0 foundation validation and diff check exit 0. Full LFS fsck exits 1 with 88
  pre-existing unexpectedGitObject pointer records under Assets/CoastalUpgrade;
  no object rewritten/deleted. Receipt `Tools/Continuation_20261020/R0_gates.json`.

## W2 visual water refinement — 2026-10-20

- Online technical comparison used primary references: GPU Gems describes a
  four-wave geometric base plus detail normal waves and explains that Gerstner
  lateral displacement sharpens crests; the Three.js `Water2` source shows the
  higher-cost reflection/refraction/flow-map path. The prototype adopts only
  the bounded low-cost subset.
- `Prototypes/ThreeWater` now keeps one fixed 160x160 plane and adds analytic
  Gerstner lateral displacement, tangent-derived normals, procedural detail
  slope, Fresnel/specular response, deep/shallow color, crest foam and shore
  foam. CPU geometry is not rebuilt per frame.
- The original four wave tuples and W3 hash remain unchanged. The new visual
  steepness defaults are code-owned and documented in the prototype README;
  they are not silently added to the Unreal parameter contract.
- Boat QA now samples from a fixed base position and applies the displaced
  result through the boundary clamp, so lateral Gerstner motion cannot compound
  into position drift. A new contract check covers finite Gerstner position,
  lateral displacement and unit normal.
- Fresh checks: `npm run check`, `npm run test:contract` (69 checks), `npm run
  build`, and HTTP delivery from Vite all pass. Browser screenshot/console smoke
  is UNVERIFIED in this environment because Work browser automation is disabled;
  this receipt does not claim headed visual quality or 60 FPS.

## F1 — Fresh three-scene runtime observer continuation (2026-10-20)

This continuation records new evidence after the city graphics observer was
made opt-in by `CityObserveGraphics` and able to snapshot rows every 120
samples before process exit. The source/build change is commit
`43584e3bd91a20efb9396ca41db9d07f7502b83e`, pushed to `origin/main`; unrelated
dirty files and prior evidence remain untouched.

### Fresh runtime evidence

| Scene | Run | Executable and mode | Rows | CPU p95/max ms | Render p95/max ms | GPU p95/max ms | VRAM | Console errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `downtown_traffic` | `20261020_151359733_39278ff0` | DX12 High, `UnrealEditor-Cmd.exe`, 1280x720, scale 1 | 857 | 16.848 / 1431.773 | 10.670 / 1391.167 | 7.253 / 33.514 | 7956 MB | 0 |
| `interior_alley` | `20261020_151654176_781259c1` | DX12 High, `UnrealEditor-Cmd.exe`, 1280x720, scale 1 | 2583 | 16.562 / 187.198 | 10.879 / 194.941 | 6.823 / 30.923 | 7956 MB | 0 |
| `coast_streaming` | `20261020_150739259_07110863` | DX12 High, `UnrealEditor-Cmd.exe`, 1280x720, scale 1 | 1319 | 12.953 / 630.261 | 8.450 / 2980.685 | 5.041 / 35.982 | 7956 MB | 0 |

The three runner metadata files are `PASS` with fresh CPU/render/GPU rows,
non-NullRHI DX12 rendering, required scene selectors, WorldPartition and
ContentStreaming markers, and no console errors. The captured CSVs are stored
under each run directory in `Saved/QA/F1/`. The runner's `headed` metadata is
retained, but the actual executable is `UnrealEditor-Cmd.exe`; this evidence
proves runtime rendering and counters, not a human visual headed review.

### Classification

**DONE:** fresh runtime samples for all three required scene labels; resolution,
internal scale, renderer, scalability, CPU/render/GPU rows, VRAM and console
error fields are recorded; observer output is durable before early CoastalQA
exit; commit and remote verification are complete.

**PARTIAL:** GPU p95 is below the 16.667 ms reference in all three scenes, and
interior/coast wall p95 is below the reference. Downtown wall p95 is
16.848 ms, slightly above budget. Large startup/streaming maxima remain in all
three CSVs, so this is a measurement receipt and optimization baseline rather
than a 60 FPS acceptance.

**UNVERIFIED:** numeric panel readback for `stat unit`, `stat gpu`,
`stat sceneRendering`, `stat initviews` and `stat levels`; fixed camera parity
between scenes; human visual headed review; and a final 60 FPS claim after
optimization. `UnrealEditor-Cmd.exe` runtime evidence must not be relabeled as
full headed visual acceptance.

**BLOCKED:** C1 still has the pre-existing `git lfs fsck` failure with
`unexpectedGitObject` entries under `Assets/CoastalUpgrade`; the full objective
also remains open for W3 city integration, V1/A1/A2 native hero gates, S1
streaming readback and G1 native gameplay/persistence.
