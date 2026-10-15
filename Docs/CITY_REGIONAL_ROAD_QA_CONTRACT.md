# QA tuyến đường ở vùng mở rộng

Repo D:\GAME\ANANTA, UE 5.8.3. Main đang apply map, đã dừng driver chờ build riêng.
Không mở Unreal, không build/run workload, không tạo agent con, không commit/push.

## API/hằng số đã có

- CityMobility::MakeNearbyRoute(ECityTransportKind Kind, const FVector& PlayerLocation).
- FCityTransportRoute: Id, Points, Stops, ReverseTargets, bWater, bRail.
- MakeRoute giữ tuyến core; MakeNearbyRoute chọn vòng đường cố định theo khu vực.
- MaximumVehicles=8 là budget game; fixture vật lý không dùng để chứng minh FPS.
- Capsule/mesh/velocity/route/collision giữ nguyên. Không thêm sàn hỗ trợ giả.
- Map ANANTA_City World Partition; streaming source fixture radius 62000 cm.

## Chế độ cần thêm

- Test-CityRoadRoutes.ps1 có Region = Core (mặc định), East, West, South, NorthEast.
- Điểm chọn tuyến: East=(200000,0,100), West=(-244000,420,100),
  South=(-28000,-215580,100), NorthEast=(188000,288420,100).
- Core giữ tám loại/16 probe/schema/pass gate cũ hoàn toàn.
- Regional dùng MakeNearbyRoute cho tám loại; thay slot Ambulance bằng FireEngine.
  Mỗi loại vẫn có probe initial 0/2, đi đủ vòng và lên/xuống phủ cả bốn trạm.
- Thêm Kind enum vào result để Configure không suy enum từ index khi slot FireEngine=11.
- Observer đặt tại tâm bounds XY của các route regional, Z=2000; kiểm xa nhất <=58000.
- Giữ radius62000, readiness/wall-clock watchdog, floor gap/road deviation/side travel/return gates.
- Cho phép authored PassengerTrain có sẵn; không phá/hạ tick hai tàu đó.
  Vẫn từ chối fleet đường bộ không thuộc fixture; vẫn chặn transport manager cho fixture.
- Regional ghi thư mục/JSON riêng CityRoadRoutesCheck_<Region>, region và sourcePlayerLocation.
  Báo scope đúng fixture đường khu vực; các field no-bypass/no-artificial-floor phải là false.
- PS runner kiểm đúng region/kinds/fresh timestamp/marker/8 results/16 probes và gate cũ.

## Tệp được sửa/tạo độc quyền

- Source/ANANTA/Public/QA/CityRoadRoutesCheck.h
- Source/ANANTA/Private/QA/CityRoadRoutesCheck{,Fixture,Observe,Report}.cpp
- Có thể tạo Source/ANANTA/Private/QA/CityRoadRoutesCheckRegional.cpp để giữ mỗi tệp <300 dòng.
- Tools/Build/Test-CityRoadRoutes.ps1

Done: kiểm tĩnh API local UE, git diff --check, PS parse, <300 dòng/<120 ký tự/dòng.
Chưa được compile/runtime; main sẽ build rồi chạy Core và bốn region nối tiếp.
Giữ default behavior; không sửa các subsystem/actor/gameplay ngoài danh sách, asset, map hay save thường.
Báo một lần tối đa15 dòng, nêu tệp, cách tự kiểm và các vấn đề còn mở.
