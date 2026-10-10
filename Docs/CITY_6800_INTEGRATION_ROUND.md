# Vòng tích hợp thành phố 6,8 km

Cập nhật 2026-10-10. Map 6,8 km đã lưu; EXE đã kiểm vẫn là 3,4 km.

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
- Rà source bắt tuyến xe chỉ quanh trung tâm; thêm vòng cố định tại tám khu, chọn điểm dừng gần nhất.
  Giữ cap tám xe, tuyến cảng/ga và tránh vùng cắt biển/sân bay; regression mới PASS, thực địa còn chờ.
- Sửa menu FPS bỏ sót cap hợp lệ đang lưu như 200/200,5; giữ giá trị chính xác, thêm regression lựa chọn.
  Không suy ra FPS thực từ cap; regression giữ cap tùy chỉnh đã PASS trong automation.
- Max thử nghiệm giảm mẫu bóng còn 4, giảm độ phân giải tính GI/reflection/history.
  Vẫn native 1080p/100%; đây là Max tùy chỉnh có đánh đổi chất lượng.
- Công cụ chụp năm góc chia thành metro/small/facilities; tàu đứng yên riêng khi chụp QA.
- Ảnh đặt cảnh dùng Max tùy chỉnh, native 1080p/100% trong file cài đặt QA riêng.
- Mỗi vị trí có bảng đủ năm ảnh thật và giữ bản gốc; index vẫn visualAccepted=false trước khi xem.

## Kiểm chứng hiện tại

- PASS Python compile và VerifyCity6800Layout.py: không có lỗi bounds/lối vào/biển trong nguồn.
- Build Editor tích hợp PASS, gồm QA tàu, input thuyền và kiểm va chạm theo vùng (78,25 giây).
- Ba regression thuyền PASS: tái hiện chui dưới bến với hull thấp, hull mới chặn;
  xuống tại bến khô/từ chối giữa biển; không vượt biên nước.
- Automation sau nhập model PASS 20/20 (19 thành công, một thành công có cảnh báo), không thất bại.
  Fleet.ImportedBounds đọc đủ mobility/metro manifest và bounds thực của 13 loại.
- Build mới toàn bộ QA khu vực/mái ga/cap FPS PASS 78,62 giây; build lại không đổi C++ PASS 2,64 giây.
- Automation mới PASS 23/23: 21 thành công, hai thành công có cảnh báo, không thất bại/bỏ qua.
  Ba bài BoardingUnderStationCanopy, RegionalRoadCoverage và CustomFrameRateChoice đều Success.
  Cả 23 state là Success; hai bài có tổng ba cảnh báo World has no context khi dọn fixture riêng.
  Unit runner dùng map Entry, tắt auto-navigation riêng process và yêu cầu report mới theo timestamp.
  Lượt khởi tạo map đầy đủ trước đó được dừng riêng, ghi StartupCancelled; không tính test case FAIL.
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
- Checkpoint nguồn/model d7281b30ba04755e475348e0bac14e16b957e9fc đã push, remote SHA khớp;
  Git LFS fsck PASS, upload 31/31 object mới. Map lưu tại checkpoint vẫn 3,4 km.
- Apply 6,8 km PASS exit 0: 85.386 nhóm, 1.660.761 instance, 10.754 nhà, 87.142 actor.
  Commandlet mất 3.541,71 giây, peak RAM 4.290 MB; lưu xong lúc 00:47:52 UTC ngày 10/10.
  Readback/body/đường/ranh giới và chuỗi tám fixture vật lý đã PASS; ảnh GPU/EXE vẫn chờ.
- Đã sửa ray lên/xuống tàu bắt sàn bên dưới mái ga, kèm regression hai sân ga và vật cản cửa.
  Build/regression và gate hai tàu tại ga trong map mới đã PASS.
- Đã chạy 14 sweep capsule 38/92 qua rìa/góc/biển; lượt đầu FAIL 14/14 do mesh còn compiling.
  Chẩn đoán xác nhận physicsBefore=0, bounds=0; sau hoàn tất mesh/tree/body physicsAfter=1 và PASS 14/14.
  Gate chính chạy độc lập PASS exit 0, nạp đúng bốn collider; không đổi geometry hoặc clamp tọa độ.
  Đây là editor persisted-map acceptance; chưa chứng minh gameplay tại rìa trong EXE.
- Test-City6800Round.ps1 nối 13 gate tuần tự sau exit 0 của apply; lỗi bất kỳ sẽ dừng và lưu stage.
  Chuỗi này chưa gồm ảnh GPU, HLOD, EXE, reload hoặc FPS; các gate đó vẫn phải chạy riêng.
- Checkpoint QA tiếp theo chỉ gồm mã/tài liệu; map apply dở không được stage cùng.
  Driver đầu PASS Build/Automation/Readback/Collision, dừng tại Boundaries FAIL; lưu nguyên report lỗi.
  Build helper mới PASS 57,15 giây; gate Boundaries sau chuẩn bị mesh PASS độc lập.
  Test-City6800Gameplay.ps1 tiếp tục tám fixture từ prerequisite map/body/ranh giới đã đạt.
- Fixture vật lý Core/East/West/South/NorthEast đã viết/build: 16 xe mỗi vùng, đủ vòng và bốn trạm.
  Giữ đường, tốc độ, collider và giới hạn streaming; năm vùng đều PASS. Tàu authored giữ nguyên tick.
- Checkpoint QA 086104425cb8a59eb27f17d8b93d3a68d919107e đã push; LFS fsck PASS, remote SHA khớp.
- Checkpoint tuyến khu vực/menu FPS/ảnh 98b9688241579567e1023b54faf5fdb2f6e90680 đã push, remote SHA khớp.
  Đã build/automation 23 bài PASS; map/EXE tại checkpoint nguồn vẫn 3,4 km.
- Checkpoint QA khu vực 5ebc30bf499bdbab9ad4eabc4f094ad736a0f7bd đã push; LFS fsck PASS, remote SHA khớp.
  Gồm 11 tệp nguồn/tài liệu; map 6,8 km chưa commit vì gate thực địa còn chạy.
  Mốc này là checkpoint trước readback; chuỗi hiện đã dừng tại gate ranh giới.
- Readback 6,8 km PASS sau 588,51 giây: đủ 86.180 actor, 85.386 nhóm, 1.660.761 instance, 12 dịch vụ.
  Collision tiếp theo PASS: 34.617 component, 154.964 instance chặn, 13.987 điểm đường trong 49 vùng.
  Ranh giới sau chờ compilation PASS 14/14; chưa coi gameplay hoặc chặn rìa trong EXE là PASS.
- Bộ thử EXE Max có ba biến thể GI32/Reflections4/VsmBias0, kiểm actual cvar và hash cùng package.
  Giữ đủ mọi frame, yêu cầu evidence mới và phục hồi hai slot QA trong finally; chín fixture dữ liệu PASS.
  Chưa chạy EXE 6,8 km hoặc nghiệm thu hình ảnh/FPS; không thay đổi preset mặc định từ các trial chưa đo.
- Checkpoint f3cf22c010deea49d3671a22e26f73a752a6f15e đã push, LFS fsck PASS, remote SHA khớp.
  Chỉ mã/tài liệu; map mới chưa stage. Không coi checkpoint nguồn là EXE hoặc HLOD mới.
- Fixture tàu đầu FAIL sau 180 giây vì mốc khứ hồi lấy khi tàu giữa đường; report lỗi/log đã lưu riêng.
  Mỗi tàu chạy 59.108,75 cm, lên/xuống tám lượt, blocker rỗng; chưa đủ điều kiện fixture khứ hồi.
  Đã sửa chỉ lấy mốc tại điểm dừng, đếm boarding/alighting mới, ghi returnDistanceCm và startedAtStop.
  Build PASS 68,40 giây; giữ nguyên tốc độ/tuyến/collider và ngưỡng 180 giây/3.800 cm/1.900 cm.
  Gate hai tàu PASS: 52,43 giây đo, 109,44 giây cả process; hai lượt lên/hai lượt xuống mới mỗi tàu.
  Mỗi tàu đi 15.667,19 cm, xa nhất 3.916,81 cm, quay về sai số 0,097 cm, không blocker.
  Rowboat tiếp theo PASS 29,91 giây cả process, 9,70 giây fixture input thật E/W/Space/E tại bến.
  Chèo 78 cm, đỉnh 4,32 km/h, phanh về gần 0, xuống bến khô/capsule không overlap, từ chối xuống biển.
  Test từ chối xuống biển dời thuyền riêng lúc setup; không tính phần dời vào quãng chèo đã đo.
  RoofPool tiếp theo PASS 63,41 giây cả process, 43,12 giây fixture W trên cầu thang map thật.
  Lên/xuống đủ 41 bậc, 2.600 mẫu floor/clearance, đứng trên mái Z=840 và trở lại sân Z=20; không lỗi.
  Không teleport/mặt đỡ giả/đổi movement trong đoạn đo; capsule 38/92 nguyên, chưa kiểm bơi hoặc hình ảnh.
  Core tiếp theo PASS tám loại/hai xe mỗi loại, đủ bốn điểm lên/xuống, hai vòng đầy đủ mỗi loại.
  Core đo 140,82 giây, process 182,20 giây; report mới 03:02:32 UTC ngày 10/10.
  East/West/South/NorthEast tiếp theo đều PASS; process lần lượt 187,62/192,87/203,78/217,38 giây.
  Chuỗi tổng PASS 8/8 và exit 0 lúc 03:15:57 UTC; giữ report FAIL đầu và log để truy nguyên.
  Chuyến biển dài, ảnh GPU, EXE và FPS vẫn chờ; fixture không thay nghiệm thu gameplay người chơi.
- Checkpoint rail 67e4229266d4f052f7cab4783b36da9b9269b17f đã push, remote SHA khớp.
- Gate HLOD identity mới bắt đúng map 6,8 km, hash evidence, log rebuild mới và actor/GUID đầy đủ.
  27 fixture dữ liệu PASS; tám regression cầu nối boundary-source PASS; build C++ PASS 60,38 giây.
  API thực đọc 31 nguồn proxy cũ PASS exit 0; chỉ xác nhận binding, không nhận HLOD cũ làm map mới.
  Chi tiết: CITY_6800_HLOD_IDENTITY_GATE.md; full rebuild/readback vẫn chờ.
  Checkpoint 7e539694f64afc305e1aa5b2a7851f18d270b172 đã push, remote SHA khớp.
  Full rebuild PASS 3.557 proxy, exit 0; run 9a4ba05837584d998162a3092dd72dba, xong 03:44:18 UTC.
  Readback PASS exit 0: đủ 3.557/3.557 actor/GUID, 1.619.348 instance, mesh/material không thiếu.
  83.212 source mapping được kiểm; bốn collider ẩn loại khỏi HLOD, không violation/limitation.
  Receipt đầu bị từ chối vì Sort-Object theo culture khác Python ordinal; hai tập thực đều đủ 3.557.
  Đã sửa so danh sách ordinal, vẫn bắt thiếu/trùng/sai actor; sáu regression và receipt thật PASS.
  Giữ report lỗi riêng; readback lại mất 21,16 giây, peak RAM 4.222 MB, không cần rebuild HLOD lần nữa.
  FullMapAccepted là cấu trúc, renderedArtAccepted/fpsAccepted vẫn false.
- Lượt 30 ảnh phương tiện đầu đủ file nhưng render scale thực 3%; xem ảnh và RenderConfig phát hiện lỗi.
  Regex sg.*Quality bắt cả ResolutionQuality; sửa đặt native 100% sau quality và thêm gate cvar thực.
  Bốn regression chạy các assignment AST của runner PASS, gồm input 100/85/3/72,5.
  Giữ toàn bộ ảnh/log lỗi trong CityPlacement_metro_Scale3Rejected; không nhận chất lượng hoặc FPS.
  Đang chụp lại native 100%; sửa script QA không đổi model, map hoặc preset game.
  Lượt native lại FAIL exit 3 trước capture: DXGI_ERROR_DEVICE_HUNG/PageFault ở Nanite culling/VSM.
  Log CityPlacement_metro.log 03:53:48 UTC ghi ReservedResources=0 đã áp dụng; chưa kết luận root cause.
  File native không có RenderConfig/ảnh đầu; không nhận hình ảnh, Max hoặc FPS từ lượt 3% trước.
  Chuẩn bị package City6800 để so Player/Editor; vật lý/HLOD cấu trúc vẫn PASS, ảnh chưa đạt.
- Rà HLOD thấy report cũ 962 proxy/591.633 instance không thuộc map mở rộng; phải kiểm lại map identity.
  Chi tiết và các gap cần sửa: CITY_6800_HLOD_READINESS.md.
- Rà GPU độc lập đã ghi ba phương án và đánh đổi trong CITY_GPU_COST_AUDIT.md; chưa áp dụng thử mới.
  Rà crash/reload tiếp theo: CITY_6800_GPU_RELOAD_DIAGNOSIS.md; nguyên nhân/ổn định còn chưa xác nhận.
- Đọc đủ 25.801 actor nền theo lô PASS: 25.026 nhóm, 602.965 instance, 12 dịch vụ.
  Sửa cách đếm bỏ sót năm HISM Living_CivicDressing; đối chiếu nguồn commit cũ cùng số instance.
  Báo cáo nền đã hòa giải thay vòng quay 282 thành một và cabinet bỏ 42/thêm 54; không sửa map.

## Các bước cần làm tiếp

1. Đã xong nguồn model/tám hướng/FBX/bounds/material/LOD; ảnh Unreal vẫn ở bước 4.
2. Map 6,8 km đã apply/readback, automation/body/đường/ranh giới PASS.
3. Tám fixture vật lý thuyền/tàu/mái/năm vùng xe PASS; còn gameplay người chơi trong EXE.
4. Chụp/xem năm góc từng vị trí mới; sửa nổi/chìm/xuyên/lệch hoặc silhouette chưa hợp lý.
5. Rebuild toàn bộ HLOD, kiểm proxy, package EXE riêng City6800.
6. Gameplay ngắn native Max, giữ mọi frame; kiểm cài đặt/save/reload và lỗi GPU.
7. Ghi kết quả, commit/push, LFS fsck và đối chiếu remote SHA.

Model nguồn hoặc ảnh render xong không tự đồng nghĩa nghiệm thu gameplay/đẹp/90 FPS.
