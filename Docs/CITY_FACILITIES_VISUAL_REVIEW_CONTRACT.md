# Hợp đồng review công trình native, 2026-10-10

- Root phụ trách source, props nhỏ, Docs tổng và Git; subagent chỉ review công trình.
- UE 5.8.3, repo D:\GAME\ANANTA; không chạy engine/game/Blender hoặc sửa asset/map/source.
- Capture đã hoàn tất: `Saved/QA/CityPlacement_facilities_Dred/`, 50 PNG/10 contact native 1920x1080.
- Schema index: scope, diagnostic, nativeCaptureCount, contacts[].index/id/contact/images/visualAccepted.
- Các id: Station, Hotel, Restaurant, Theater, Cinema, Cafe, Pool, Factory, Airport, Highway.
- Mỗi contact chứa front/rear/left/right/upper, view PNG tương ứng trong Manifest.json.
- Chỉ được tạo/sửa `Docs/CITY_6800_FACILITIES_VISUAL_REVIEW.md`.
- Đọc RenderConfig.txt/manifest/index và mở xem đủ mười contact; mở PNG gốc khi nghi bị che/cắt.
- Ghi bảng từng id: thấy đủ năm góc hay chưa, geometry/placement lỗi rõ, mức độ prototype còn lại.
- Không suy FPS/va chạm/khả năng vào nhà từ ảnh. DRED là diagnostic, GPU Base/reload chưa ổn định.
- Không nhận đồ họa cuối chỉ vì có đủ PNG; không tự sửa hoặc hide actor để nghiệm thu.
- Done: Doc ngắn dưới 120 dòng, liệt kê đủ mười id và việc còn mở; git diff --check trên file riêng.
- Không commit/push, không gửi followup, không subagent. Báo một lần tối đa 15 dòng khi xong.
