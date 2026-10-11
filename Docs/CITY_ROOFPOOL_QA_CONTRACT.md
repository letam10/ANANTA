# Hợp đồng kiểm cầu thang mái bể bơi trên map thật

Unreal 5.8.3, centimet, map /Game/ANANTA/Maps/ANANTA_City.
Chỉ tạo subsystem với -CityRoofPoolCheck -CityQASlot, không tạo trong Shipping.

## Hình học và API chung

- Nhà Pool centre (102000,198000). Nền sân cao 20; mái cao 840 cm.
- 41 bậc: centre X=98350, Y=195800 + index*100, cao mặt 40 + index*20.
- Bậc rộng 500, sâu 100; landing centre (98350,199975,830), size (500,250,20).
- Landing bắt đầu Y=199850 sau bậc cuối; đường sang mái tại Y=199800 đi qua bậc 40.
- Hero capsule hiện tại 38/92; giữ nguyên tốc độ, collider, CharacterMovement.
- AANANTACityController: CanCaptureProgress/GetPawn, InputKey dùng FInputKeyEventArgs.
- Input thật W để đi, controller yaw 90 cho đoạn lên (+Y), yaw 0 qua landing (+X).
- UANANTACitySubsystem::IsUsingQASlot(); không ghi save cá nhân.
- Observer có WorldPartitionStreamingSourceComponent; đợi stream ổn định hai giây.
- Tham khảo các CityDoorCheck/CityCivicCheck/CityRowboatCheck đã có, chỉ đọc.

## Chuỗi kiểm thực

1. Nạp vùng nhà Pool, đợi restore controller xong; setup hero (98350,195600,115), yaw 90.
2. Đợi capsule tiếp đất sân, W thật qua đủ 41 bậc, đo tăng Y tối thiểu 4100 cm.
3. Dừng/đổi hướng nhìn sang +X tại đầu thang; W đi qua landing đến X>=98800.
4. Xác nhận floor đứng vững cao khoảng 840, capsule không overlap; chưa có cơ chế bơi.
5. Đi ngược landing và xuống cầu thang bằng input thật, không teleport trong đoạn đo.
6. Xác nhận trở về sân, không xuyên thang/roof, số mẫu lên/xuống/floor có dữ liệu.
- Chỉ teleport lúc setup đầu, không tạo/sửa geometry, không đổi vị trí người trong leg đo.
- Timeout có báo phase/blocker và exit thất bại; không coi thiếu streaming/model là đạt.
- JSON Saved/QA/CityRoofPoolCheck/Report.json: passed/completedUtc/scope/elapsedSeconds,
  ascent/descent travel, roof height, capsule clearance, sample counts và lỗi.
- Log CITY_ROOFPOOL_CHECK_FINISH success=1 chỉ khi mọi gate đạt, exit 0/1 tương ứng.

## File sở hữu và kiểm tra

- Chỉ tạo Public/QA/CityRoofPoolCheck.h, Private/QA/CityRoofPoolCheck*.cpp dưới Source/ANANTA,
  Tools/Build/Test-CityRoofPool.ps1.
- Mỗi file dưới 300 dòng, khoảng 120 cột, comment tiếng Việt ngắn cho logic leg/input.
- Self-check API/style, parse PowerShell; ghi rõ chưa compile/runtime.
- Main biên dịch và chạy engine. Không build/launch UE, sửa map/gameplay/asset/file khác,
  spawn children hoặc commit/push. Báo một lần tối đa 15 dòng khi xong.
