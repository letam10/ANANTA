# Coastal City — bàn giao ngày 15/10/2026

## Phạm vi lượt này

Tiếp tục nhánh codex/coastal-interiors-20261014 của Unreal Engine 5.8.3.
Giữ nguyên thay đổi người dùng trong AGENTS.md; chỉ cập nhật nguồn Coastal,
asset sinh bởi bộ công cụ, công cụ kiểm chứng và Docs thuộc lượt này.

## Đã thực hiện

- Thêm Tools/Upgrade/coastal_micro_props.py với 10 prop low-poly có pivot nền:
  KitchenKnifeBlock, BathroomBin, BedroomClock, ToyBlocks, BarGlassRack,
  TrafficCone, FireHydrant, ParkingMeter, AirportCart và Lifebuoy.
- Nối 10 prop vào GenerateCoastalModels.py và đặt vào phòng ngủ, bếp, phòng tắm,
  phòng khách, cafe/bar/nhà hàng, sân bay, giao lộ, phố biển và bến thuyền.
- Cập nhật placement để prop nhỏ tắt collision khi không cần, giữ bounds assertion
  cho các đồ trong phòng, và không thay đổi hệ trục/đơn vị hiện có.
- Sinh lại bộ kit: 65 model FBX và CoastalModels.blend. Mỗi model có 8 hướng review.
- Import vào Unreal thành công 65 model; map commandlet dựng lại 23 building,
  6.947 placement và 969 HISM batch.
- Review hình học phòng đạt 180 view cho 36 review unit, tương ứng 5 view/unit.
- Cấu hình render đã có từ lượt trước: TSR, Lumen software, hardware ray tracing
  tắt, HZB/occlusion/instance culling bật; cull distance đã sửa từ mét sang cm Unreal.

## Kiểm chứng mới

- python -m py_compile trên GenerateCoastalModels.py, coastal_micro_props.py,
  coastal_home.py, coastal_rooms.py, coastal_landscape.py và coastal_transit.py:
  PASS.
- Blender 4.5.1: COASTAL_MODELS_OK 65 models; max triangles=9678; exit 0.
- ReviewModels.py: MODEL_VIEW_COVERAGE_OK 65 models x 8 views; exit 0.
- ComposeModelReviews.py: MODEL_REVIEWS_OK 65 models, 520 rendered views; exit 0.
- AuditCoastalQuality.py: COASTAL_QUALITY_OK manifest_models=65 review_units=36
  warnings=0; import_readback=65, layout_buildings=23, review_views=180.
- ImportCoastalModels.py commandlet với NullRHI: IMPORT_EXIT=0, Python script
  executed successfully, 0 import errors; có 1 cảnh báo UE-MCP Slate startup.
- BuildCoastalCity.py commandlet với NullRHI:
  COASTAL_MAP_OK 23 enterable buildings, 6947 instances / 969 HISM batches,
  map check 0 Error(s), 0 Warning(s); còn cảnh báo API deprecated của Unreal
  và UE-MCP Slate startup.
- ReviewRoomGeometry.py: ROOM_GEOMETRY_VIEWS_OK 180 views; đây là review hình học,
  không thay thế gameplay hoặc lighting acceptance.
- Quick gameplay bounded với map CoastalCity, -game -CoastalQA -NullRHI:
  runtime-r7-quick.log ghi COASTAL_QA_COMPLETE failures=0 views=122.
  Các check spawn, cửa, dịch vụ, NPC, item, chọn cửa từ phố, biên biển, đi bộ,
  lên/lái/xuống xe và lên/chèo/xuống xuồng đều đạt. Đây không phải benchmark 60 FPS.

## Dọn file tạm

- Đã dọn bytecode pyc sinh trong Tools/Upgrade/__pycache__ cho các script của lượt.
- Giữ log import/build/QA, manifest, city-layout, audit report, ảnh 8 hướng và
  room geometry để làm bằng chứng; không xóa asset/model hay file người dùng.
- AGENTS.md vẫn dirty từ trước và không được stage.

## Chưa hoàn tất và giới hạn bằng chứng

- Chưa có headed/player capture để xác nhận visual, material, collision cảm nhận,
  VRAM, GPU p95 hay 60 FPS; NullRHI chỉ xác nhận logic bounded.
- CoastalCity chưa chuyển sang World Partition/HLOD/Data Layers.
- NPC chưa có lịch sinh hoạt; xe/thuyền còn kinematic; chưa có lái máy bay,
  hoạt ảnh chèo tay, minigame, kinh tế/save đầy đủ hoặc phản chiếu gương riêng.
- Các building đã vào được theo harness nhưng chất liệu/ánh sáng và mật độ đô thị
  chưa đạt mức photoreal/AAA cho mọi camera.
- 5 view/unit hiện là review camera; chưa phải người chơi tự do kiểm từng phòng
  trên headed build.

## Kế hoạch còn tồn đọng

1. Tạo hero slice có World Partition/HLOD và đo streaming trước khi nhân rộng district.
2. Thêm material/lighting review headed, sau đó đo downtown, interior và traffic.
3. Mở rộng interaction data-driven cho đồ nhỏ, NPC schedule, transit và save state.
4. Chỉ tuyên bố đạt 60 FPS sau khi có log headed mới ghi preset, độ phân giải,
  phần cứng và frame-time percentile.

## Evidence

- Saved/Upgrade/coastal-quality-report.json
- Saved/Upgrade/runtime-r7-quick.log
- Saved/Upgrade/Runtime/2026.10.14-23.31.04/checks.csv
- Saved/Upgrade/Runtime/2026.10.14-23.31.04/frames.csv
- Saved/Upgrade/ModelViews/coverage.json và review-page-*.jpg
- Saved/Upgrade/RoomGeometry/20261014-232832
- Saved/Upgrade/import-coastal-65.log
- Saved/Upgrade/build-coastal-65.log

## Git

Đã ủy quyền commit/push cho nhánh codex/coastal-interiors-20261014.
AGENTS.md không được stage; sau khi kiểm tra status sẽ stage đúng nguồn, asset và
Docs của lượt này, rồi đối chiếu git rev-parse HEAD với git ls-remote origin.


## Cập nhật 2026-10-15 — prop nhỏ có tương tác

- Thêm Tools/Upgrade/coastal_prop_actions.py với hàm
  place_interactive_prop(scene, label, model, position, message, yaw, scale).
  Hàm dùng ACoastalInteractable Kind=5, giữ mesh riêng cho prop nhỏ và scale
  theo đúng placement đã review; các prop ngoài trời vẫn dùng HISM để giữ chi phí thấp.
- Bốn prop trong nhà có thể nhấn E để kiểm tra: BedroomClock, KitchenKnifeBlock,
  BathroomBin và ToyBlocks. BarGlassRack trong cafe/restaurant/bar cũng có message
  tương tác. HUD hiện có hiển thị action_name và Use() trả message reusable.
- BuildCoastalCity commandlet chạy bằng script path tuyệt đối đạt
  COASTAL_MAP_OK 23 enterable buildings, 6906 instances / 928 HISM batches,
  0 error; hai warning là Slate startup và API save level deprecated.
- CoastalQAGameplay.cpp thêm check micro_props_respond. Build Development exit 0.
  Quick gameplay r8 ghi micro_props_respond PASS và
  COASTAL_QA_COMPLETE failures=0 views=122 trong
  Saved/Upgrade/runtime-r8-microprops.log.
- Lệnh commandlet phải dùng absolute path cho Tools/Upgrade/*.py vì Unreal có thể
  resolve path tương đối từ Engine/Binaries/Win64; lần chạy sai path đã được giữ
  làm chẩn đoán, không dùng làm bằng chứng PASS.
- Đây vẫn là bounded NullRHI gameplay proof; chưa phải headed visual acceptance,
  benchmark 60 FPS, GPU/VRAM percentile hay test người chơi tự do trong từng phòng.\n

## Cập nhật 2026-10-15 — lịch cư dân nhẹ

- Kind=2 resident NPC nay có lịch chuyển động nhẹ quanh anchor trong bán kính
  120 cm, tick interval 0,1 giây; service, cửa, item, prop nhỏ và HISM không tick.
- coastal_scene.py đặt schedule_enabled, schedule_radius và schedule_speed bằng
  set_editor_property để tương thích Unreal Python. coastal_rooms.py bật lịch cho
  23 resident actor.
- CoastalInteractable.cpp giữ anchor, pha dao động xác định theo vị trí và di chuyển
  bằng hai hàm sin nhỏ; không đổi độ cao, không dùng pathfinding hoặc tick toàn map.
- Build Development đạt Result: Succeeded. BuildCoastalCity log tuyệt đối ghi
  COASTAL_MAP_OK 23 enterable buildings, 6906 instances / 928 HISM batches,
  Python script executed successfully, 0 error(s), 2 warning(s).
- CoastalQA r9 ghi 23_npcs_scheduled PASS, npc_schedule_moves PASS,
  micro_props_respond PASS và COASTAL_QA_COMPLETE failures=0 views=122.
  Đây vẫn là bounded NullRHI gameplay proof, chưa phải headed visual/FPS benchmark.
- Một lần chạy commandlet dùng tên thuộc tính trực tiếp b_schedule_enabled đã lỗi
  AttributeError; lỗi đã được sửa bằng set_editor_property và lần chạy sau đạt.

## Cập nhật 2026-10-15 — đèn giao thông runtime nhẹ

- Đổi 72 đèn giao thông tại 36 giao lộ thành actor `ACoastalInteractable` Kind=6. Mỗi actor giữ mesh TrafficLight, không tạo collision riêng và được đặt theo cùng tọa độ hai phía đường.
- `SignalPeriod` mặc định là 12 giây, tối thiểu 3 giây; `SignalState` chuyển Green (0), Yellow (1) rồi Red (2) theo tỷ lệ 55% / 10% / 35%. Pha ban đầu phụ thuộc tọa độ để các giao lộ không đồng bộ tuyệt đối.
- Actor signal bật tick 0,1 giây; service, cửa, item, HISM và prop nhỏ không bị bật tick bởi thay đổi này. HUD/action message phản ánh trạng thái signal hiện tại.
- Build Development đạt `Result: Succeeded`. BuildCoastalCity dùng absolute script path và ghi `COASTAL_MAP_OK 23 enterable buildings, 6834 instances / 892 HISM batches`, Python script executed successfully, 0 error(s), 2 warning(s). Cảnh báo là Slate startup và API save level deprecated.
- QA r10 chạy `-game -CoastalQA -NullRHI -unattended -NoSound` exit 0. Các marker mới và hồi quy đều PASS: `traffic_signals_present`, `npc_schedule_moves`, `micro_props_respond`, cùng các check spawn/cửa/dịch vụ/NPC/item/biên biển/xe/xuồng; tổng kết `COASTAL_QA_COMPLETE failures=0 views=122` trong `Saved/Upgrade/runtime-r10-signal.log`.
- Đây là proof logic bounded trong NullRHI; chưa chứng minh màu đèn/material trong headed player, cảm nhận va chạm, GPU/VRAM, frame-time percentile hay 60 FPS. Cần headed visual review và đo phần cứng trước khi tuyên bố đạt mục tiêu FPS.

## Cập nhật 2026-10-15 — sáu prop nội thất mới

- Bổ sung sáu model low-poly có pivot nền và hướng đọc `+X`: `MakeupKit`, `SaucePan`, `BathroomTowel`, `SofaCushion`, `ToyDoll` và `Laptop`. Các model dùng primitive hiện có, dưới giới hạn 20.000 tam giác/model và được generator xuất cùng bộ 3 LOD.
- Generator Blender đạt `COASTAL_MODELS_OK 71 models; max triangles=9678`. Review đạt `MODEL_VIEW_COVERAGE_OK 71 models x 8 views` và `MODEL_REVIEWS_OK 71 models, 568 rendered views`.
- Import Unreal đạt `COASTAL_IMPORT_OK 71 models with 3 LODs; dimensions verified`, Python script exit 0. Cảnh báo duy nhất là UE-MCP Slate startup.
- `coastal_rooms.py` đặt prop tương tác bằng API `place_interactive_prop` trong nhóm home/hotel/beauty: vanity makeup, kitchen sauce pan, bathroom towel, sofa cushion, toy doll và hotel laptop. Các vị trí giữ khoảng hở lối đi/cửa; prop nhỏ dùng Kind=5 và không bật tick riêng.
- Build map đạt `COASTAL_MAP_OK 23 enterable buildings, 6834 instances / 892 HISM batches`, MapCheck 0 Error/Warning; warning còn lại là Slate startup và `save_current_level` deprecated.
- Build Development đạt `Result: Succeeded` trong 18,63 giây. QA r11 exit 0 với `11_micro_props_present PASS`, `micro_props_respond PASS`, `traffic_signals_present PASS`, `npc_schedule_moves PASS` và `COASTAL_QA_COMPLETE failures=0 views=122` trong `Saved/Upgrade/runtime-r11-microprops.log`.
- Đây vẫn là bounded NullRHI proof; chưa thay thế headed visual review, kiểm tra va chạm cảm nhận, GPU/VRAM hoặc benchmark 60 FPS. Asset cũ bị generator/import ghi lại đã được phục hồi, chỉ giữ blend/manifest và sáu asset mới cho tranche này.

## Cập nhật 2026-10-15 — gate tàu hai hướng

- Ga Nova Coast hiện có hai đường ray độc lập tại hai cao độ ngang khác nhau, hai platform và cầu vượt; `coastal_transit.py` tạo `Train_0` chạy `Direction=+1` và `Train_1` chạy `Direction=-1`.
- `ACoastalTrain` chạy dọc trục X ở tốc độ 650 cm/s, dừng 6 giây khi qua mốc ga X=0 rồi tiếp tục, và đảo vị trí ở hai đầu `RouteHalfLength`; đây là chuyển động nhẹ, không thêm tick cho actor tĩnh/HISM.
- `CoastalQAGameplay.cpp` thêm gate `train_two_way_present`, đếm đúng hai train actor và kiểm tra một hướng đông, một hướng tây.
- Build Development sau thay đổi đạt `Result: Succeeded` trong 11,15 giây. QA r12 exit 0 ghi `train_two_way_present PASS`, `11_micro_props_present PASS`, `traffic_signals_present PASS`, `npc_schedule_moves PASS` và `COASTAL_QA_COMPLETE failures=0 views=122` trong `Saved/Upgrade/runtime-r12-train.log`.
- Gate này chứng minh actor và hướng tuyến trong runtime bounded NullRHI; chưa chứng minh headed visual, va chạm tàu với người chơi, tín hiệu đường ray điều khiển tàu, âm thanh, schedule giao thông hoặc FPS 60.

## Cập nhật 2026-10-15 — dải bọt sóng nhẹ

- Thêm model low-poly `OceanFoam` với pivot nền, dải bọt trắng mỏng và bốn gợn ellipsoid; model giữ dưới ngân sách hình học và không có tick/physics.
- `coastal_landscape.py` đặt 8 instance `OceanFoam` thưa dọc mép cát tại x=210 m, collision=false. Vì dùng scene.model nên các instance được gom HISM, không tạo 8 actor runtime độc lập.
- Generator đạt `COASTAL_MODELS_OK 72 models; max triangles=9678`; review đạt `MODEL_VIEW_COVERAGE_OK 72 models x 8 views` và compose đạt `MODEL_REVIEWS_OK 72 models, 576 rendered views`.
- Import đạt `COASTAL_IMPORT_OK 72 models with 3 LODs; dimensions verified`, exit 0. BuildCoastalCity đạt `COASTAL_MAP_OK 23 enterable buildings, 6842 instances / 899 HISM batches`, MapCheck 0 Error/Warning và 0 error runtime.
- QA r14 exit 0 đạt `ocean_boundary_blocks PASS`, `train_two_way_present PASS`, `traffic_signals_present PASS`, `11_micro_props_present PASS`, `npc_schedule_moves PASS`, các gate xe/xuồng và `COASTAL_QA_COMPLETE failures=0 views=122` trong `Saved/Upgrade/runtime-r14-foam.log`.
- Đây là cải thiện thị giác nhẹ trên mặt nước opaque có normal động; chưa phải water simulation, buoyancy, foam interaction, headed visual acceptance hoặc proof 60 FPS GPU.

## Cập nhật 2026-10-15 — mở rộng tương tác đồ nội thất r15

- Không thêm mesh mới trong tranche này. `coastal_home.py` chuyển các placement đã được review trong home/hotel/beauty thành Kind=5 có message: TVConsole, Perfume, Kettle, Fridge, hai DinnerPlate, ShowerTray và SoapDispenser.
- `coastal_rooms.py` chuyển thêm các placement hiện hữu ở cafe/restaurant/bar, cinema/opera, factory và arcade thành tương tác có giới hạn: Stove, CookingPan, CookingPot, Fridge, một ghế auditorium, một FactoryControl và một ArcadeCabinet. Không tạo actor trùng và giữ nguyên model, yaw, scale, bounds, lối đi và khoảng hở tường.
- Cả hai file đạt AST parse và `git diff --check`; C++ Development build đạt `Result: Succeeded` trong 26,46 giây. Warning duy nhất từ API deprecated của Unreal Engine, không phải lỗi tranche.
- Dùng project path tuyệt đối khi chạy commandlet vì path tương đối làm Unreal báo `Failed to open descriptor file ANANTA.uproject`. Lần chạy đúng đạt `COASTAL_MAP_OK 23 enterable buildings, 6745 instances / 816 HISM batches`, MapCheck 0 Error(s), 0 Warning(s), Python script exit 0. HISM giảm so với r14 vì một phần placement nhỏ được tách thành actor tương tác, không phải do xóa building.
- Quick gameplay r15 chạy `-game -CoastalQA -NullRHI -unattended -NoSound`, profile ghi `High Lumen, TSR 900p/1080p, target 16.667 ms`. Các gate `all_23_doorways_close_and_clear_on_open`, `23_services_respond`, `23_npcs_scheduled`, `micro_props_respond`, `11_micro_props_present`, `traffic_signals_present`, `train_two_way_present`, `ocean_boundary_blocks`, đi bộ/xe/xuồng đều PASS; tổng kết `COASTAL_QA_COMPLETE failures=0 views=122` trong `Saved/Upgrade/runtime-r15-interactive.log` và runtime folder `Saved/Upgrade/Runtime/2026.10.15-01.19.19`.
- Commandlet đã ghi lại materials nhưng các material `.uasset` sinh lại không thuộc tranche và đã được khôi phục. Map được giữ vì là asset đã theo dõi từ các tranche trước và cần lưu placement tương tác mới.
- Đây vẫn là bounded NullRHI proof. Chưa có headed/player visual capture, collision cảm nhận, GPU/VRAM percentile, frame-time headed hoặc benchmark/soak; mục tiêu 60 FPS vẫn chỉ là ngân sách 16,667 ms. World Partition/HLOD/Data Layers, aircraft control, rowing animation, economy/save và visual AAA toàn map vẫn là tồn đọng.
- Worktree giữ nguyên `AGENTS.md` dirty có sẵn và không stage file đó. Evidence mới: `Saved/Upgrade/runtime-r15-interactive.log`, `Saved/Upgrade/build-coastal-interactive.log` và `Saved/Upgrade/Runtime/2026.10.15-01.19.19`.

## Cập nhật 2026-10-15 — final closure handoff

- Báo cáo chốt đầy đủ được lưu tại `Docs/COASTAL_FINAL_HANDOFF_20261015.md`.
- Foundation verify mới nhất đạt `ANANTA foundation validation passed.` với BridgeDescriptor và WorkflowConfig đúng, không thiếu plugin/file.
- Bằng chứng runtime r15 vẫn là `COASTAL_QA_COMPLETE failures=0 views=122`; map commandlet đạt 23 building, 6745 instances, 816 HISM và MapCheck 0 lỗi/0 cảnh báo.
- Không còn `.tmp` dưới `Saved`; `AGENTS.md` dirty từ trước không được stage.
- Capture editor-only 195 ảnh đã chạy nhưng compose pixel validation thất bại vì variance dưới ngưỡng ở toàn bộ ảnh. Vì vậy không dùng capture này làm visual acceptance.
- Chốt trung thực: logic/placement/interior tranche đã bàn giao; headed visual, GPU/VRAM/frame-time và 60 FPS chưa được chứng minh. World Partition/HLOD/Data Layers, aircraft/rowing, railway signal control, economy/save và photoreal AAA toàn map vẫn là tồn đọng.
