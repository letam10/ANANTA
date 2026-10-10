# Vòng native Nanite 6,8 km — 2026-10-10

## Đã chạy, cùng package City6800

- Base FAIL exit 3: D3D12 PageFault ở frame 39, chưa có FPS hợp lệ.
- NaniteAsyncOff FAIL exit 3: log xác nhận global async=0, PageFault ở frame 36.
- NaniteShadowAsyncOn PASS exit 0: chỉ ForceDPCVars shadow async=1, global async vẫn 1.
  Hoàn tất tám dịch vụ bằng gameplay thông thường, không benchmark.
  20.167 frame / 281,757528 giây; trung bình 71,575727 FPS; p95 16 ms; max 387,152 ms.
  Giữ đủ ba frame trên 33,3 ms và ba trên 50 ms; stable90Accepted=false.
  GPU 13,381006 ms, render thread 13,947003 ms, game thread 4,227760 ms trung bình.
- Native 1920×1080 / r.ScreenPercentage=100; mười nhóm sg.*Quality=3; VSync=0; cap=90.
  VSM bật, ray directional/local=4; GI=24; reflection=2; TSR history=100; HW ray tracing=0.
- Một lượt chạy được chưa chứng minh nguyên nhân hoặc độ ổn định qua camera/reload.
  Không áp dụng shadow async vào preset sản phẩm trước kiểm ảnh và reload.
- Settings shadow diagnostic: Check PASS, Reload FAIL exit 3 với PageFault; slot QA phục hồi.
  RunId `20261010T051302934-ee0861d8e6874febbd92c806b506ca93`, cùng fingerprint package.
- DRED + TrackAllAllocations=1 PASS một hành trình, 17.180 frame / 281,926276 giây.
  60,937917 FPS, p95 26,177 ms, max 383,493 ms; 72 frame trên 33,3 ms, tám trên 50 ms.
  Log xác nhận DRED/allocation tracking bật; overhead không dùng làm nghiệm thu Max thông thường.
  Không tái hiện fault ở lượt này, không có bằng chứng resource gây lỗi hoặc đã sửa lỗi GPU.
- Editor build QA PASS 49,99 giây; metro native shadow diagnostic hoàn tất 30 PNG và sáu contact.
  Đã xem đủ sáu contact, sửa/chụp lại sàn và vật liệu thuyền; góc tàu còn bị cột ga che một phần.
- Cặp Check-On/Reload-Off PASS, run `20261010T074919491-b1b4510515a447a3937832bdf34029f5`.
  EXE/containers cùng hash, INI trước/sau copy/Reload cùng SHA 8F26CD40837B9ACC, slot QA phục hồi.
  Diagnostic startup ghi global async=1/shadow async=0 cho Reload; chưa tính đạt Max/90 FPS.
- Đối chứng On/On run `20261010T075538957-ce20e6f5deb341378a9d01e9a3350a31` FAIL ngay Check.
  GPU crash exit 3 lúc 07:55:49 UTC, frame 45; chưa tới Reload, slot QA đã phục hồi.
  Shadow async On vẫn có thể lỗi lúc khởi động; không đủ bằng chứng nguyên nhân hoặc fix.
- Thuyền đã reimport/binding/physics/năm ảnh native PASS; props nhỏ capture 45 ảnh/chín contact PASS.
  Review props phát hiện nồi chồng vùng ấm và góc compact bị chân đèn che; xem CITY_6800_SMALL_VISUAL_REVIEW.md.

## Bằng chứng

- Saved/QA/CityMaxGraphicsPackaged/Trial.json: Base fail, hai slot QA phục hồi trong finally.
- Saved/Logs/CityMaxGraphicsPackagedNaniteAsyncOff.log: override và PageFault thực.
- Saved/QA/CityMaxGraphicsPackagedNaniteShadowAsyncOn/Trial.json, Summary.json,
  FrameTimes.csv, RenderConfig.txt; log cùng tên trong Saved/Logs.
- Các trial fingerprint cùng EXE/containers; package EXE SHA bắt đầu 25B6541949602B8B.
- Source QA đã thêm cvar shadow async vào observation/capture cho lượt build kế tiếp.
- Saved/QA/CitySettingsPackagedNaniteShadowAsyncOn-<RunId>/Round.json và Check/Reload logs.
- Saved/QA/CityMaxGraphicsPackagedDred/{Trial,Summary}.json, FrameTimes.csv, RenderConfig.txt.
- Saved/QA/CityPlacement_metro_NaniteShadowAsyncOn: lượt đầu cần lưu riêng trước chụp lại.

## Tiếp tục

1. Sửa placement/camera props và tàu còn lỗi; thuyền đã đạt gate sửa sàn/vật liệu/placement.
2. Rà fault khởi động từ control On/On mới FAIL và cặp On/Off PASS; chưa thay đổi preset.
3. Sửa/chụp lại props còn lỗi và chụp công trình; xem năm góc từng vị trí.
4. Rà HISM/streaming độc lập; tối ưu theo render/GPU 13–14 ms, không suy ra 90 FPS từ cap.
5. Cập nhật status, commit/push mã/tài liệu; map binary chờ gate hình ảnh/runtime hoàn tất.
