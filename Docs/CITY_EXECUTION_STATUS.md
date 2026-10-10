# ANANTA — tiến độ hiện hành

Cập nhật 2026-10-10. Mục tiêu tổng thể đang thực hiện, chưa hoàn tất.
Mỗi vòng: sửa → kiểm chứng → cập nhật file này → commit/push GitHub.
Nguồn: nhánh codex/city-expansion; chi tiết: CITY_MOBILITY_ROUND.md.

## Yêu cầu đã chốt

- Yêu cầu mới: tăng từ 3,4 lên 6,8 × 6,8 km, gấp đôi mỗi chiều lần nữa; map mới đã lưu, chưa nghiệm thu.
- Model mới/sửa kiểm tám hướng; mỗi vị trí đặt kiểm năm góc trong scene thực.
- Biển mở ra chân trời, có ranh giới chặn người chơi; props nhỏ có thể giản lược hình học.
- Giữ model nhân vật và save cá nhân. Nhà không vào được chỉ có vỏ.
- Hướng trải nghiệm ANANTA/Neverness to Everness và chất lượng hình ảnh Endfield.
- Đa dạng nhà, nội thất, phố, công cộng/giải trí/biển/cảng và phương tiện.
- Rà kẹt/xuyên trên bản mới nhất; NPC lên/xuống và chạy tuyến chính cố định.
- Menu đồ họa, Việt/English, FPS bật/tắt; mục tiêu mới 90 FPS ở Max native 1080p.
- Chỉ thử gameplay ngắn, chạy ngầm/offscreen; không benchmark.

## Đã làm và kiểm chứng

### Thành phố

- Apply/readback map 6,8 km PASS: 10.754 nhà, 85.386 nhóm, 1.660.761 instance.
  EXE đã kiểm vẫn 3,4 km; chưa có EXE 6,8 km hoặc số FPS của map mới.
- Build mới PASS 78,62 giây; automation 23/23 state Success, hai bài có cảnh báo dọn fixture.
  Regression mái ga/tuyến khu vực/cap FPS tùy chỉnh đều Success; đọc đủ 86.180 actor PASS.
- Nguồn QA vòng này đã push 5ebc30bf499bdbab9ad4eabc4f094ad736a0f7bd, LFS fsck PASS và remote SHA khớp.
  Map 6,8 km chờ gameplay/ảnh/HLOD/EXE, chưa stage vào checkpoint nguồn.
- Rà body/đường 6,8 km PASS: 34.617 component, 154.964 instance chặn, 13.987 điểm đường, 49 vùng.
  Gate ranh giới PASS 14/14, exit 0; đủ bốn collider, capsule 38/92, không đổi hình học hoặc clamp tọa độ.
  FAIL trước do commandlet query lúc mesh còn compiling và physics state chưa tạo; đã chờ mesh/tree/body.
  Đây là nghiệm thu editor của map đã lưu; chặn rìa trong EXE vẫn cần kiểm riêng.
- Công cụ thử Max trong EXE đã thêm provenance package/cvar, giữ mọi frame và phục hồi hai slot QA.
  Chín test fixture dữ liệu PASS; chưa chạy gameplay hoặc xác nhận FPS bằng bộ công cụ này.
- Checkpoint f3cf22c010deea49d3671a22e26f73a752a6f15e đã push; LFS fsck PASS, remote SHA khớp.
  Gồm helper chờ mesh/physics, QA ranh giới, chuỗi gameplay và công cụ trial; không gồm map 6,8 km.
- Fixture tàu đầu FAIL ở mốc khứ hồi lấy giữa đường: mỗi tàu chạy 591 m, lên/xuống tám lượt, không blocker.
  Sửa lấy mốc tại điểm dừng thật và đếm lượt mới; build PASS 68,40 giây; fixture hai tàu PASS.
  Mỗi tàu lên hai/xuống hai lượt, đi 156,67 m, trở lại sai số 0,1 cm; tiếp tục mái/tuyến xe.
- Thuyền tại bến thật PASS E/W/Space/E: chèo 0,78 m, phanh dừng, xuống bến khô, từ chối xuống giữa biển.
  Capsule 38/92 giữ nguyên; không bypass collision/mặt đỡ/tốc độ trong đoạn đo; chưa kiểm chuyến biển dài.
- 3.534 nhà, 784 ô; bảy bộ mặt tiền, tám dạng khối, màu/chiều cao khác nhau.
- Map 3,4 km đọc lại theo lô: 25.026 nhóm, 602.965 instance; 19 đồ sinh hoạt và 16 đèn mới.
  Gồm năm nhóm civic mới; đã sửa báo cáo nền và cách đếm bỏ sót HISM mang nhãn Living.
- 12 dịch vụ: tám địa điểm cũ và điểm đọc thông tin cảnh sát/cứu hỏa/bar/arcade.
- Khu vui chơi, biển, bến tàu cùng bản đồ; bốn phòng công cộng có cửa rộng 480 cm.
- Nguồn bố cục không lấn đường, chồng nhà hay thiếu mesh tham chiếu.
- Nội thất mới: 11 loại, 73.844 tam giác; 19 vị trí đã nhập/ghi map.
- Vòng quay 40.068 tam giác, tám cabin đã thay 282 khối cũ; đã xem ảnh GPU trong Unreal.
- Đèn phòng công cộng giới hạn khoảng hiển thị; texture sân lát theo kích thước thế giới.
- Nước thêm gợn normal nhỏ, giữ nguyên mặt nước/va chạm.
- Ảnh civic đã xem: nhà cứu hỏa, bar, arcade, vòng quay, biển/cảng; cảnh còn thưa.
- Sửa nền lát/gỗ trùng mặt phẳng bằng tách cao độ 1 cm; ảnh GPU bar/arcade đã hết mảng loang.
- Đã xem lại tám ảnh GPU sau chuyển cube Nanite: mặt tiền, nền, cầu tàu và vòng quay vẫn hiện đúng.
  Nội thất bar/arcade còn thưa, sàn bóng mạnh; biển/cảng còn đơn giản, cần cải thiện tiếp.
- Các khu mới vẫn cần tinh chỉnh; chưa nghiệm thu là đồ họa cuối cùng.

### Va chạm và giao thông

- Sửa giới hạn lái xe, phép xoay, khoảng trống đầu khi xuống xe, mantle và capsule khôi phục.
- Sửa dò cửa xe nhận nhầm nóc vật cản là sàn; sửa xe dài bị khóa hướng lái ở góc rẽ.
- PASS: 17/17 automation, gồm regression capsule, mantle, góc rẽ, asset và tuyến.
- Regression tái hiện 57 tuyến đi bộ quá ngắn ở cuối vỉa hè; sửa điểm đến/đổi hướng trong cùng ô.
  Kiểm lại không còn tuyến dưới 2 m trong fixture 512 tổ hợp vị trí/seed.
  Gameplay Max đi qua đoạn từng bị chặn và hoàn tất tám dịch vụ sau bản sửa.
- PASS rà map sau thay vòng quay: 10.401 component, 47.809 instance chặn Pawn,
  3.992 điểm đường; không thiếu body/mặt đỡ trong phạm vi kiểm tra này.
- PASS cửa căn hộ/cà phê hai chiều: bốn đoạn CharacterMovement thật.
- PASS cửa cảnh sát/cứu hỏa/bar/arcade: tám lượt W/Shift vào/ra, bốn tương tác E.
  Fixture dời người chơi giữa địa điểm lúc chuẩn bị; không dời trong đoạn đo, không đổi va chạm/tốc độ.
- 11 phương tiện: khách/buýt/taxi/tải/chở hàng/bồn/cảnh sát/cứu thương,
  tàu hàng/cano/thuyền buồm; 197.536 tam giác tổng nguồn, có LOD.
- PASS 11/11 fixture: cửa bị chặn, lên xe, chờ vật cản, chạy ít nhất 49 m,
  xuống xe, dọn actor. Fixture không thay cho nghiệm thu mọi tuyến thật.
- Tối đa tám xe gần người chơi; nạp mesh lúc khởi tạo; chờ vật cản/đường chưa tải.
- NPC đi bộ tới cửa, ẩn trong cabin, hiện tại điểm xuống đã kiểm capsule.
  Chưa có animation mở cửa/ngồi ghế mới. Vòng quay là cảnh vật tĩnh.
- Xe khởi đầu chuyển sát lề; không sửa vị trí xe trong save cá nhân.
- PASS Coach trên tuyến thật: lên xe, qua góc rẽ, xuống ở bến tiếp; 3.315 lần kiểm tiếp đất.
- PASS tám tuyến đường bộ đầy đủ: 16 xe, khoảng 925 m/vòng, bốn phía và trở lại điểm đầu.
  Hai xe lệch điểm xuất phát mỗi loại kiểm đủ lên/xuống cả bốn bến; 140,86 giây.
  Fixture NullRHI nạp vùng đường thật, giữ tốc độ/geometry/collision; chưa thay cho kiểm xe trong EXE.
- PASS ba tuyến tàu trên hình học map thật: khoảng 219 m khứ hồi, lên/xuống và trở lại bến.
  Fixture NullRHI dời observer/nạp vùng cảng; không sửa tốc độ, cầu tàu, mặt đỡ hay collision.
  Người chơi đi tại cảng chưa nghiệm thu đầy đủ.

### Cài đặt và hiệu năng

- Menu: preset/10 nhóm chất lượng, render scale, cap FPS, VSync, ngôn ngữ, FPS.
- Esc/F10 mở cài đặt; Alt hiện chuột; F8 bật/tắt bộ đo frame thực.
- Apply/Hủy/mặc định/pause/Việt/English/reload đã qua QA và EXE preview cũ.
- PASS tải lại save QA sau hành trình tám dịch vụ trên bản 3,4 km mới.
- Có frustum/occlusion, Nanite HZB, World Partition, HISM, streaming, LOD, TSR.
- Hướng dẫn vật thể lặp: CITY_INSTANCING_GUIDE.md; Ctrl+D/Ctrl+V không tự bảo đảm instancing.
- Mesh kính translucent dùng LOD thường, tránh vật liệu mặc định do Nanite không hỗ trợ.
- Bản EXE đã đo dùng Epic (3), native 100%. Nguồn mới có Max tùy chỉnh giảm chi phí GI/bóng/TSR;
  giữ native 100%, ghi rõ đánh đổi chất lượng. Editor 3,4 km sau sửa: 50,34 FPS, p95 24,98 ms;
  14.206 frame/282,17 giây, giữ đủ 52 frame trên 33,3 ms và 10 trên 50 ms; chưa đạt 90 FPS.
  Lượt này dùng ReservedResources=0, chưa chứng minh EXE/reload hết PageFault.
- Max native 1080p bản 3,4 km sau sửa tuyến NPC: 62,57 FPS trung bình,
  p95 18,90 ms, GPU 15,26 ms; 17.621 frame trong 281,61 giây quan sát. Chưa đạt 90 FPS.
  Hoàn tất tám dịch vụ; giữ cả 22 frame trên 33,3 ms và sáu frame trên 50 ms trong số liệu.
- Số cũ 52,56 FPS thuộc map 1,7 km; không dùng làm so sánh trực tiếp với bản mới.
- D3D12 PageFault/Nanite/VSM khi khởi động chưa được kết luận đã sửa.
- Trước chuyển cube Nanite, Max lỗi PageFault; tắt NonNanite.Batch vẫn lỗi.
  Tắt VSM đã hoàn tất 282,62 giây/55,71 FPS, chỉ là chẩn đoán, không tính đạt Max.
  Hai lượt Max sau chuyển Nanite chưa crash; chưa chứng minh đã sửa triệt để.
- HLOD Instancing đầy đủ PASS 962/962; đọc lại 591.633 instance, không thiếu mesh/material.
- Bố trí bar/arcade thêm 54 instance trong 5 nhóm đã kiểm bounds/lối đi/chồng đồ;
  map, HLOD, tám lượt qua cửa/bốn dịch vụ và đủ tám ảnh GPU đã kiểm.
- EXE CityExpanded 3,4 km build/cook/package PASS; menu Apply PASS, reload bị GPU PageFault Nanite/VSM.
- EXE Max 1080p gốc: 47,71 FPS / p95 37,87 ms; 13.523 frame, 283,46 giây, GPU trung bình 20,12 ms.
  Giữ 1.760 frame trên 33,3 ms và 13 frame trên 50 ms. Chưa đạt 90 FPS; chưa kết luận lỗi GPU đã sửa.
- Map 6,8 km đã apply/readback/body/đường/ranh giới PASS; chưa nghiệm thu gameplay/ảnh.
  Chi tiết thuyền/tàu/bể bơi trên mái/props nhỏ: CITY_6800_INTEGRATION_ROUND.md.
- Đã chuyển 12.025 component / 113.907 instance khối đục sang Nanite;
  giữ geometry/material/collision; rà lại body và 3.992 điểm đường đạt.

## Tiếp tục

1. Thử người chơi đi tại cảng và kiểm các tương tác trong EXE mới.
2. Tiếp tục tối ưu render và tăng chi tiết nội thất/biển/cảng theo ảnh và số đo hiện tại.
3. Commit/push checkpoint HLOD/civic và số đo EXE; giữ rõ lỗi reload và FPS chưa đạt.
4. Áp dụng mở rộng 6,8 km, model mới, biển mở và ranh giới theo CITY_6800_CONTRACT.md.
5. Kiểm va chạm, tám hướng model/năm góc đặt, HLOD, EXE và gameplay; giữ các build cũ.
6. Tiếp tục chất lượng cảnh vật và ổn định 90 FPS; không coi build/test là nghiệm thu toàn game.

## Bằng chứng

- Saved/QA/CityAutomation/index.json; CityWholeMapCollision.txt; CityFleetCheck/Report.txt.
- Saved/QA/CityMobilityMapReadback.json; CityExpansionApplied.json; CityTransitCheck/Report.txt.
- Saved/QA/CityHarborCheck/Report.json: ba tuyến nước, 78,28 giây sau sẵn sàng.
- Saved/QA/CityCivicCheck/Report.json: tám lượt qua cửa, bốn dịch vụ, 51,26 giây.
- Saved/QA/CityRoadRoutesCheck/Report.json: tám tuyến, 16 xe, 140,86 giây.
- Saved/QA/CityMaxGraphics/Summary.json, FrameTimes.csv, RenderConfig.txt: lượt Max hoàn tất.
- Saved/QA/CityPedestrianRegressionBefore.json và After.json: tái hiện lỗi rồi kiểm lại đạt.
- Saved/QA/CityMobilityAssets, CityLivingAssets, CityFerrisAssets, CityCivic.
- Assets/City/*_manifest.json: nguồn, giấy phép, hash, tam giác, texture.
- Preview cũ: Saved/Builds/CitySettingsPreview/Windows/ANANTA.exe, vẫn là bản 1,7 km.
- Không đưa save cá nhân/log máy vào Git. Checkpoint b99f3956f đã push, remote SHA khớp;
  Git LFS fsck đạt, upload đủ 12.027 đối tượng / 108 MB.
