# Hợp đồng regression dò sàn dưới mái sân ga

Unreal 5.8.3, cm; main đang chạy ApplyCityExpansion, không build hoặc mở UE song song.

## ABI và hình học chung

- ACityRouteVehicle::Configure(kind, route, mesh, initialPoint) đã có.
- DoorAndSidewalk(FVector&, FVector&) const là private; có thể thêm friend class
  FCityRailCanopyTest cho automation, không tạo API gameplay/config mới.
- Source actor tâm hull: OriginHeight = mesh bounds centre Z + 5; mesh dịch -bounds centre.
- SurfaceZ = actor location Z - OriginHeight. Rail surface 51, platform top 100.
- Station local track Y=500, platform centre Y=1370, width 940, length 8000.
- Mái có bảy dải Y=890+band*160, width 180, Z=720-abs(band-3)*45, thickness 35.
- Door rail ở right 430, sidewalk right 800; capsule NPC 32/92, floor Z+95.
- Dò cũ từ actor-centre Z+600 có thể trúng mái thay vì sàn; rise hơn 180 bị từ chối.
- Giữ AllowedRise water/rail 180, road 40; giữ floor normal/capsule/sweep gates.

## Nhiệm vụ và ownership

- Chỉ sửa Source/ANANTA/Private/City/Mobility/CityRouteVehicleStops.cpp,
  Source/ANANTA/Public/City/Mobility/CityRouteVehicle.h (friend declaration duy nhất),
  tạo Source/ANANTA/Private/Tests/CityRailCanopyTests.cpp.
- Test world isolated theo CityRowboatTests/CityFleetTests; dùng mesh train nhập thật,
  platform/canopy đúng kích thước source, không sửa asset/capsule hay tốc độ.
- Tái hiện ray cũ bắt mái; hàm đã sửa phải tìm platform 100 ở hai phía ga và có đường capsule.
- Bổ sung vật cản tại cửa: vẫn phải từ chối, không bỏ kiểm va chạm để làm test đạt.
- Sửa đơn giản: dò từ cao độ mặt chạy, dưới mái có đủ không gian cho người; không hardcode ga X/Y.
- Mỗi file dưới 300 dòng, khoảng 120 cột; comment tiếng Việt ngắn cho ray từ dưới mái.
- Self-check API/style; main sẽ build/run test sau UE thoát. Báo rõ chưa compile/runtime.
- Không launch/build UE, sửa map/asset/code khác, spawn con hoặc commit/push.
- Xong báo một lần tối đa 15 dòng: files, kiểm tra, phần chưa kiểm.
