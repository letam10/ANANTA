# Hợp đồng runner settings / reload diagnostic

## Mục tiêu và phạm vi

Repo D:\GAME\ANANTA, Unreal 5.8.3. Base native PageFault; shadow async=1 chạy gameplay PASS.
Root đang chụp ảnh GPU riêng; agent chỉ sửa runner/test/docs, không chạy game/build.

## API chung đã có

Tools/Build/CityGraphicsTrialEvidence.ps1 exports:

- Get-CityQASlotSnapshot([string] SavedRoot): array entry Path, Existed, Bytes và metadata UTC/attributes.
- Reset-CityQASlots([string] SavedRoot, [array] Snapshot): chỉ hai tên QA được chấp nhận.
- Restore-CityQASlots([string] SavedRoot, [array] Snapshot): phục hồi byte/metadata; xác nhận byte giống.
- Get-CityPackageFingerprint([string] ExecutablePath): reject bootstrap; trả executable/containers SHA256.
- Assert-CityFreshEvidence([string] Path, [datetime] StartedUtc): bắt report/log cũ.

## Phân công độc quyền

Chỉ được sửa Tools/Build/Test-CitySettings.ps1 và tạo:

- Tools/Build/Test-CitySettingsRound.ps1.
- Tools/QA/TestCitySettingsDiagnostics.ps1.
- Docs/CITY_6800_SETTINGS_DIAGNOSTIC_RUNNER.md.

Root sở hữu source C++, capture/graphics runner và các status/contracts khác.

## Yêu cầu cụ thể

1. Settings runner thêm Diagnostic enum None/NaniteShadowAsyncOn, mặc định None giữ API cũ.
2. Diagnostic suffix riêng cho QA/config/log; chỉ shadow override=1; giữ mức native Height 1080.
3. Không làm mất cặp Check/Reload: cùng config diagnostic và evidence mới theo timestamp.
4. Round runner bắt inner packaged EXE, fingerprint, snapshot/reset hai QA slot trước Check,
   chạy Check rồi Reload tuần tự; finally phục hồi snapshot dù game/gate ném lỗi.
5. Round.json schemaVersion=1: diagnostic, startedUtc, completedUtc, artifactFingerprint,
   checkPassed, reloadPassed, qaSlotsReset, qaSlotsRestored, status PASS/FAIL.
6. Không nhận FPS/visual/stability từ hai stage này; diagnostic chỉ là kiểm menu/reload.
7. Test stub hoặc AST/thư mục tạm không chạy Unreal: suffix/override/Check-Reload/finally failure.
8. PS AST parse và test script phải PASS; mỗi file <300 dòng, dòng khoảng <120 cột.

## Không làm và báo cáo

Không sửa helper chung, C++/config/map/model/save thật, không build/game/commit/push hoặc spawn.
Giữ mọi evidence thất bại; dùng LiteralPath, không xóa đệ quy.
Báo cáo một lần tối đa 15 dòng: files/checks/open issues; root thực hiện runtime.
