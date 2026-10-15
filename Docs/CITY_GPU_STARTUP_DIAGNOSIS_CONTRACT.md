# Chẩn đoán lỗi GPU khởi tạo — 2026-10-08

## Phạm vi

- UE 5.8.3, DX12, RTX 4060 Laptop 8 GB, driver giữ nguyên.
- Lỗi rời rạc lúc khởi tạo, không phải khẳng định thiếu VRAM hoặc lỗi UI.
- Log chính: Saved/Logs/CitySettingsCheck.GPUStartupFailure.log.
- Lỗi cũ liên quan: Saved/Logs/CityGPUCaptureBlueHour.Failure1.log nếu còn tồn tại.
- Active breadcrumbs: ShadowDepths / RenderVirtualShadowMaps(Nanite) / NodeAndClusterCull.
- Aftermath PageFault; log ghi Local Used 460,55 MB / Budget 7.188 MB.

## Đầu ra và ràng buộc

- Chỉ đọc log và mã nguồn engine C:/Program Files/Epic Games/UE_5.8/Engine/Source.
- Nếu tra web, chỉ dùng tài liệu Epic/NVIDIA chính thức và lưu URL.
- Agent chỉ tạo Saved/QA/CityGPUStartupDiagnosis.md, dưới 150 dòng.
- Phân biệt bằng chứng, giả thuyết và một phép thử ít xâm lấn có tiêu chí kiểm chứng.
- Không sửa cấu hình, driver, source game/engine hoặc chạy thêm game/build/GPU workload.
- Không Git commit/push; không subagent.
- Tự kiểm tra báo cáo tồn tại; gửi một lần <=15 dòng gồm kết luận và vấn đề chưa giải quyết.
