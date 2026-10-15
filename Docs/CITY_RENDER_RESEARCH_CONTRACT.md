# Hợp đồng rà soát render — 2026-10-08

- Mục tiêu: đối chiếu yêu cầu culling và giảm rays/samples với UE 5.8.3 hiện dùng.
- Root tra tài liệu chính thức, cập nhật CITY_EXECUTION_STATUS.md và commit/push.
- Agent chỉ đọc Config, Source, Tools/Editor, log runtime cần thiết và mã nguồn engine.
- Agent được tạo duy nhất Saved/QA/CityRenderConfigAudit.md; không sửa mã hoặc Content.
- Định dạng báo cáo: cơ chế; giá trị cấu hình; đường dẫn:dòng; giới hạn chứng cứ; bước tiếp theo.
- Phân biệt cấu hình tĩnh, mặc định engine và giá trị thật trong runtime.
- Tìm frustum/occlusion/HZB/Nanite; World Partition/HLOD; Lumen/VSM/TSR; texture streaming.
- Xác định có override rays/samples/path tracing hay không; tránh đoán mặc định 12/4096.
- Tự kiểm: dẫn chứng rg và đoạn nguồn ngắn cho mỗi kết luận; không chạy game hoặc benchmark.
- Không spawn agent, không sửa file khác, không commit; báo cáo một lần tối đa 15 dòng.
