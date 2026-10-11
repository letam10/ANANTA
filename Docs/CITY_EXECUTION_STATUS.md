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
  EXE 6,8 km đã build/cook/stage/archive PASS; Base native FAIL GPU.
  Diagnostic shadow async=1 hoàn tất một hành trình, 71,58 FPS; reload vẫn FAIL, chưa đạt 90 FPS.
- Build mới PASS 78,62 giây; automation 23/23 state Success, hai bài có cảnh báo dọn fixture.
  Regression mái ga/tuyến khu vực/cap FPS tùy chỉnh đều Success; đọc đủ 86.180 actor PASS.
- Nguồn QA vòng này đã push 5ebc30bf499bdbab9ad4eabc4f094ad736a0f7bd, LFS fsck PASS và remote SHA khớp.
  Map 6,8 km đã qua fixture vật lý/HLOD/package; ảnh/Player Max còn chờ, chưa stage vào checkpoint nguồn.
- Rà body/đường 6,8 km PASS: 34.617 component, 154.964 instance chặn, 13.987 điểm đường, 49 vùng.
  Gate ranh giới PASS 14/14, exit 0; đủ bốn collider, capsule 38/92, không đổi hình học hoặc clamp tọa độ.
  FAIL trước do commandlet query lúc mesh còn compiling và physics state chưa tạo; đã chờ mesh/tree/body.
  Đây là nghiệm thu editor của map đã lưu; chặn rìa trong EXE vẫn cần kiểm riêng.
- Công cụ thử Max trong EXE đã thêm provenance package/cvar, giữ mọi frame và phục hồi hai slot QA.
  Chín test fixture dữ liệu PASS; Base 6,8 km đã chạy nhưng lỗi GPU trước đo FPS.
- Checkpoint f3cf22c010deea49d3671a22e26f73a752a6f15e đã push; LFS fsck PASS, remote SHA khớp.
  Gồm helper chờ mesh/physics, QA ranh giới, chuỗi gameplay và công cụ trial; không gồm map 6,8 km.
- Fixture tàu đầu FAIL ở mốc khứ hồi lấy giữa đường: mỗi tàu chạy 591 m, lên/xuống tám lượt, không blocker.
  Sửa lấy mốc tại điểm dừng thật và đếm lượt mới; build PASS 68,40 giây; fixture hai tàu PASS.
  Mỗi tàu lên hai/xuống hai lượt, đi 156,67 m, trở lại sai số 0,1 cm.
- Thuyền tại bến thật PASS E/W/Space/E: chèo 0,78 m, phanh dừng, xuống bến khô, từ chối xuống giữa biển.
  Capsule 38/92 giữ nguyên; không bypass collision/mặt đỡ/tốc độ trong đoạn đo; chưa kiểm chuyến biển dài.
- Cầu thang mái PASS input W lên/xuống đủ 41 bậc, 2.600 mẫu floor/clearance, đứng mái và trở lại sân.
  Capsule/tốc độ giữ nguyên, không teleport trong đoạn đo, không lỗi; chưa kiểm bơi hoặc hình ảnh bể bơi.
- Chuỗi vật lý đạt 8/8, exit 0: Rail/Rowboat/RoofPool và Core/East/West/South/NorthEast.
  Mỗi vùng xe kiểm tám loại/hai xe mỗi loại, đủ vòng/bốn trạm; hoàn tất lúc 03:15:57 UTC.
  Đây là fixture vật lý trên map đã lưu; ảnh GPU, EXE và FPS vẫn chờ kiểm.
- Checkpoint rail 67e4229266d4f052f7cab4783b36da9b9269b17f đã push, remote SHA khớp.
- HLOD mới có gate identity/hash/log đầy đủ và đối chiếu actor/GUID; 27 fixture dữ liệu PASS.
  Cầu nối metadata C++ build PASS 60,38 giây, tám regression boundary-source PASS.
  API thực đọc 31 nguồn của một proxy PASS exit 0; chưa chứng minh độ phủ map mới.
  Checkpoint 7e539694f64afc305e1aa5b2a7851f18d270b172 đã push, remote SHA khớp.
  Full rebuild PASS 3.557 proxy, exit 0; run 9a4ba05837584d998162a3092dd72dba, hoàn tất 03:44:18 UTC.
  Readback PASS 3.557/3.557 actor/GUID, 1.619.348 instance; mesh/material đầy đủ, không lỗi.
  Kiểm 83.212 source mapping PASS, loại đủ bốn collider ẩn; chưa nghiệm thu ảnh hoặc FPS.
  Lỗi sắp thứ tự receipt PowerShell/Python đã sửa; sáu regression và receipt thật PASS, không rebuild lại.
  Lượt 30 ảnh đầu bị loại: regex QA ghi render scale 3%, dù PNG là 1080p; không nhận hình ảnh/FPS.
  Đã sửa thứ tự replacement và gate cvar thực 100%; bốn regression trên runner PASS.
  Evidence lỗi lưu CityPlacement_metro_Scale3Rejected; chụp lại native FAIL, các scope khác vẫn chờ.
  Chụp native lại FAIL exit 3 trước ảnh đầu: D3D12 PageFault/Nanite-VSM culling, ReservedResources=0 đã áp dụng.
  City6800 package PASS 698,86 giây, cook 5.382 package; EXE riêng ở Saved/Builds/City6800.
  Base packaged native FAIL exit 3, D3D12 PageFault lúc 04:13:03 UTC; chưa có frame/FPS hợp lệ.
  Cả Editor/Player đều lỗi native; đang thử riêng lịch async Nanite, chưa kết luận nguyên nhân.
  Global async=0 vẫn PageFault; riêng shadow async=1 hoàn tất EXE 281,76 giây, exit 0.
  20.167 frame, 71,58 FPS, p95 16 ms; giữ cả ba frame trên 33,3/50 ms; chưa đạt 90 FPS.
  Ba trial fingerprint cùng package, hai slot QA đều phục hồi; chỉ diagnostic, chưa đổi preset.
  Build QA capture PASS 49,99 giây; native shadow diagnostic chụp đủ 30 ảnh/6 contact, không crash.
  Đã xem đủ sáu contact: thuyền lộ nước ở sàn, một góc bị bến che; camera tàu bị mái ga che.
  Chưa nhận chất lượng cuối: xe/sân bay/biển vẫn đơn giản. Không coi đủ PNG là nghiệm thu đẹp.
  Sửa camera dưới mái ga và cao hơn bến; 15 ray mới không bị che, tái hiện hai góc cũ bị che.
  Model thuyền có sàn kín local Z=33 cm, cao hơn waterline 8 cm; 4.120 tris, ba material slots.
  Tám ảnh nguồn, UV/manifold/7.421 ray sàn/FBX/hash PASS; Unreal reimport PASS 4.120 tris/ba LOD.
  Wrapper lỗi đọc UTC PowerShell 7 đã sửa/bảy regression PASS; chạy lại PASS, chèo 79,08 cm.
  Native phát hiện ba slot material bị reimport giữ thứ tự cũ; sửa gán theo tên, sáu regression PASS.
  Unreal readback và năm ảnh thuyền mới PASS: sàn khô, vân gỗ đúng, bến/người chơi không che model.
  Hai tàu còn cột che một phần; props/công trình đã chụp và review, package thuyền mới còn chờ.
  Settings cùng package: Check PASS, Reload FAIL GPU exit 3; hai slot QA phục hồi đúng.
  DRED/TrackAllAllocations=1 hoàn tất 281,93 giây, 60,94 FPS; có overhead, không tính đạt Max.
  DRED không tái hiện fault nên chưa xác định resource gây lỗi; chưa đổi preset sản phẩm.
  Check-On/Reload-Off cùng package PASS một cặp, INI giữ nguyên hash, slot QA phục hồi.
  Đối chứng On/On mới FAIL ngay Check exit 3 ở frame 45; slot QA phục hồi, không coi shadow On là fix.
  Props nhỏ cũ capture PASS 45 ảnh/chín contact; một số góc bị lò/ấm/bình che.
  Native readback 85 nguồn/43 bounds PASS: tám props kê đúng, không chồng AABB, khớp nguồn.
  Nồi–ấm cách 2,9555 cm; không di chuyển actor hoặc làm HLOD mất hiệu lực.
  Camera mới qua bảy test, tái hiện ba góc cũ bị che; lượt DRED mới PASS 45 PNG/chín contact.
  Đã xem đủ năm góc/chín vị trí: nhận camera visibility; mỹ thuật cuối và toàn scope physics còn mở.
  Capture công trình shadow On FAIL GPU frame 811 trước ảnh đầu; không coi On là fix.
  Đã thêm DRED capture/gate CVar runtime, 11 regression PASS; build QA PASS 42,47 giây.
  RenderConfig xác nhận tracking=true, native 100%/1080p; DRED không dùng nhận performance Max.
  Lượt props DRED đầu có 45 ảnh nhưng bị gate từ chối do thiếu quan sát tracking; đã lưu riêng.
  Công trình DRED PASS 50 PNG/mười contact; đã review đủ, còn prototype, chưa nhận mỹ thuật cuối.
  Factory cần rà chi tiết bốc hàng lệch; Airport cần góc gần mặt đất, terminal hiện quá nhỏ trong ảnh.
  Checkpoint 27d3ec9db5ea1419dd00ba66127d01f0c4c56e1e đã push, remote SHA khớp và LFS fsck PASS.
  Chi tiết: CITY_6800_NATIVE_TRIAL_ROUND.md và CITY_6800_METRO_VISUAL_REVIEW.md.
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
  Rà log và gate EXE/reload: CITY_6800_GPU_RELOAD_DIAGNOSIS.md; runtime 6,8 km native đã FAIL.
- Trước chuyển cube Nanite, Max lỗi PageFault; tắt NonNanite.Batch vẫn lỗi.
  Tắt VSM đã hoàn tất 282,62 giây/55,71 FPS, chỉ là chẩn đoán, không tính đạt Max.
  Hai lượt Max sau chuyển Nanite chưa crash; chưa chứng minh đã sửa triệt để.
- HLOD Instancing bản 3,4 km PASS 962/962; đọc lại 591.633 instance, không thiếu mesh/material.
- Bố trí bar/arcade thêm 54 instance trong 5 nhóm đã kiểm bounds/lối đi/chồng đồ;
  map, HLOD, tám lượt qua cửa/bốn dịch vụ và đủ tám ảnh GPU đã kiểm.
- EXE CityExpanded 3,4 km build/cook/package PASS; menu Apply PASS, reload bị GPU PageFault Nanite/VSM.
- EXE Max 1080p gốc: 47,71 FPS / p95 37,87 ms; 13.523 frame, 283,46 giây, GPU trung bình 20,12 ms.
  Giữ 1.760 frame trên 33,3 ms và 13 frame trên 50 ms. Chưa đạt 90 FPS; chưa kết luận lỗi GPU đã sửa.
- Map 6,8 km đã apply/readback/body/đường/ranh giới, tám fixture vật lý/HLOD/package PASS.
  EXE Base/Reload FAIL GPU; ảnh metro diagnostic đã xem nhưng phát hiện lỗi sàn/camera cần sửa.
  Mục tiêu 90 FPS và rìa EXE chưa đạt; ảnh props/công trình đã review, mỹ thuật cuối còn mở.
  Chi tiết thuyền/tàu/bể bơi trên mái/props nhỏ: CITY_6800_INTEGRATION_ROUND.md.
- Đã chuyển 12.025 component / 113.907 instance khối đục sang Nanite;
  giữ geometry/material/collision; rà lại body và 3.992 điểm đường đạt.

## Tiếp tục

1. Rà Factory, chụp gần Airport, bổ sung facade/dressing; hoàn tất góc tàu còn bị cột che.
2. Khoanh vùng fault khởi động/reload từ cặp On/Off PASS và On/On Check FAIL; chưa đổi preset.
3. Dùng EXE City6800 đã package; thử gameplay ngắn, cài đặt/save/reload và rìa map.
4. Đo native Max giữ mọi frame; so trial cùng package, kiểm hình ảnh và lỗi GPU trước đổi preset.
5. Tiếp tục chất lượng nội thất/biển/cảng và mục tiêu 90 FPS; không suy ra từ cap hoặc build.
6. Mỗi vòng cập nhật tài liệu, commit/push; map mới qua gate rồi mới stage, LFS fsck và remote SHA.

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

## Vòng camera Airport 2026-10-10

- Tạo `Tools/QA/PrepareFacilityCloseViews.py` để lập năm góc nhìn thật cho terminal sân bay.
- Bốn góc dùng cao độ mắt 170 cm; góc upper nâng cao để giữ terminal và sân đỗ trong khung.
- Chạy `py_compile` và chạy generator hai lần; manifest có đúng 5 hướng, SHA256 lặp lại khớp
  `c0539755de45ed9ffa2a3c3ca5ab50092a01cf39e26749674abcd9d995dffe59`.
- Đây mới là kế hoạch camera, chưa tạo PNG, chưa di chuyển actor, chưa nhận mỹ thuật, collision,
  gameplay hoặc FPS. Capture Unreal gần mặt đất là bước kế tiếp sau khi source nhà máy hoàn tất.

## Vòng factory dressing 2026-10-10

- Sửa đúng hàm `factory()` trong `Tools/Editor/CityMetroDistrict.py`; giữ nguyên shell, `SITES`, `AIRPORT`
  và reserve footprint. Loading dock mới bám mặt phố `-Y`, không thay actor map đang lưu.
- Thêm apron 3.600 x 1.200 cm, bốn cọc bảo vệ, hai cửa cuốn, canopy và dải cảnh báo dùng Cube/material
  đã có; chi tiết trang trí đặt collision false để giữ chi phí instancing thấp.
- `py_compile` và layout source check phải đạt trước khi chạy Unreal. Chưa nhận ảnh native, collision,
  nội thất, gameplay NPC hoặc FPS; bước kế tiếp là Apply/readback và capture năm góc.

## Vòng model review và instancing 2026-10-11

- Thêm `Tools/QA/PrepareModelReviewViews.py`: đọc 11 manifest nội bộ, tạo 8 góc kiểm model và 5 góc kiểm placement cho mỗi model.
- Manifest nguồn hiện có 93 model, 744 góc model và 465 góc placement; output là `Saved/QA/CityModelReviewViews.json`.
- Thêm `Tools/QA/VerifyCityInstanceReuse.py`: kiểm theo chữ ký mesh/material/collision/hidden để phân biệt ISM/HISM thật với thao tác nhân bản editor.
- Self test instancing PASS; `CityMapBuild.json` chỉ có số tổng hợp nên report `CityInstanceReuse.json` là `PARTIAL` với 85.387 nhóm và 1.660.776 instance.
- `py_compile` và generator PASS. Không chạy Unreal, native capture, benchmark, soak test hoặc gameplay dài trong vòng này.
- Chưa nhận mỹ thuật, collision, HLOD, GPU hay 90 FPS từ manifest; bước tiếp theo là capture có mục tiêu sau khi map persistence/source control sạch.

## Vòng city diversity và interactive venues 2026-10-11

- Mở rộng `CityExpansionData.VENUES` từ 6 lên 10 venue: Library, Restaurant, Cinema và Hotel bổ sung bên cạnh Bookshop/Clinic/Market/Gallery/Workshop/Transit.
- `CityExpansionVenues.py` có dressing riêng cho bốn venue mới bằng mesh đã có trong manifest; không thêm asset ngoài hoặc chạm model nhân vật.
- `CityExpansionLandscape.py` thêm bốn kiểu pocket dressing và một phần playground dressing: quầy, shelter, bàn, ghế, planter, giá xe đạp, slide và swing; tất cả dùng instance tĩnh và collision nhỏ gọn.
- Source audit PASS: 10.750 building, 87.998 nhóm, 1.668.218 instance, 7 style facade, pendingAssetMeshes rỗng, errors rỗng.
- Gate 6,8 km PASS: width 6.788,225 m, area ratio 32, bốn boundary collider, ba mặt nước, chín access lane, không lỗi footprint.
- `py_compile`, `VerifyCityExpansionLayout.py` và `VerifyCity6800Layout.py` PASS. Không chạy Unreal Apply, native capture, benchmark hoặc gameplay dài trong vòng này.
- Map hiện chưa chứa source round mới vì ApplyCityExpansion sẽ xoá/ghi lại hàng chục nghìn actor; cần chạy riêng trong cửa sổ apply có log/marker và sau đó readback/HLOD.
- 60 FPS đồ họa cao vẫn là mục tiêu chưa nghiệm thu; source audit không chứng minh FPS, GPU stability, collision runtime hay visual acceptance.

## Vòng handoff và model quality source-only 2026-10-11

- Theo yêu cầu mới, đã dừng handle Unreal cũ `9031`; vòng này không mở Unreal, không chạy game,
  không kiểm tra cổng, không benchmark và không chạy soak test.
- Tạo `Docs/CITY_EXECUTION_HANDOFF.md`: kiểm kê source, generated `.uasset`, report, trạng thái Git,
  chênh lệch source/map, gate HLOD/GPU/visual/collision/Player/FPS và hành động an toàn cho chat sau.
- Tạo `Docs/CITY_HANDOFF_REVIEW_CONTRACT.md`: quy định tách source khỏi actor map, kiểm 8 hướng model,
  5 góc placement, instance reuse, nội thất shell-only và không suy ra FPS từ source audit.
- Cập nhật `CityExpansionBuildings.py`: bảy facade style có `STYLE_QUALITY` với accent material,
  cờ vertical/balcony và metadata quality; điểm nhấn dùng mesh/material hiện có để giữ instancing.
- Generator source-only đạt: 10.750 building, 89.078 group, 1.671.256 instance và đủ 7 style.
  Đây là số của generator sau source patch, chưa phải số map đã apply.
- Map/external actor dirty tree vẫn chưa stage. Report cũ còn `hlodRebuildRequired=true`,
  `runtimeVerified=false`, `physicalBoundaryCheckRequired=true`; không dùng làm nghiệm thu vòng này.
- Chưa thể xác nhận model thực tế, collision, HLOD, GPU hay 90 FPS vì người dùng yêu cầu không chạy
  Unreal/runtime; bước kế tiếp là native capture có kiểm soát sau khi user cho phép.

Handoff chi tiết: `Docs/CITY_EXECUTION_HANDOFF.md`.

## Vòng FacadeCivic và asset Blender headless 2026-10-11

- Thêm module `FacadeCivic` 4 x 3,2 m cho sảnh công cộng: cột đá, kính cao, mái che kim loại,
  bảng nhận diện và các thanh mullion; không chỉnh model nhân vật hoặc actor map.
- Blender 5.2 headless build PASS: 12 mesh, `FacadeCivic` 2.088 triangles, dưới ngân sách facade
  6.000 triangles; FBX roundtrip PASS 12/12, hash/bounds/material/UV/manifold đều đạt.
- Render review offline PASS 24 ảnh Cycles 24 samples, 2 góc cho 12 mesh. Hai ảnh FacadeCivic
  front/quarter đã xem; sảnh và mái che đọc rõ, chưa coi là nghiệm thu trong Unreal.
- Mở rộng style gate từ 7 lên 8 (`VerifyCityDistrictVariety.py`), thêm `FacadeCivic` vào phân bố
  west/core/east. Map/external actor chưa apply và không stage trong vòng này.
- Cảnh báo Blender chỉ liên quan đường dẫn brush mặc định; không có lỗi mesh hay exit failure.

## Còn tồn động sau vòng FacadeCivic

- Cần apply map có kiểm soát để style mới xuất hiện trong World Partition, rồi readback/HLOD riêng.
- Cần tiếp tục thay prototype identity cho Station/Hotel/Restaurant/Cinema/Pool/Factory/Airport
  bằng module facade/props tương ứng; source asset mới chưa chứng minh visual trong game.
- 60 FPS đồ họa cao, collision runtime, NPC/xe và GPU PageFault vẫn chưa được xác nhận trong vòng
  này vì chỉ chạy Blender/source audit, không mở Unreal hoặc packaged game.

## Vòng district variety và pocket dressing source-only 2026-10-11

- Bổ sung hồ sơ kiến trúc west/core/east trong CityExpansionBuildings.py.
  Mỗi building record hiện ghi district và dùng nhóm form riêng để giảm lặp hình khối.
- Generator vẫn giữ width 6.788,225 m và 10.750 building, nhưng phân bố được kiểm chứng:
  west 5.529, core 994, east 4.227; đủ 7 facade style và 8 form.
- CityExpansionLandscape.py tăng từ 4 lên 6 theme pocket.
  Hai theme mới là plaza đôi ghế/planter và market pocket; dùng mesh hiện có,
  collision nhỏ gọn và phù hợp instancing.
- Tạo Tools/QA/VerifyCityDistrictVariety.py làm gate source-only.
  Gate PASS; VerifyCityExpansionLayout.py PASS; py_compile PASS.
  Generator hiện ghi 89.097 group và 1.659.861 instance.
- Không mở Unreal, không apply map, không kiểm tra cổng, không chạy game,
  không benchmark và không đo FPS trong vòng này.
- Map/external actor dirty tree vẫn ngoài staging. Các số trên là source generator,
  chưa phải readback map. HLOD, collision runtime, visual acceptance và mục tiêu 60 FPS
  vẫn chưa được chứng minh.

Handoff tiếp tục: Docs/CITY_EXECUTION_HANDOFF.md.

## Vòng nội thất đa dạng 2026-10-11

- Đã hoàn thiện source dressing cho 12 loại không gian: Cafe, Apartment, Bookshop, Clinic, Market, Gallery, Workshop, Transit, Library, Restaurant, Cinema và Hotel.
- Bổ sung chi tiết riêng cho Library, Restaurant, Cinema và Hotel: kệ sách, đèn đọc, bản đồ/tranh, khung poster, quầy menu, cây cảnh, thảm dệt, sách và bảng trang trí. Các chi tiết nhỏ dùng lại mesh đã có để giảm số asset và phù hợp ISM/HISM.
- Sửa vị trí quầy vé Cafe về trục bố trí cố định để không phụ thuộc hướng mặt tiền của venue.
- Gate `python -X utf8 Tools/QA/VerifyCityVenueDressing.py` PASS: 249 additions, 12 phòng, 12 service desk, 166 vật thể non-collision, 72.816 so sánh bounds với nội thất nền, không overlap mới.
- Gate `python -X utf8 Tools/QA/VerifyCityModelViewCoverage.py` PASS: 94 model, 9 family, 8 hướng model và 5 góc placement; 20 mesh lặp lại, 223 reference có thể tái sử dụng.
- Đây là kiểm tra source-only; chưa chứng minh asset đã được Apply vào map, va chạm runtime, HLOD, ánh sáng, GPU hoặc FPS.

## Vòng sửa gate đồ nhỏ 2026-10-11

- Rà lại `small_manifest.json`, tám FBX và `SmallDetails.blend`; audit Blender headless PASS cho CookingPot, Saucepan, KitchenBowl, CoffeeMug, MakeupCompact, ToyBlocks, RoomVase và BathroomSoap.
- Bổ sung material references từ các placement source vào `VerifyCitySmallPlacement.py`. Gate trước đó fail vì dressing dùng `ShellSage` nhưng catalog fixture chỉ lấy material mặc định; đây là lỗi của gate, không phải lỗi mesh.
- Gate sau sửa: `CITY_SMALL_PLACEMENT_SOURCE_OK 8 regressions 3`; tám prop đều nằm trên surface hợp lệ, không overlap với obstacle hoặc nhau, và ba tọa độ sai bị regression test loại đúng.
- Không mở Unreal, không import asset vào map, không chạy EXE, không benchmark; visual native, collision runtime và persistence vẫn cần lượt riêng.

## Vòng civic dressing source-only 2026-10-11

- `CityCivicDressing.py` dùng sáu ArcadeCabinet mesh thật cho Pixel Pier, bố trí hai dãy theo tường; hai cabinet living hiện có được giữ lại, không để lại hộp cabinet procedural trùng hình.
- `VerifyCivicDressingLayout.py` PASS: 5 nhóm mesh, 54 instance, 43 collider, capsule radius 38 cm; containment, hành lang, overlap mới và overlap seating đều đạt.
- Bar giữ route vào rộng 480 cm, ba counter, ba bàn và sáu ghế; không thêm đèn động hoặc nội thất phía trên không cần thiết.
- Đây là source layout evidence; chưa chứng minh map persistence, import/reopen, collision trong Unreal, HLOD, ảnh native hoặc FPS.

## Vòng render audit và kế hoạch CVar 2026-10-11

- Đọc `Saved/QA/CityRenderConfigAudit.md` và `Saved/QA/CityRenderingNextSteps.md` theo phạm vi read-only; không mở Unreal, không benchmark và không đổi Config.
- Frustum/occlusion/HZB không bị tắt bởi project override được tìm thấy; World Partition/HLOD và Nanite đã có đường source, nhưng runtime residency/culling chưa được đo.
- Project đang dùng Lumen/VSM/TSR. Quality 2 dùng VSM SMRT directional 8 rays x 4 samples per ray và local 4 x 4; đây là shadow controls, không phải global path tracing samples.
- Không tìm thấy CVar project cho 12 rays hoặc 4096 samples. Không được đổi các con số đó theo suy đoán; thí nghiệm hợp lệ tiếp theo là HLOD rebuild comparison, VSM resolution bias diagnostic và VSM off crash isolation, mỗi nhánh phải ghi rõ chất lượng.
- Max native 1080p hiện có bằng chứng cũ khoảng 52,56 FPS; mục tiêu 60 FPS chưa đạt và mục tiêu 90 FPS vẫn chưa nghiệm thu.

## Vòng sửa gate 6,8 km FacadeCivic 2026-10-11

- `VerifyCity6800Layout.py` đã được đồng bộ với source facade hiện tại: yêu cầu 8 style và kiểm tra bắt buộc `FacadeCivic`, thay cho điều kiện cũ đúng 7 style.
- Gate sau sửa PASS: width 6.788,225 m, 10.750 building, 1.661.320 instance, 10 facility, 4 hidden boundary, 3 ocean surface, 9 access lane, pendingAssetMeshes rỗng.
- Đây là sửa phạm vi QA, không thay đổi geometry, map, actor tree hay model nhân vật. Các cờ `inEngineVerified`, `visualAccepted` và `gameplayFacilities` vẫn false.

## Vòng FacadeTransit và style facade thứ chín 2026-10-11

- Tạo module `FacadeTransit` cho sảnh ga/terminal: khung đá, kính phân ô, mái che nhôm, dải tuyến teal, cột nhận diện và đèn sign; dùng vật liệu đã có, không thêm texture mới.
- Blender 5.2 headless build PASS: 13 mesh, `FacadeTransit` 2.304 triangles, dưới ngân sách facade 6.000 tris; FBX roundtrip/hash PASS 13/13.
- Render review PASS 26 ảnh Cycles 24 samples cho 13 mesh. Đã xem `FacadeTransit_front.png` và `FacadeTransit_quarter.png`; silhouette, kính và canopy đọc rõ.
- Style distribution PASS với 9 style; `FacadeTransit` xuất hiện 1.800 building records. Model review coverage tiếp tục dùng 8 hướng model và 5 góc placement.
- Đây là source/Blender evidence; chưa Apply map, import Unreal, HLOD, collision runtime, NPC route hoặc FPS.

## Vòng station concourse FacadeTransit 2026-10-11

- Dùng lại `FacadeTransit` ở sân ga Station tại vị trí source `(x-3900,y-3900,15)`, xoay 90 độ; thêm `BusStopSign` collision false để tạo điểm nhận diện lối vào.
- Vị trí nằm trong reserve nhà ga và ngoài access lane rộng 300 cm; không thay ray, platform, gameplay anchor hoặc model nhân vật.
- `VerifyCity6800Layout.py` PASS sau thay đổi: width 6.788,225 m, 10.750 building, 1.667.839 instance, 4 boundary, 3 ocean, 9 access lane, pendingAssetMeshes rỗng.
- Đây là source placement evidence; chưa chứng minh actor map persistence, collision runtime, native visual, NPC boarding hoặc FPS.

## Vòng facility facade identity 2026-10-11

- Dùng lại asset facade đã kiểm định để cải thiện nhận diện facility: Hotel dùng `FacadeCivic`, Restaurant dùng `FacadeBrickArch`, Cafe dùng `FacadeBay`, Theater dùng `FacadeArtDeco`.
- Các điểm nhận diện đặt ở mặt đường với collision false, giữ shell, ray, platform, access lane và tầng trên shell-only; không thêm texture hoặc ánh sáng động.
- Gate `VerifyCity6800Layout.py` PASS: 10.750 building, 1.667.847 instance, 10 facility, 4 boundary, 3 ocean, 9 access lane, pendingAssetMeshes rỗng.
- Đây là source placement evidence; visual native, collision runtime, NPC traversal, HLOD persistence và FPS vẫn chưa nghiệm thu.

## Vòng airport terminal facade 2026-10-11

- Bổ sung hai `FacadeTransit` và hai `BusStopSign` trước hai khối terminal sân bay, dùng mesh đã import/hash PASS và collision false.
- Giữ nguyên runway, apron, heli pad, aircraft, access lane 1200 cm và ranh giới airport; không thêm nước hoặc mặt sàn collision mới.
- Gate `VerifyCity6800Layout.py` PASS: 10.750 building, 1.667.851 instance, 10 facility, 4 boundary, 3 ocean, 9 access lane, pendingAssetMeshes rỗng.
- Đây là source placement evidence; terminal native close view, map persistence, HLOD, collision, NPC/aircraft interaction và FPS vẫn chưa nghiệm thu.

## Vòng pool roof dressing 2026-10-11

- Bổ sung hai đèn, hai planter và một BusStopSign trên roof deck Pool bằng asset dùng lại, tất cả collision false.
- Giữ nguyên 41 bậc cầu thang, lan can, mặt nước DistrictWater không collision và đường tiếp cận mái.
- `VerifyCity6800Layout.py` PASS: 10.750 building, 1.667.856 instance, 10 facility, 4 boundary, 3 ocean, 9 access lane, pendingAssetMeshes rỗng.
- Đây là source dressing evidence; chưa có native pool capture mới, map persistence, HLOD/readback, collision runtime hoặc FPS acceptance.
## Checkpoint handoff: chẩn đoán EXE và bản đóng gói 2026-10-11

### Kết luận đã kiểm tra

- EXE vẫn tồn tại. Bootstrap của bản City nằm ở
  `Saved/Builds/City/Windows/ANANTA.exe` (171,520 bytes, ghi ngày 07/10/2026).
- Runtime chính nằm ở
  `Saved/Builds/City/Windows/ANANTA/Binaries/Win64/ANANTA.exe`
  (337,542,656 bytes, ghi ngày 07/10/2026).
- Ngoài ra còn bản City6800 và staged copy 338,096,640 bytes ghi ngày 10/10/2026;
  đây là các package khác nhau, không được coi là bản mới nhất của source.
- `Binaries/` và `Saved/` bị Git ignore nên EXE không xuất hiện trên GitHub. Lịch sử Git
  cũng không chứa `.exe` hoặc `.pak`; người nhận checkout phải dùng artifact local hoặc
  tự package lại.
- Commit source mới nhất `f7536deeee` ngày 11/10/2026 chưa được đóng gói vào các EXE
  hiện có. Vì vậy mở EXE cũ không thể hiện các facade/pool dressing mới nhất.
- Không mở game, không probe port, không benchmark và không tạo log runtime trong lượt
  chẩn đoán này. Không có bằng chứng để kết luận crash mới từ bản hiện tại.

### Nguyên nhân dễ gây lỗi hoặc tưởng như không có game

1. Chỉ sao chép `ANANTA.exe` ra ngoài sẽ thiếu thư mục `ANANTA`, `Engine`, Content/Paks
   và DLL đi kèm; bootstrap hoặc runtime sẽ không khởi động đúng.
2. Mở `Binaries/Win64/ANANTA.exe` của source root hoặc bản City6800 cũ sẽ chạy artifact
   khác với bản được mô tả trong handoff hiện tại.
3. Tài liệu `CITY_PLAYABLE_BUILD.md` đang trỏ tới bootstrap
   `Saved/Builds/City/Windows/ANANTA.exe`; phải giữ nguyên toàn bộ cây thư mục bên cạnh
   file đó.
4. Project config vẫn đặt GameDefaultMap là Slice, trong khi script package chọn
   `ANANTA_City`; package mới cần được build và kiểm tra map khởi động trước khi gọi là
   bản thành phố 6,8 km.

### Cách khôi phục có thể kiểm chứng ở lượt được phép package

- Chạy `Tools/Build/Package-City.ps1` với Unreal Engine 5.8 và output mặc định
  `Saved/Builds/City`; script dùng BuildCookRun Win64 Development, cook City, stage,
  pak và archive.
- Sau khi script trả `CITY_PACKAGE_OK`, kiểm tra cả bootstrap và inner EXE cùng các
  file Paks/Engine. Ghi timestamp, kích thước, SHA-256 và map startup vào handoff.
- Chỉ sau package mới được thực hiện một lần chạy ngắn có giới hạn để kiểm tra startup;
  lượt này chưa thực hiện theo yêu cầu không chạy game nặng/lâu.
## Vòng factory loading alignment 2026-10-11

### Đã làm

- `Tools/Editor/CityMetroDistrict.py` căn lại khu loading factory: apron 3.000 cm nằm trong
  shell, sát mặt trước và không che access lane; hai shutter flush tường và chạm cao độ apron.
- Bốn bollard được hạ từ 700 cm xuống 110 cm; dải vàng được dời khỏi AABB planter để tránh giao
  hình ảnh khi import.
- Tạo receipt `Docs/CITY_FACTORY_SOURCE_AUDIT.md` và giữ audit JSON source-only.

### Đã kiểm chứng

- `TestCityFactorySource.py`: 7/7 PASS.
- `VerifyCityFactorySource.py`: PASS, 96 instances, không issue.
- `VerifyCity6800Layout.py`: PASS, 10.750 building, width source 6.788 km, 9 access lane.
- `py_compile` và `git diff --check` PASS.

### Giới hạn còn mở

- Chưa apply map, chưa import/readback Unreal, chưa native five-angle capture, simple collision,
  NPC/xe loading, HLOD hoặc GPU/FPS. Các số liệu hiện là source evidence.
## Vòng airport close camera anchor 2026-10-11

### Đã làm

- Sửa generator camera dùng terminal thật tại `(186000,188000,20)`, không dùng site centre sân bay
  `(228000,204000)` cho close review.
- Thêm projection tám góc với FOV ngang 75 độ, aspect 16:9, positive depth và margin 0,92;
  năm hướng có identity `AirportTerminal` và eye height ground 170 cm.
- Thêm `Tools/QA/TestFacilityCloseViews.py` để bắt hồi quy anchor, hướng, frame, input và
  determinism; cập nhật `Docs/CITY_AIRPORT_CLOSE_CAMERA_ROUND.md`.

### Đã kiểm chứng

- 7/7 airport unit tests PASS.
- `py_compile` generator/test PASS.
- Manifest `Saved/QA/CityAirportCloseViews.json` tạo đủ 5 view, `accepted=false`.

### Giới hạn còn mở

- Chưa mở Unreal, chưa capture PNG, chưa kiểm tỷ lệ native, vật cản, collision, HLOD, NPC route,
  GPU hoặc FPS. Đây chỉ là camera/source evidence.
## Vòng station concourse dressing 2026-10-11

### Đã làm

- `Tools/Editor/CityMetroDistrict.py` thêm sảnh `FacadeTransit` đối xứng phía đông nam của ga,
  hai biển lối vào, bốn đèn sân ga, bốn ghế, hai route display và hai biển platform.
- Các asset đặt trên hai platform ở cao độ 100 cm; ghế giữ collision, các đèn/biển/display tắt
  collision. Access lane phía tây, ray và platform bounds không bị thay đổi.

### Đã kiểm chứng

- `VerifyCity6800Layout.py`: PASS, 10.750 building, 1.667.868 instance, 9 access lane,
  4 hidden boundary, 3 ocean surface, không pending mesh.
- `VerifyCityExpansionLayout.py`: PASS, 90.368 group, 1.667.868 instance, 9 facade style.
- `VerifyCityInstanceReuse.py`: PASS, 143 signature, 1.667.725 instance dùng lại.
- `VerifyCityDistrictVariety.py` và `VerifyCityRoofPool.py`: PASS.
- `py_compile` và `git diff --check` sẽ chạy trước commit.

### Giới hạn còn mở

- Chưa apply World Partition, chưa native five angle capture station, chưa kiểm collision runtime,
  NPC boarding, HLOD, GPU hoặc FPS. Đây là source placement evidence.
## Vòng factory industrial facade 2026-10-11

### Đã làm

- Thêm `FacadeIndustrial` ở mặt trước lệch phải của factory để tạo nhận diện công nghiệp mà không
  che access lane trung tâm.
- Thêm hai `DetailedStreetLamp` và một `BusStopSign` collision false ở sân loading; giữ nguyên
  apron, shutter, bollard và đường xe tải đã sửa ở vòng trước.

### Đã kiểm chứng

- `VerifyCityFactorySource.py`: PASS, 100 instances, không issue.
- `TestCityFactorySource.py`: 7/7 PASS.
- `VerifyCity6800Layout.py`: PASS, 10.750 building, 1.667.872 instance, 9 access lane.
- `VerifyCityExpansionLayout.py`: PASS, 90.370 group, không pending mesh.
- `VerifyCityInstanceReuse.py`: PASS, 144 signature, 1.667.728 instance dùng lại.
- `VerifyCityDistrictVariety.py`, `VerifyCityRoofPool.py`, `py_compile`: PASS.

### Giới hạn còn mở

- Chưa apply map, chưa native capture factory, chưa kiểm collision runtime, NPC/xe loading, HLOD,
  GPU hoặc FPS. Source gate không thay thế nghiệm thu Unreal.
## Vòng highway roadside dressing 2026-10-11

### Đã làm

- Bổ sung 56 `RoadBarrier` và 56 `DetailedStreetLamp` collision false dọc vai highway mỗi
  24.000 cm, giữ nguyên lòng đường, vỉa hè và reserve.
- Bổ sung 14 `TrafficSignal` collision false tại bảy nút lớn để highway có nhận diện giao thông
  rõ hơn mà không thêm collider hoặc logic xe mới.

### Đã kiểm chứng

- `VerifyCity6800Layout.py`: PASS, 10.750 building, 1.667.998 instance, 9 access lane,
  4 hidden boundary, 3 ocean surface và không pending mesh.
- `VerifyCityExpansionLayout.py`: PASS, 90.433 group, width source 6.788 km.
- `VerifyCityInstanceReuse.py`: PASS, 145 signature, 1.667.853 instance dùng lại.
- `VerifyCityDistrictVariety.py`, `VerifyCityRoofPool.py` và `py_compile`: PASS.

### Giới hạn còn mở

- Chưa apply World Partition, chưa native highway capture, chưa kiểm collision runtime, NPC/xe,
  HLOD, GPU hoặc FPS. Highway visual acceptance vẫn chưa được nghiệm thu trong Unreal.
## Vòng cinema commercial facade 2026-10-11

### Đã làm

- Bổ sung một `FacadeCommercial` ở mặt tiền rạp chiếu phim, lệch khỏi lối vào trung tâm để tạo
  khối nhận diện thương mại rõ hơn mà không chặn access lane.
- Bổ sung hai `DetailedPlanter` đối xứng phía trước và một `BusStopSign` ở mép tiếp cận; các
  prop này để collision false, giữ lối đi và vùng tương tác sạch.

### Đã kiểm chứng

- `VerifyCity6800Layout.py`: PASS, 10.750 building, 1.668.002 instance, 9 access lane,
  4 hidden boundary, 3 ocean surface và không pending mesh.
- `VerifyCityExpansionLayout.py`: PASS, nguồn rộng 6,788 km, tỉ lệ diện tích 4x.
- `VerifyCityInstanceReuse.py`: PASS, 90.436 group, 146 signature, 1.667.856 reusable instance.
- `VerifyCityDistrictVariety.py`, `VerifyCityRoofPool.py`, `py_compile` và `git diff --check`:
  PASS.

### Giới hạn còn mở

- Chưa apply map hoặc readback Unreal, chưa native capture, chưa kiểm collision runtime, NPC/xe,
  HLOD, GPU hoặc FPS. Đây là source placement evidence; visual acceptance trong game chưa được
  xác nhận.

## Vòng theater frontage 2026-10-11

### Đã làm

- Bổ sung hai dải marquee neon collision false ở mặt tiền Theater, dùng lại primitive đã có.
- Bổ sung hai `DetailedPlanter`, hai `DetailedStreetLamp`, hai `Bench` collision true và một
  `BusStopSign` ở hai bên mặt tiền; lối vào trung tâm rộng 600 cm được giữ nguyên.
- Không đụng model nhân vật, gameplay actor, map generated hoặc ExternalActors.

### Đã kiểm chứng

- `CityExpansionLayout.py`: PASS, 10.750 building, 90.440 group, 1.668.011 instance,
  source width 6,788 km và 9 facade style.
- `VerifyCity6800Layout.py`: PASS, 10 facility, 4 hidden boundary, 3 ocean surface, 9 access
  lane, không pending asset mesh; `inEngineVerified=false`, `visualAccepted=false`.
- `VerifyCityInstanceReuse.py`: PASS, 146 signature và 1.667.865 reusable instance.
- `VerifyCityDistrictVariety.py`, `VerifyCityRoofPool.py`, `py_compile` và `git diff --check`:
  PASS.

### Lỗi và bug còn mở

- Chưa chứng minh kẹt/xuyên, collider của props, NPC boarding hoặc tuyến xe trong runtime Unreal.
- Chưa có native eight direction model capture và five angle placement capture cho Theater.
- Chưa chứng minh HLOD, occlusion, shader sample, shadow ray, GPU frame time hoặc 60 FPS.
- Các venue hiện vẫn khai báo `shellOnly=true` và `gameplay=false`; tương tác nhà còn thiếu.

### Kế hoạch tiếp theo

- Rà source bounds và đặt thêm props cho civic/coastal/public-playground theo cùng quy tắc lane.
- Tách nhóm nhà có thể vào được khỏi shell-only, sau đó viết gate collision/NPC ngắn trước khi
  apply map.
- Chỉ chạy kiểm tra source và gameplay ngắn có giới hạn; không benchmark hoặc soak test.

## Vòng accessible ToyShop 2026-10-11

### Đã làm

- Thêm venue tương tác `ToyShop` tại `(-102000, 2600)` với footprint 1800x1500 cm, service
  `ToyShop_Supplies` dùng cơ chế `CityServiceInteractable` hiện có.
- Thêm kệ hàng, quầy checkout, `ToyBlocks`, bàn chơi, ghế và cây nhỏ; đồ chơi lặp lại dùng cùng
  mesh để giữ reuse và các item trang trí đặt collision false.
- Thêm wall details cho ToyShop và mở rộng coverage requirement để kiểm tra đồ chơi cùng quầy.

### Đã kiểm chứng

- `VerifyCityExpansionLayout.py` và `VerifyCity6800Layout.py`: PASS; layout giữ 10.750 building,
  9 style, width source 6,788 km, 4 hidden boundary, 3 ocean surface, 9 access lane và không
  pending asset mesh.
- `VerifyCityInstanceReuse.py`: PASS, 90.440 group, 1.668.011 instance, 146 signature và
  1.667.865 reusable instance.
- `VerifyCityModelViewCoverage.py`: PASS, 95 model, 11 manifest, 8 model views, 5 placement
  views, 13 phòng, 271 dressing item, sparse limit 273, 21 mesh lặp và 244 reusable references.
- `VerifyCityDistrictVariety.py`, `VerifyCityRoofPool.py`, `py_compile` và `git diff --check`:
  PASS.

### Lỗi và giới hạn còn mở

- Đây là source evidence; chưa apply/readback Unreal, chưa mở EXE, chưa capture native, chưa
  chứng minh collision runtime, NPC traversal, HLOD, GPU hoặc 60 FPS.
- Các cờ `inEngineVerified`, `visualAccepted` và `gameplayFacilities` vẫn false; service actor
  mới chưa được nghiệm thu trong gameplay.
- Quy tắc sparse interior hiện tính `max(250, số phòng x 21)` để số lượng tăng theo venue nhưng
  vẫn giữ trung bình tối đa 21 item mỗi phòng.
