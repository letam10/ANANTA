# Vòng thành phố, va chạm và phương tiện

Cập nhật 2026-10-08. Yêu cầu mới đã xác nhận: 3,4 × 3,4 km, bốn lần diện tích bản 1,7 km.
Nguồn hiện tại: nhánh codex/city-expansion. Giữ model nhân vật và save thường.

## Tiêu chí và thứ tự

1. Rà kẹt/xuyên: capsule, mantle, xe, điểm lên/xuống, va chạm đồ trang trí và streaming.
   Sửa nguyên nhân tái hiện được; regression + tuyến chơi thử ngắn, không benchmark.
2. Xe khách/buýt/taxi/xe tải/xe chở hàng/xe bồn/cảnh sát/cứu thương.
   Tàu hàng/cano/thuyền buồm chạy ở vùng nước; NPC có lên/xuống thật tại điểm dừng.
3. Đường chính cố định; giới hạn số NPC/xe hoạt động gần người chơi, chờ vật cản.
4. Thành phố liên tục 3,4 km; giữ địa điểm/nhiệm vụ cũ; phân khu và dáng nhà đa dạng.
5. Nâng bồn cây/đèn/vỉa hè/bảng/đèn giao thông/lan can/tượng đài.
6. Khu vui chơi, bar, giải trí, cảnh sát, cứu hỏa, bãi biển, bãi tàu.
7. Nội thất: đèn/quạt/đồ sinh hoạt có texture; nhà không vào được chỉ có vỏ.
8. Kiểm tra ảnh, va chạm, NPC, save, Max FPS và đóng gói; cập nhật trạng thái và push.

## Đã xác nhận trước vòng này

- Menu đồ họa/ngôn ngữ/FPS đã có; 11 automation đạt; EXE preview menu/reload đạt.
- Max native 1080p trên RTX 4060 Laptop: 52,56 FPS trung bình ở Editor -game.
- EXE Max còn lỗi khởi động D3D12 PageFault; chưa đạt ổn định 90 FPS.
- HLOD mới có phần cache; toàn bộ proxy chưa hoàn thành, không có lượt HLOD đang chạy.

## Đang thực hiện

- Điều tra/sửa va chạm và tạo regression độc lập.
- Tạo bộ 11 phương tiện và 6 props mới có geometry/UV/PBR/LOD/provenance.
- Runtime tuyến NPC, điểm dừng/lên/xuống; mở rộng layout và phân khu.

## Chưa được nghiệm thu

- Toàn bộ nội dung yêu cầu mới; chưa gọi là hoàn tất chỉ từ source/build.
- Mốc 90 FPS ở Max; cần ngân sách 11,11 ms/frame và kiểm tra spike/hình ảnh.
- Va chạm toàn map, tất cả vòng lên/xuống, bến nước, texture/model cuối và HLOD đầy đủ.

Hợp đồng phân việc/API: CITY_MOBILITY_EXPANSION_CONTRACT.md.
Bằng chứng sẽ lưu dưới Saved/QA; không đưa save cá nhân hoặc log chứa đường dẫn máy lên Git.
