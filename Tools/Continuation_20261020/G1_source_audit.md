# G1 source audit — 2026-10-20

Phạm vi: đọc nguồn, không chạy engine, test, browser hay sửa Unreal. Chỉ báo cáo này thuộc GAMEPLAY_AUDIT. Kết luận: **P4A/P4B/G1 PARTIAL; P4C là persistence fixture, chưa phải native Coastal actor persistence.** Không có fresh runtime log do audit này tạo. Nguồn và script authoring không xác nhận trạng thái thực của binary map.

## Đường tương tác đang có

- `Source/ANANTA/Private/CoastalCharacter.cpp:49`: WASD, mouse look, Space, Shift, E bind thật; `FindAction:81` chọn gần nhất trong 320 cm, kiểm tra khoảng cách 3D và visibility trace. Chỉ nhận `ACoastalInteractable` và `ACoastalVehicle`, **không nhận train**.
- `CoastalCharacter.cpp:115`: E gọi `Use()`, hoặc `Vehicle->Board(this)`; elevator có overlap capsule ở destination rồi teleport. Đây là capability nguồn, chưa phải hành trình vào venue bằng input bình thường đã được kiểm mới.
- `Source/ANANTA/Private/CoastalInteractable.cpp:218`: door xoay 95 độ; item ẩn mesh và tắt collision; service/NPC/prop/signal chủ yếu trả chuỗi và đặt `bUsed=true`. Service trả lời không tương đương heal, giao dịch, inventory hay mission.
- Metadata `VenueId/PropId/SaveKey/Prompt/Response/FailureMessage/CollisionPolicy` đã có và được normalize. Nhưng `FindAction()` không gọi `IsInteractionAvailable()`, `Use()` không kiểm `bScheduleActive`, HUD dùng `ActionName` thay vì `GetInteractionPrompt()`. Actor disabled/inactive vẫn có thể được chọn; E elevator có thể teleport trước khi `Use()` kiểm enabled. `CollisionPolicy` mới là metadata; pickup luôn tắt collision và chưa thực thi đủ các lựa chọn policy.
- `Source/ANANTA/Private/CoastalHUD.cpp`: có prompt xe/prop; không có prompt passenger train, flight altitude hay điều khiển chèo riêng. Marker `P4A_INTERACTION_PASS` chỉ mô tả một lần gọi `Use`, không phải gate tổng thể.

## Phân hệ và giới hạn bằng chứng

| Hạng mục | Nguồn native hiện có | Thiếu / QA hiện tại |
|---|---|---|
| NPC schedule | `CoastalInteractable.cpp:101,119,164`: phase từ vị trí gốc; sin quanh điểm neo, distance gating 3200 cm; tùy chọn hide/collision khi inactive. | Không phải lịch theo giờ, waypoint/navmesh, hoạt động venue hoặc skeletal walk. `SetActorLocation` không sweep; không liên hệ day/night/save. Tick return sớm khi `!bScheduleEnabled`, nên chỉ bật distance gating không đủ cập nhật activation. QA chỉ đếm 23 NPC có flag và một NPC đổi vị trí sau 0.4 s. |
| Aircraft/helicopter | `Source/ANANTA/Private/CoastalVehicle.cpp:35,224,260`: enum, giới hạn tốc độ, WASD throttle/yaw, possession Board/Leave; aircraft yaw chậm hơn. | Không input ascend/descend, pitch/roll, takeoff/landing, altitude dynamics. Z giữ nguyên do chỉ chuyển theo forward có yaw. QA `aircraft_and_heli_control_states` chỉ đếm type, không lái chúng. |
| Rowboat | Cùng Board/Leave; W/S điều tốc, A/D yaw; clamp XY biển riêng; `RowingFeedback` tăng và mesh yaw sin 4 độ (`CoastalVehicle.cpp:334`). | Không có tay chèo, chân tay người, animation/IK hay nhịp stroke theo input. Driver bị ẩn. Feedback vẫn tăng tối thiểu 0.5 khi tốc độ bằng 0, và state vẫn Rowing. QA Board trực tiếp rồi bơm W 0.8 s; chỉ kiểm di chuyển >40 cm, không kiểm animation/input E. |
| Railway stop/release | `Source/ANANTA/Private/CoastalTrain.cpp:19,150`: Stop không di chuyển; Caution 325 cm/s, Clear 650 cm/s; dwell ga, swept move và route wrap. | Không thấy native caller nối traffic/signal actor với train ngoài QA; signal traffic Kind6 chỉ đổi chuỗi/state riêng. QA đổi Stop/Clear rồi `HoldAtStationForBoarding`, không quan sát tàu tiến lại sau release. |
| Train boarding/alighting | `CoastalTrain.cpp:51,86`: API Board có distance/controller/state check; Alight tìm floor/capsule trống; counters/log. | Không E target/caller; Board không attach passenger, chuyển camera hay lưu passenger transform; hidden pawn vẫn ở vị trí cũ và movement disabled. Alight không kiểm tàu đang dừng. QA teleport player tới tàu rồi gọi Board/Alight ngay; không chứng minh ride. |
| Vehicle route bounds | `CoastalVehicle.cpp:72,260`: normalize min/max, clamp XYZ dự kiến; swept move; RouteLimit/RouteBlocked; rowboat box riêng. | Clamp origin chứ chưa inset theo rotated/scaled collision bounds; cần probe thân xe, không chỉ tâm. `Tools/Upgrade/coastal_scene.py:174` đặt box chung [-24000,-30000,-1000]..[74000,30000,12000], chưa phải route từng loại hay map readback. QA chỉ đếm `bRouteBounded` >=5. |
| P4C persistence | `Source/ANANTA/Private/City/ANANTACitySubsystem.cpp:154` trở đi có schema2 mutations, save rollback, backup/readback; City player/car capture riêng. | Không tìm thấy native Coastal calls cho door/prop/NPC/transit/signal/inventory/tokens/daynight. Metadata SaveKey chưa nối save/restore. `SaveProgress` cast City controller và City vehicle, không Coastal. |
| Economy/service/mission | City có actor thật `CityServiceInteractable`, mission state machine giver→3clues→3enemies→fragment→return; City controller E gọi actor. | Đây là đường ANANTA_City; Coastal Kind0 chỉ response. `Economy.Inventory/CityTokens` chỉ được fixture gọi trong tìm kiếm hiện tại. Mission hoàn thành đặt `Mission.RewardCount=1`, không đồng thời tăng `Economy.CityTokens`, dù objective text nói 1 city token. Không coi hai field đã đồng bộ. |

## Những lỗi state cần sửa hẹp trước khi nâng gate

1. **Availability phải thống nhất.** Cho selection, HUD và execution cùng dùng availability; kiểm trước elevator teleport. Test disabled/inactive/item-used không được chọn hoặc mutate; failure message có lý do. Không tự đổi các actor hiện tại thành interactive chỉ vì có metadata.
2. **Train state đang quá rộng.** `Source/ANANTA/Public/CoastalTrain.h:63` dùng `TrainState != Running` làm `IsStopped()`, nên Blocked/Boarding/Alighting cũng là stopped. Một Board thất bại có thể đặt Blocked rồi làm lần Board sau vượt qua check dừng khi signal Clear. Cần tiêu chí stopped-at-station/dwell tách khỏi error state; Alight phải cùng tiêu chí. Không dùng counter thay cho vị trí ride.
3. **Station predicate chỉ đúng ga ở X=0.** Tick kiểm `PreviousX * Location.X <= 0` và đặt X=0, dù API có StationLocation khác 0. Nếu cần support ga authored khác 0 phải kiểm crossing station coordinate/distance, giữ route alignment. `Direction` chỉ được QA đối chiếu; chuyển động thực lấy actor forward.
4. **Stop dwell bằng 0 có thể giữ mãi.** Vehicle `SetStop` cho phép DwellSeconds=0; nhánh at-stop luôn reset 0 rồi return, không tới nhánh disable-stop. Sửa lifecycle stop một lần, kiểm 0 và >0, resume qua input thật.
5. **NPC schedule chưa phải schedule thật.** Tách activation khỏi `bScheduleEnabled`, route/schedule theo time-of-day và chuyển hoạt động có ID ổn định. Bổ sung collision/navigation, locomotion animation và save capture ở checkpoint, không gọi SaveGame mỗi frame.
6. **Flight và rowing cần triển khai thật trước đổi tên gate.** Flight có input dọc/attitude/giới hạn/trạng thái takeoff-land; rowing có stroke/input và animation nhìn thấy. Có thể bàn giao phần kinematic bounded rõ ràng, nhưng không ghi physics/buoyancy đã có.
7. **Actor persistence phải restore trước interaction.** Dùng ID authored ổn định; fallback actor FName có thể đổi khi rebuild. Door toggle hiện chỉ có API `MarkDoorOpened` kiểu set một chiều; cần chốt ý nghĩa current-open hay ever-open rồi implement close/restore tương ứng. Prop/item restore visibility/collision; NPC phase/activation; xe transform/stop/occupancy; train signal/station. Không restore hidden passenger mà thiếu controller/camera/safe exit.
8. **Economy/mission phải có transaction semantics.** Nối một venue nhỏ và reward thật; kiểm chống nhận trùng, save failure, reload. Tránh chỉ gọi SetCityTokens để fixture đẹp. Giữ City contract cũ và QA slot riêng; không ghi production save trong smoke.

## QA hiện tại chứng minh điều gì

- `Source/ANANTA/Private/CoastalQAGameplay.cpp:24`: đa số interaction count gọi `Use()` trực tiếp, còn một door thực sự nhận E sau teleport. Có synthetic InputKey W cho đi bộ/road vehicle/rowboat. Board/Leave vẫn gọi API. Không có hành trình đi bộ tới mọi venue, train ride input, flight hay rowing animation check.
- `CoastalQAGameplay.cpp:149`: Stop/Clear/Board/Alight được API test ngay, không chờ delta position. Các tên `aircraft_and_heli_control_states`, `train_signal_release_and_station_stop`, `vehicle_route_bounds_authored` mạnh hơn nội dung assertion; phải báo bằng nội dung thực tế.
- `Source/ANANTA/Private/QA/CityPersistenceCheckSubsystem.cpp:169,218`: fixture mutate schema2, so primary/backup và reload khác process. `StartRun` chỉ nhận ANANTA_City + CityQASlot; receipt `:286` ghi rõ `fixture_mode=true`, `backend_economy=fixture_only`, `native_coastal_actor_hooks=false`. Các actor thật không được restore/quan sát trong fixture này.
- `Source/ANANTA/Private/Tests/CityPersistenceTests.cpp`: migration schema1, roundtrip schema2, defaults, rejected schema/invalid data là data gates; audit không chạy lại. Không đổi thành headed actor acceptance.
- City có input journey riêng tại `Source/ANANTA/Private/QA/CityMissionCheckActions.cpp`, đi route bằng W/Shift, E và combat; chỉ xác nhận source capability của City trong audit này, chưa có fresh run.
- `Source/ANANTA/Private/CoastalQA.cpp:52` metadata resolution là literal 1920x1080; cần actual viewport readback cho gate hình ảnh/performance. `CoastalHeroOnly` tạo 5 camera đều `bMeasure=false`. Không dùng hero-only, config t.MaxFPS60, C++ build hoặc NullRHI làm bằng chứng 60 FPS.

## Tranche tiếp theo và fresh runtime acceptance

Thực hiện từng tranche trên main, root kiểm ownership/diff trước sửa; không mở rộng toàn map trước hero. Mỗi receipt ghi UTC, commit/source hash, map identity, command, actual viewport/renderer, QA slot, input path và log mới. Không cần soak hoặc benchmark dài.

| Tranche | Gate runtime ngắn cần thu |
|---|---|
| G1a metadata/availability | Một door, item, elevator, NPC, service ở Coastal; tiếp cận bằng WASD/E, enabled và disabled; đo rotation/visibility/collision thực, elevator landing bị chặn, không teleport khi disabled. Log actor IDs + before/after; screenshot eye-level. Service chỉ text phải ghi text/static dressing. |
| G1b train | E lên tàu đang dừng đúng ga, camera/character đi cùng tàu; red giữ transform qua nhiều tick; clear cho delta dọc route >0; E xuống chỉ khi ga/dừng và có capsule-safe exit; no-exit/moving giữ passenger an toàn. Không gọi HoldAtStation làm bằng chứng release. |
| G1c vehicle/flight/row | Road/boat đi bằng input E/WASD; probe mọi cạnh/corner với mesh/collision transformed bounds; stop 0/>0 resume. Flight input làm Z/pitch/roll thay đổi, land rồi exit an toàn. Rowing stroke nhìn thấy tương quan input/speed, idle không giả rowing. Không claim physics. |
| G1d persistence actors | Process1 tương tác actor thật với stable ID trong isolated QA slot; lưu rồi thoát. Process2 load cùng map, đọc chính actor door/item/NPC/vehicle/signal/service; so transforms, collision, prompt và state. Verify primary/backup; thử duplicate/reload và save failure; vẫn ghi fixture-only nếu actor hook chưa có. |
| G1e một venue/mission | Một service có hiệu ứng thật, inventory/token ledger, nhiệm vụ ngắn input thường, reward duy nhất kể cả lặp E/restart. Chụp state trước/sau và reload, bảo toàn City mission/service hiện có. |

Audit không sửa Source/Content/Config, không nhận hoặc commit các tool untracked A1–A6/W3 cũ, không tạo runtime/PASS mới. Các kết luận về caller được xác nhận bằng tìm kiếm trong Source/ANANTA; Blueprint/binary có thể bổ sung hành vi nhưng cần graph readback và runtime riêng trước khi nâng gate.
