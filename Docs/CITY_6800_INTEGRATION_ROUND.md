# Vòng tích hợp thành phố 6,8 km

Cập nhật 2026-10-10. Đang thực hiện; bản đồ/EXE đã kiểm vẫn là 3,4 km.

## Nguồn đã làm

- Bố cục 6.788,23 m mỗi chiều: 10.754 nhà, 1.660.761 instance trước nội thất đặt riêng.
- Ba mặt biển mở ra đông/nam; bốn collider ranh giới; chín lối tiếp cận công trình.
- Ga hai ray/hai sân ga, sân bay/helipad/cao tốc/nhà máy/khách sạn/nhà hàng/nhà hát/rạp/café.
- Bể bơi trên mái nhà hai tầng, cầu thang ngoài và lan can; chưa có cơ chế bơi.
- Thuyền chèo chậm dùng E/WASD/Space; chỉ xuống khi có bến khô và đủ khoảng trống capsule.
  Một thuyền người chơi luôn nạp để không bị unload theo ô bến khi chèo xa; vẫn camera culling.
- Hai actor tàu con thoi chạy ngược chiều; tính khoảng dừng từ kích thước mesh thực.
- Tám vật dụng nhỏ dùng texture/vật liệu Living đã có, ba LOD và không chặn người đi.
- Đèn phố chỉ tìm ứng viên quanh người chơi; tái sử dụng tám đèn, hai đèn có bóng.
- Max thử nghiệm giảm mẫu bóng còn 4, giảm độ phân giải tính GI/reflection/history.
  Vẫn native 1080p/100%; đây là Max tùy chỉnh có đánh đổi chất lượng.
- Công cụ chụp năm góc chia thành metro/small/facilities; tàu đứng yên riêng khi chụp QA.

## Kiểm chứng hiện tại

- PASS Python compile và VerifyCity6800Layout.py: không có lỗi bounds/lối vào/biển trong nguồn.
- Build Editor tích hợp PASS, gồm QA tàu, input thuyền và kiểm va chạm theo vùng (78,25 giây).
- Ba regression thuyền PASS: tái hiện chui dưới bến với hull thấp, hull mới chặn;
  xuống tại bến khô/từ chối giữa biển; không vượt biên nước.
- Automation sau nhập model PASS 20/20 (19 thành công, một thành công có cảnh báo), không thất bại.
  Fleet.ImportedBounds đọc đủ mobility/metro manifest và bounds thực của 13 loại.
- Bản 3,4 km đã publish: 4a68808146aab8a11d44d561a35e8241dea6b5d5, LFS fsck đạt, remote SHA khớp.
- EXE 3,4 km: Max gốc 47,71 FPS trung bình, p95 37,87 ms; chưa đạt 90 FPS.
- Reload cài đặt EXE gặp D3D12 PageFault ở Nanite/VSM; chưa kết luận đã sửa.
- Editor 3,4 km, Max tùy chỉnh + Nanite ReservedResources=0: gameplay PASS 282,17 giây,
  14.206 frame, 50,34 FPS trung bình, p95 24,98 ms, 52 frame trên 33,3 ms và 10 trên 50 ms.
  Giữ tất cả frame; chưa đạt 90 FPS. Hai thử nghiệm trước vẫn PageFault.
- ReservedResources=0 được ghi vào nguồn sau lượt PASS; chưa có EXE mới hoặc reload xác nhận.
- Tám vật nhỏ đã xem 64 ảnh/tám hướng và kiểm geometry/hash; nhập engine PASS, bounds khớp, ba LOD.
- Kiểm mặt đỡ sửa bát/cốc/lọ hoa và khoảng cách nồi với lò vi sóng; ảnh đặt cảnh chưa chạy.
- Kiểm mặt đỡ nguồn PASS tám props và bắt ba vị trí nhô mép cũ; chuẩn bị 45 ảnh đặt gồm bồn rửa.
- Nạp/dỡ map theo lô 1.000 actor; lượt thử phát hiện lỗi so chuỗi GUID, đã sửa và đang kiểm lại.
- Collider ẩn bỏ đóng góp distance field/bóng; giữ nguyên hình học chặn người chơi.
- Năm model metro đã sửa UV/kính/khớp tàu/chân ghế, xem đủ 40 ảnh/tám hướng.
  Build/FBX/hash/render/delivery PASS; nhập Unreal PASS, bounds khớp, ba LOD và simple collision.
  50.912 tam giác tổng nguồn. Import còn cảnh báo bi-normal gần zero; cần xem ảnh Unreal.
- QA đi lên/xuống thang mái đã viết và build Editor PASS 61,20 giây; chưa nghiệm thu thực địa.
- Regression bắt landing che ba bậc 37–39, tạo bước cao 60 cm; đã dời landing sau bậc cuối.
  Kiểm lại cả 41 bậc và đường nối mái PASS trong nguồn, chưa thay cho CharacterMovement thực.
- Đã đồng bộ vùng cắt đường sân bay giữa Python, audit C++ và đèn phố.
- Git giữ nguyên byte hai thư mục nguồn model mới để hash provenance không đổi do xuống dòng.
- Đọc đủ 25.801 actor nền theo lô PASS: 25.026 nhóm, 602.965 instance, 12 dịch vụ.
  Sửa cách đếm bỏ sót năm HISM Living_CivicDressing; đối chiếu nguồn commit cũ cùng số instance.
  Báo cáo nền đã hòa giải thay vòng quay 282 thành một và cabinet bỏ 42/thêm 54; không sửa map.

## Các bước cần làm tiếp

1. Nhận đủ model, xem tám hướng thực; nhập FBX, đối chiếu bounds/material/LOD.
2. Apply map 6,8 km, đọc lại nội dung, rà toàn bộ body/đường/capsule và ranh giới.
3. Thử thuyền tại bến thật, hai tàu lên/xuống/khứ hồi, cầu thang lên mái.
4. Chụp/xem năm góc từng vị trí mới; sửa nổi/chìm/xuyên/lệch hoặc silhouette chưa hợp lý.
5. Rebuild toàn bộ HLOD, kiểm proxy, package EXE riêng City6800.
6. Gameplay ngắn native Max, giữ mọi frame; kiểm cài đặt/save/reload và lỗi GPU.
7. Ghi kết quả, commit/push, LFS fsck và đối chiếu remote SHA.

Model nguồn hoặc ảnh render xong không tự đồng nghĩa nghiệm thu gameplay/đẹp/90 FPS.
