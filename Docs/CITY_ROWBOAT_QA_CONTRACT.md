# Hợp đồng kiểm người chơi chèo thuyền tại bến thật

Unreal 5.8.3, centimet, map /Game/ANANTA/Maps/ANANTA_City.
Chỉ bật với -CityRowboatCheck -CityQASlot; Shipping không tạo subsystem.

## ABI và dữ liệu đã có

- ACityRowboat : AANANTACityVehicle, header City/Mobility/CityRowboat.h.
- AANANTACityVehicle: public bool bOccupied, float GetSpeedKmh() const,
  virtual bool FindSafeExit(const APawn*, FVector&) const; không đổi ABI.
- AANANTACityController::GetInteractionPrompt() const trả English; HUD tự dịch.
- Nút thật: E lên/xuống; W chèo tiến; Space phanh. Dùng Controller->InputKey,
  FInputKeyEventArgs(nullptr, INPUTDEVICEID_NONE, Key, IE_Pressed/Released, 1/0, false).
- Thuyền authored Living_PlayerRowboat, (129440,-137000,-120), yaw 90.
- Bến timber: min (127940,-137300,-35), max (129300,-136700,15).
- Chuẩn bị hero tại (129240,-137000,110), capsule hiện tại 38/92; không đổi size/collision/tốc độ.
- FindInteractionTarget giới hạn 320 cm và line visibility; Controller phải restore xong.
- ANANTACitySubsystem::IsUsingQASlot() xác nhận save QA; không chạm save cá nhân.

## Phạm vi kiểm chứng

1. Observer có WorldPartitionStreamingSourceComponent tại bến; đợi completed ổn định.
2. Dời hero chỉ khi chuẩn bị lượt; giữ physics và CharacterMovement trong đoạn đo.
3. E qua hệ thống input thật: bOccupied, hero ẩn/attached đúng actor.
4. Giữ W khoảng 1 giây, nhả W, giữ Space đến dừng; ghi quãng đường thực >20 cm.
5. E xuống: hero hiện, collision/movement walking, có floor bến và capsule không overlap.
6. Sau lượt đo, dời thuyền riêng tới (150000,-130000,-120) để chuẩn bị thử xuống giữa biển;
   FindSafeExit phải false. Ghi rõ đây là setup riêng, không tính quãng đường gameplay.
7. Báo JSON trong Saved/QA/CityRowboatCheck: passed, completedUtc, scope, phase outcomes,
   elapsedSeconds, measuredTravelCm, capsule/board/alight/dryFloor/openSeaExitRejected.
   Log CITY_ROWBOAT_CHECK_FINISH success=1 chỉ khi mọi gate đạt; exit 0/1 phù hợp.

## Quyền sở hữu của subagent

- Chỉ tạo Source/ANANTA/Public/QA/CityRowboatCheck.h,
  Source/ANANTA/Private/QA/CityRowboatCheck*.cpp, Tools/Build/Test-CityRowboat.ps1.
- Mỗi file dưới 300 dòng, khoảng 120 cột; comment tiếng Việt ngắn cho state/input phức tạp.
- Không sửa controller/save/thuyền/bản đồ/asset hoặc file người khác.
- Không launch Unreal hoặc build DLL: main đang chạy GPU QA và sẽ biên dịch sau báo cáo.
- Self-check cú pháp PowerShell, style/source references; báo rõ chưa compile/runtime.
- Không spawn agent, không commit/push; xong báo một lần tối đa 15 dòng.
