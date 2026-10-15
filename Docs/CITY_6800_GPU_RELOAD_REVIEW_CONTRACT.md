# Hợp đồng rà lỗi GPU/reload 6,8 km

## Phạm vi chung

- Unreal 5.8.3, D:\GAME\ANANTA; nhánh codex/city-expansion.
- Nguồn map /Game/ANANTA/Maps/ANANTA_City rộng 6.788,2250993908565 m.
- Apply 85.386 nhóm/1.660.761 instance; readback 86.180 non-HLOD actor.
- Rail/Rowboat/RoofPool và năm vùng xe đã PASS; HLOD/ảnh/EXE 6,8 km vẫn đang thực hiện.
- Chỉ một process Unreal; agent rà này không mở engine/game hoặc compile DLL.
- Giữ model nhân vật, save cá nhân và các thay đổi chưa stage.

## Dữ liệu/performance contract

- Base custom Max: native 1920×1080, scale 100, sg.* 3, cap 90, VSync 0.
- HWRT 0, SMRT rays 4, GI 24, reflection 2, TSR history 100, VSM bias -1,5.
- GI32/Reflections4/VsmBias0 chỉ đổi một cvar ở cùng package; giữ mọi frame.
- Test-CityMaxGraphics.ps1 nhận INNER ANANTA/Binaries/Win64/ANANTA.exe.
- Trial.json schemaVersion 1 chứa package hash, variant, cvar và source evidence.
- Slot QA ANANTA_City_QA.sav/QA_Backup được phục hồi; không sửa City_v1.
- Các trial chưa chạy; không kết luận 90 FPS hoặc reload hết crash từ cvar/config.

## Công việc và đầu ra duy nhất

- Đọc log crash D3D12 PageFault cũ, nguồn render settings và runner EXE hiện tại.
- Dùng rg để tìm log; chỉ mở file liên quan, không quét dump nặng toàn ổ.
- Tài liệu được tạo/sửa duy nhất: Docs/CITY_6800_GPU_RELOAD_DIAGNOSIS.md.
- Báo cáo nêu evidence/log chính xác, nguyên nhân đã/chưa xác nhận, gate cần chạy trong EXE mới.
- Phân biệt crash trước menu/reload và quan sát bình thường; không đề xuất tắt tính năng như đã sửa.
- Có thể tra tài liệu chính thức Epic nếu cần; ghi URL hỗ trợ kết luận.
- Không chỉnh source/config/assets/save; không commit/push; không tạo subagent.

## Kiểm chứng

- Mỗi kết luận gắn với file/log và marker/timestamp thực; giả thuyết ghi rõ là giả thuyết.
- Tài liệu dưới 300 dòng, dòng khoảng dưới 120 ký tự; git diff --check cho tệp tài liệu đạt.
- Báo cáo một lần tối đa 15 dòng: file, kiểm chứng, vấn đề còn mở.
