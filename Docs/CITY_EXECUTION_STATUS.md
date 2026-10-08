# ANANTA — tiến độ hiện hành

Cập nhật: 2026-10-08. Mục tiêu tổng thể đang thực hiện, chưa hoàn tất.
Mỗi vòng: cập nhật file này, kiểm chứng thay đổi, commit/push GitHub.
Bằng chứng chi tiết: Saved/QA và Saved/Logs; lịch sử đầy đủ nằm trong Git.

## Yêu cầu hiện hành

- Thành phố liên tục khoảng 1,70 × 1,70 km, gấp đôi diện tích bản trước.
- Tăng kiến trúc/cảnh quan/địa điểm tương tác; giữ nguyên model nhân vật.
- Nhà không vào được chỉ có vỏ, ưu tiên đồ chi tiết cho nội thất tương tác.
- Hướng trải nghiệm thành phố ANANTA/Neverness to Everness, chất lượng hình ảnh kiểu Endfield.
- Menu đồ họa, tiếng Việt/English, thanh FPS bật/tắt và lưu được lựa chọn.
- Mục tiêu mới: khoảng 90 FPS ở mức tối đa trên máy hiện tại, thay mục tiêu 60 FPS trước đó.
- Tối đa là Epic (3), render scale 100%; không đổi nhãn High thành Max để đạt số FPS.
- Chỉ chơi thử ngắn vài phút, không benchmark; ưu tiên chạy ngầm/offscreen.

## Đã có và đã kiểm chứng

### Thành phố và gameplay

- 196 ô phố, 1.472 nhà nền, bảy kiểu kiến trúc, 281.266 instance trong cùng World Partition.
- Tám dịch vụ: cà phê, căn hộ, hiệu sách, phòng khám, chợ, phòng tranh, xưởng và giao thông.
- Nhiệm vụ/xe/save giữ nền tảng trước; giới hạn save/nav của bản mở rộng là ±860 m.
- Mở lại map độc lập, kiểm mesh/material/transform/collision và hướng mặt tiền đạt.
- 238.666 instance mặt tiền và tám cửa đã sửa lỗi đảo hướng FBX.
- Nội thất hoàn thiện gồm sofa/thảm/rèm, PBR sàn, quầy, tranh và ốp gỗ; ảnh GPU đã xem.
- Nguồn sàn Poly Haven CC0; sofa HOUSE có giấy phép/tác giả ghi trong manifest.

### Model chi tiết mới — đã nhập và áp dụng

- Bảng dụng cụ 7.456, thùng phụ tùng 3.096, tủ y tế 4.128, bảng giao thông 1.086 tam giác.
- Bốn mesh, mười material, sáu texture mới đã nhập; thay bốn cụm và bỏ 21 mảnh blockout.
- Đọc lại map: 190 đồ nội thất + 73 đồ quảng trường = 263; 16 đèn, tám dịch vụ; không lỗi.
- Kiểm nguồn bố trí 35.720 cặp bounds, giữ hành lang 440 cm.
- Ảnh ngày/chiều xanh 1080p đã xem các model mới, bảng chỉ dẫn dùng tọa độ thật của tám địa điểm.
- Góc xưởng còn tối; chất lượng toàn thành phố chưa được nhận là hoàn tất.
- Backup trước áp dụng: CityBeforeVenueFixtures_20261008_1628, 7.577 file / 569.310.444 byte.

### Kiểm tra thực tế gần nhất

- Build game và Editor đạt; 7/7 automation thành phố trước phần settings đạt.
- Tuyến tám dịch vụ sau model mới: 293,729 giây, 23 lần lưu, một tiếp tế; tải lại tiến trình khác đạt.
- Quan sát tuyến đó: 29.215 frame, trung bình 9,984 ms, p95 13,590 ms; 8 frame >33,3 ms.
- Đi bộ/chạy thật theo input qua khu mở rộng: 277,788 giây, 1,708 km, không teleport/tăng tốc.
- 30.866 kiểm tra tiếp đất đạt; bốn điểm streaming sẵn sàng; bốn ảnh cuối tuyến đã xem.
- Quan sát tuyến mở rộng: trung bình 8,935 ms, p95 11,446 ms; 10 frame >33,3 ms, 6 >50 ms.
- Khoảng frame lớn nhất 686,948 ms trùng lần chụp ảnh đầu; báo cáo giữ cả spike này.
- Các số trên thuộc cấu hình High/TSR khoảng 1600×900 xuất 1080p, không chứng minh Max ổn định 90 FPS.
- Save thường giữ nguyên checksum sau lượt tuyến mở rộng; kiểm tra settings dùng config/save QA riêng.

### Render đang có hiệu lực

- Frustum/occlusion queries bật; Nanite frustum/HZB bật; World Partition, HISM và texture streaming.
- Lumen phần mềm, VSM, TSR; High dùng pool texture 3.000 MB.
- High thực tế: directional 8 rays, local 4 rays, cùng 4 samples/ray; không có control 12/4096 samples.
- Không dùng SetActorHiddenInGame theo góc nhìn camera làm culling.
- Thử riêng sun 60.000 → 40.000 lux không cho cải thiện rõ ở góc đối chiếu; đã khôi phục 60.000.
- Đọc lại map độc lập xác nhận sun 60.000 lux; không nhận phép thử này là tăng FPS.

## Vòng đang thực hiện: menu và 90 FPS

- Đã viết settings backend, migration cấu hình cũ, kiểm tra giá trị và ba automation mới.
- Đã thêm menu Slate với preset/10 nhóm chất lượng, TSR scale, FPS cap, VSync, ngôn ngữ và FPS.
- Đã nối nút góc màn hình, Esc/F10 mở menu, Alt hiện chuột, F8 bật/tắt bộ đo frame thực.
- Đã dịch HUD/nhiệm vụ/tương tác; Apply/Hủy/bản nháp và pause được kiểm tra bằng QA riêng.
- PASS: Editor build, 11/11 automation, menu Apply/Hủy/pause/F8, tiếng Việt/English và reload.
- PASS: ảnh 1080p/720p và cuộn tới ngôn ngữ; input nút qua keyboard Slate, chưa thử chuột desktop.
- PASS: hai save và cấu hình thường giữ checksum; runner automation đã tách config QA.
- Tối đa/Epic native 1080p: 52,56 FPS trung bình; frame 19,02 ms, p95 23,46 ms.
- GPU 18,18 ms, render thread 18,94 ms; 52 frame >33,3 ms và 9 >50 ms trong 294,6 giây quan sát.
- Mục tiêu 90 FPS chưa đạt. Lỗi GPU PageFault khởi tạo Nanite/VSM được giữ log, đang chẩn đoán.
- Cvar Max đã xác nhận Epic 3, native 1080p, cap 90, pool 3000 MB, Nanite culling bật, hardware RT tắt.
- Chi tiết sử dụng và nghiệm thu: Docs/CITY_GRAPHICS_SETTINGS.md.

## Tồn đọng và thứ tự tiếp tục

1. PASS: build game 94,90 giây, Editor và 11 test; menu/ngôn ngữ/FPS/persistence đã kiểm chứng.
   Tiếp tục tối ưu GPU/render và kiểm tra chuột desktop khi nghiệm thu bản đóng gói.
2. Tối ưu phần GPU/render của Max/Epic native 1080p trên RTX 4060 Laptop 8 GB / RAM 16 GB.
   Chưa xác nhận ổn định 90 FPS; không che spike hay âm thầm hạ chất lượng để báo đạt.
3. Dựng đủ 288 HLOD, kiểm proxy và quay góc/chuyển ô. Hiện chưa có tiến trình HLOD chạy.
   Lượt cũ đã lưu 13 cụm, dừng có kiểm soát trong cụm 14 để nhập fixture trước lượt cuối.
   Cache đã lưu được giữ; không dừng/khởi động lại chỉ vì chờ lâu.
4. Mẫu HLOD X0_Y0 đạt PBR/emissive/normal; cảnh báo normal cũ X5_Y3 và toàn bộ proxy còn cần rà.
5. Cải thiện sáng xưởng, cửa sổ ngày, cây/cảnh quan còn đơn giản và mức lặp ngoài phố.
6. Đóng gói bản mở rộng rồi thử lại nhiệm vụ, xe, dịch vụ, save cũ và ảnh ngày/chiều xanh.
   EXE đóng gói hiện có vẫn thuộc thành phố nhỏ trước mở rộng; không dùng làm bằng chứng bản mới.
7. Commit/push checkpoint sau vòng này; remote đã xác nhận gần nhất: 528ac60 trên codex/city-expansion.

## Bằng chứng chính

- Model/layout: Assets/City/*_manifest.json; Saved/QA/CityDressingReadback.json.
- Dịch vụ: Saved/QA/CityServiceJourney/Report.txt và Reload.txt.
- Mở rộng: Saved/QA/CityStreamingJourney/Report.txt và bốn PNG.
- Fixtures: Saved/QA/CityFixtures, CityFixturesBlueHour; GPUReview.json.
- Ánh sáng: Saved/QA/CityDaylightReadback60000.json và hai thư mục ảnh 40000/60000.
- HLOD: Saved/QA/CityHLODPreFixtureStop.json; CityHLOD.BeforeFixtureImport.log.
- Proxy mẫu: Saved/QA/CityHLODProxy/ANANTA_City_City_L0_X0_Y0.
- Nghiên cứu: Docs/CITY_RENDER_OPTIMIZATION.md; Saved/QA/RenderResearchWeb/sources.json.
- Settings: Docs/CITY_SETTINGS_CONTRACT.md; Saved/QA/CitySettings; CitySettings*Build*.log.

Input QA qua PlayerController/Slate; bàn phím/chuột desktop thực chưa được xác nhận.
Build, test và ảnh có phạm vi riêng; chưa đủ bằng chứng nhận đồ họa cuối hoặc Max ổn định 90 FPS.
