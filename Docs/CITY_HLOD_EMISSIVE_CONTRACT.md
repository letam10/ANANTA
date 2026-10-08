# Sửa bake emissive HLOD — bằng chứng 2026-10-08

- Root đã dựng đúng một proxy City_HLOD/ANANTA_City_City_L0_X5_Y3.
- Saved/Logs/CityHLODSample.log xác nhận build/save, bốn texture 1024 và đúng material mới.
- Saved/QA/CityHLODProxy/Readback.json đọc lại đúng M_City_HLOD và texture binding.
- T_ANANTA_City_City_L0_X5_Y3_EmissiveColor.png có RGB bằng 0 ở mọi pixel.
- Phải xác nhận cụm có nguồn cửa sổ emissive trước khi coi texture đen là lỗi bake.
- Không chấp nhận thay texture đen bằng hằng sáng hoặc bật sáng toàn bộ bề mặt.
- Runtime phải giữ NightAmount; ban ngày cửa sổ không tự phát sáng, ban đêm giữ mẫu cửa sổ.
- Agent được sửa CreateCityWindowLighting.py, CityHLODMaterial.py, CreateCityHLOD.py,
  VerifyCityHLODPBR.py và tạo helper Tools/Editor/CityHLODEmissive*.py nếu cần.
- Root giữ Build-CityHLOD.ps1, VerifyCityHLODProxy.py, Content và mọi tiến trình Unreal.
- Agent đọc mã engine/báo cáo/ảnh nguồn để xác định nguyên nhân; không chạy UE hoặc sửa Content.
- Nếu cần giá trị MPC tạm khi bake, đề xuất giao diện rõ ràng; mặc định lưu phải trở lại NightAmount=0.
- Chỉ sửa dựa trên nguyên nhân có chứng cứ; kiểm Python AST và giao diện engine local.
- Báo cáo một lần tối đa 15 dòng: nguyên nhân, sửa gì, tự kiểm, lệnh root cần chạy và rủi ro còn lại.
- Không spawn agent, không benchmark, không commit, không sửa file ngoài phạm vi.

Kết quả rà nguồn: X5_Y3 có 17 gói nguồn nhưng không có cửa sổ; emissive đen hợp lệ.
Mẫu tiếp theo X0_Y0 có 13 nguồn chứa cửa sổ; phải SetupHLODs lại vì có tham chiếu nguồn cũ.
Translator mới của engine bỏ qua nhánh MaterialProxyReplace; mặc định hiện tắt.
VerifyCityHLODPBR bổ sung kiểm tra tương thích translator trước khi nhận cấu hình bake.

Root đã SetupHLODs và dựng X0_Y0 thành công; đọc lại 118.590 tam giác và bốn texture 1024.
VerifyCityHLODProxyPixels --require-emissive đạt: texture cửa sổ có pixel sáng và biến thiên.
Không thay shader nguồn để xử lý texture đen của X5_Y3; đó là mẫu không có cửa sổ.
Bằng chứng: Saved/QA/CityHLODProxy/ANANTA_City_City_L0_X0_Y0 và CityHLODSample.log.
Toàn bộ proxy và chuyển tiếp ánh sáng/streaming trong bản đóng gói vẫn cần kiểm tra.
