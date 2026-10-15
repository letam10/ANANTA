# Rà PageFault native 6,8 km

- Repo D:\GAME\ANANTA, UE 5.8.3 tại C:\Program Files\Epic Games\UE_5.8.
- Actor map /Game/ANANTA/Maps/ANANTA_City; chiều rộng 6.788,2250993908565 m.
- Apply/readback/vật lý và HLOD PASS 3.557 proxy/1.619.348 instance; không chỉnh map này.
- Max custom native 1920×1080/100%, sg 3, rays 4, GI 24/reflection 2/VSM bias -1,5/TSR history 100.
- Capture đầu sai render scale 3% đã loại, archive Saved/QA/CityPlacement_metro_Scale3Rejected.
- Capture native mới FAIL exit 3 trước ảnh đầu, log Saved/Logs/CityPlacement_metro.log lúc 03:53:48 UTC.
- Actual log: ReservedResources=0; PageFault trong Nanite NodeAndClusterCull/VSM; chưa biết nguyên nhân.
- Không in XML crash/dump dài; chỉ marker/line cần thiết, giữ dữ liệu cá nhân ngoài báo cáo.
- Root chuẩn bị package; agent không mở UE/Blender/game hoặc compile/cook/test runtime.

## Đầu ra và quyền sửa

- Chỉ tạo/sửa Docs/CITY_6800_NANITE_NATIVE_DIAGNOSIS.md, dưới 300 dòng, khoảng dưới 120 ký tự/dòng.
- Rà nguồn renderer/shader UE cài sẵn để lấy giới hạn buffer chính xác và guard overflow.
- Đối chiếu tài liệu chính thức Epic; URL Nanite Technical Details:
  https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-technical-details
- Phân biệt evidence culling/PageFault với giả thuyết buffer/async/driver; không kết luận từ breadcrumb alone.
- Đề xuất tối đa hai phép thử có một biến, khởi động bằng QA INI riêng nếu cvar không đổi runtime.
- Ghi giá trị gốc/mới và chi phí RAM tính từ source; không tự áp dụng hoặc hạ chất lượng để nhận Max.
- Không sửa source/config/assets/save, không commit/push, không spawn hoặc gửi task khác.

## Done

- Báo cáo có đường dẫn/line/source chính thức cho mọi fact, giả thuyết đánh dấu rõ.
- git diff --check -- Docs/CITY_6800_NANITE_NATIVE_DIAGNOSIS.md PASS.
- Báo một lần tối đa 15 dòng: file, kiểm chứng, vấn đề còn mở.
