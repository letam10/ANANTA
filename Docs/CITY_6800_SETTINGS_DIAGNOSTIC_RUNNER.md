# Settings Check + Reload được bảo vệ

Chạy từ `D:\GAME\ANANTA`, dùng EXE bên trong gói Development:

```powershell
powershell -NoProfile -File Tools/Build/Test-CitySettingsRound.ps1 `
  -ExecutablePath '<package>\ANANTA\Binaries\Win64\ANANTA.exe' `
  -Diagnostic NaniteShadowAsyncOn
```

Bỏ `-Diagnostic` để chạy mặc định `None`. Diagnostic chỉ thêm
`-ForceDPCVars=r.Nanite.AsyncRasterization.ShadowDepths=1`, giữ 1920x1080.
Không chạy đồng thời với settings runner khác trên cùng gói: runtime ghi vào
`<package>\ANANTA\Saved\QA\CitySettings` theo API hiện có.

Wrapper xác nhận EXE trong `Binaries\Win64`, hash EXE và các container, snapshot hai slot
`ANANTA_City_QA.sav` / `ANANTA_City_QA_Backup.sav`, reset rồi chạy Check và Reload tuần tự.
Reload dùng nguyên config và save QA do Check tạo. `finally` phục hồi byte, timestamp và
attributes cũ; slot trước đó không tồn tại sẽ được xóa nếu lần kiểm tra tạo ra.
Các slot của người chơi không nằm trong phạm vi thao tác.

Mỗi vòng có ID UTC + GUID riêng, giữ cả evidence thất bại:

- `Saved/QA/CitySettingsPackaged[Diagnostic]-<RunId>/Round.json`.
- Cùng thư mục: `GameUserSettings.ini`, `Check/`, `Reload/` và stderr của từng stage.
- `Saved/Logs/CitySettingsPackaged[Diagnostic]-<RunId><Mode>.log` và console tương ứng.

`Round.json` schemaVersion=1 chứa diagnostic, startedUtc, completedUtc, artifactFingerprint,
checkPassed, reloadPassed, qaSlotsReset, qaSlotsRestored, status (`PASS`/`FAIL`). Khi lỗi,
error hoặc restoreError ghi nguyên nhân. PASS yêu cầu cả hai stage và khôi phục slot thành công.
Log, report, ảnh phải mới hơn thời điểm bắt đầu stage; config Check cũng phải mới.
Runner lưu bản sao report/ảnh mới kể cả khi process thất bại, không dùng report cũ để cho PASS.

`Test-CitySettings.ps1` vẫn hỗ trợ API cũ (`-Reload`, `-Height`, `-ExecutablePath`, `-EngineRoot`).
Thêm `-Diagnostic` và `-RunId` tùy chọn; wrapper truyền cùng RunId cho cả hai stage.
Không truyền RunId thì đường dẫn mặc định cũ được giữ; dùng wrapper để lưu lịch sử riêng từng vòng.
Diagnostic từ chối Height=720. Hai stage chỉ kiểm menu và đọc lại settings sau khi khởi động lại;
PASS không xác nhận FPS mục tiêu, chất lượng ảnh, độ ổn định dài hạn hay Max mặc định.

Kiểm tra tự động không chạy Unreal và chỉ dùng fixture trong thư mục tạm:

```powershell
powershell -NoProfile -File Tools/QA/TestCitySettingsDiagnostics.ps1
```

Test parse AST, kiểm 16 vòng stub cho cả hai diagnostic: thành công, lỗi Check/Reload,
lỗi khởi chạy, log/report/ảnh/config cũ. Kiểm thứ tự stage, config chung, override một biến,
đường dẫn riêng, fingerprint, khôi phục byte/metadata, bảo toàn save người chơi và chặn bootstrap/720p.
Một cặp Check/Reload riêng xác nhận API và đường dẫn mặc định cũ vẫn hoạt động.
Fixture được giữ lại để xem evidence; đây là kiểm chứng runner, chưa phải chạy game thật.
