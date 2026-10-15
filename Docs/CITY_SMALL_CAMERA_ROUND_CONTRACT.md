# Hợp đồng sửa camera props nhỏ, 2026-10-10

- Repo D:\GAME\ANANTA, UE 5.8.3; không chạy thêm engine hoặc sửa map từ subagent.
- Root phụ trách native readback, vị trí model, apply map, chụp ảnh, Docs tổng và Git.
- Subagent chỉ được sửa/tạo `Tools/QA/CitySmallPlacementCameras.py`,
  `Tools/QA/TestCitySmallPlacementCameras.py`, `Docs/CITY_SMALL_CAMERA_REPAIR.md`.
- API: `cameras(name, location, size, yaw)` trả đúng năm dict có `id`, `direction`,
  `location=[x,y,z]`, `rotation=[pitch,yaw,0]`. Đơn vị cm và độ, đủ front/rear/left/right/upper.
- Root sẽ tích hợp API cho scope small. Không sửa PrepareCityPlacementViews.py.
- Dùng snapshot native `Saved/QA/CitySmallNativeBounds.json` khi file xuất hiện; nếu chưa có,
  có thể đọc source, manifest và ảnh cũ trước. Không suy đoán ảnh là proof geometry.
- Các vị trí và bounds nguồn: CitySmallDetails.describe(), small_manifest.json/living_manifest.json.
- Review cũ: Docs/CITY_6800_SMALL_VISUAL_REVIEW.md. CookingPot rear bị microwave che;
  MakeupCompact left bị đèn che; saucepan rear bị ấm che một phần.
- Không di chuyển/hide actor để chụp đẹp, không sửa character, chất lượng hoặc cvar.
- Chỉ sửa khoảng cách/độ cao mục tiêu camera của prop nhỏ khi có lý do geometric.
- Regression phải tái hiện ray bị chắn của camera cũ từ actual native bounds và kiểm
  năm ray mới cho model liên quan. Source AABB là conservative geometry, chưa đủ proof hình ảnh.
- Các snapshot Saved dùng làm QA fixtures đọc riêng; test không được phụ thuộc file Saved
  để chạy ở checkout khác. Lưu số đo tối thiểu được dùng vào test với provenance.
- Self-check: python Tools/QA/TestCitySmallPlacementCameras.py và py_compile module/test,
  git diff --check; mỗi file dưới 300 dòng, dòng khoảng 120 ký tự.
- Không commit/push, không subagent, không benchmark, không compile/launch Unreal hoặc Blender.
- Khi xong báo một lần tối đa 15 dòng: files, checks và các vấn đề còn mở.
