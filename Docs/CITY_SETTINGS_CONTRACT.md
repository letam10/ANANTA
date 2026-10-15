# Hợp đồng cài đặt trong game — 2026-10-08

## Phạm vi và tiêu chí

- Unreal 5.8.3 C++, màn hình 1080p; không thay model nhân vật hoặc gameplay thành phố.
- Nút cài đặt và phím Esc/F10 mở menu, tạm dừng game; đóng menu trả điều khiển chuột về game.
- Đồ họa có preset và các nhóm chất lượng riêng, TSR render scale, giới hạn FPS và VSync.
- Tiếng Việt/English, bật/tắt thanh FPS; lưu lựa chọn qua lần khởi động tiếp theo.
- FPS lấy từ thời gian frame thực, không dùng thời gian mô phỏng hay giá trị cap giả làm FPS.
- Mục tiêu mới: khoảng 90 FPS ở mức tối đa trên máy hiện tại. Chưa đạt nếu chưa có bằng chứng.
- Tối đa = UE Epic (3), render scale 100%; không đổi nhãn High thành Max. Cinematic không dùng khi chơi.
- Không benchmark; kiểm tra menu và một lượt chơi ngắn, ghi cả khựng và cấu hình thực tế.

## Giao diện chung — backend sở hữu

Header: `Source/ANANTA/Public/Settings/ANANTAGraphicsSettings.h`.

`FCityGraphicsOptions` là struct C++ thường với các trường sau:

- int32 ViewDistance, AntiAliasing, Shadows, GlobalIllumination, Reflections;
- int32 PostProcess, Textures, Effects, Foliage, Shading;
- float ResolutionScale; float FrameRateLimit;
- bool bVSync; bool bShowFPS; FString Language;

Mặc định: quality 2, ResolutionScale 83.333333, FrameRateLimit 90, VSync false, FPS false, Language vi.
Chất lượng hợp lệ 0..3; render scale 50..100; FPS 0 (không giới hạn) hoặc 30..240; ngôn ngữ vi/en.

`UANANTAGraphicsSettings : public UGameUserSettings`, config GameUserSettings, API:

```cpp
static UANANTAGraphicsSettings* Get();
static FCityGraphicsOptions MakeDefaults();
static FCityGraphicsOptions SanitizeOptions(const FCityGraphicsOptions& Options);
FCityGraphicsOptions CaptureOptions() const;
void ApplyOptions(const FCityGraphicsOptions& Options, bool bSave = true);
FString GetLanguage() const;
bool IsFPSVisible() const;
```

ApplyOptions sử dụng API UGameUserSettings, ApplySettings(false), cập nhật culture, lưu khi bSave.
LoadSettings/SetToDefaults phải bảo toàn cấu hình cũ khi hợp lệ, khởi tạo thêm ngôn ngữ/FPS.
Không bật hardware ray tracing hoặc đổi cvar ngoài nhóm chất lượng mà không có nhu cầu cụ thể.

## Giao diện chung — UI sở hữu

Header: `Source/ANANTA/Public/Settings/SCitySettingsPanel.h`.
`SCitySettingsPanel : public SCompoundWidget` với Slate argument `FOnClicked OnClose`.
Root tạo bằng `SNew(SCitySettingsPanel).OnClose(...)` rồi thêm vào viewport ZOrder 100.
UI tự đọc UANANTAGraphicsSettings::Get; giữ bản nháp, chỉ Apply mới áp dụng/lưu.
Cancel/Esc/F10 bỏ bản nháp và gọi OnClose. Apply giữ menu mở, cập nhật ngôn ngữ ngay.
Default chỉ đổi bản nháp, không ghi đè lựa chọn đã lưu trước khi Apply.
Hỗ trợ keyboard Tab/Enter và chuột; focus đầu vào không truyền WASD/LMB xuống game.
Panel có scroll để sử dụng ở 720p, thiết kế gọn màu navy/teal, đủ glyph tiếng Việt.
UI có GetDraftOptions() const và ApplyDraft() để QA đối chiếu; ApplyDraft dùng cùng đường với nút Apply.
UI có SetDraftOptions(const FCityGraphicsOptions&) để QA điều chỉnh dữ liệu form và làm mới control.
Panel có SupportsKeyboardFocus() true; OnKeyDown xử lý Esc/F10 đóng menu.

## Quyền sở hữu

- Agent backend: GraphicsSettings.h/.cpp và Private/Tests/CityGraphicsSettingsTests.cpp.
- Agent UI: SCitySettingsPanel.h, Private/Settings/SCitySettingsPanel*.cpp (chia nhỏ <300 dòng/file).
- Root: controller, HUD, helper ngôn ngữ game, config/module, QA tích hợp, docs và Git.
- Không agent sửa file của root/agent khác, không Git commit/push, không build engine đồng thời.
- Không tạo subagent. Báo cáo một lần <=15 dòng gồm file, kiểm tra, vấn đề còn lại.

## Kiểm chứng

- Agent tự kiểm tra diff, giới hạn dòng, API UE 5.8 tại Engine/Source; không chạy full build.
- Root build Editor/game, automation và kiểm tra GPU menu/tiếng Việt/FPS, khởi động lại đọc setting.
- QA dùng save ANANTA_City_QA và config riêng, xác nhận save thường không đổi.
- Lưu ảnh, cấu hình có hiệu lực, input/pause/movement và thời gian frame; cập nhật file tiến độ.
