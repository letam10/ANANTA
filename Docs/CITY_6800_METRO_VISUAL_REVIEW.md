# Metro: kiểm ảnh native và sửa lỗi thấy được

Ngày 2026-10-10; map 6,8 km; native 1920x1080, render scale 100%, quality groups 3.
Lượt chụp dùng diagnostic `r.Nanite.AsyncRasterization.ShadowDepths=1`; chưa đổi preset sản phẩm.

## Lượt đầu

- `Test-CityPlacements.ps1 -Scope metro -Diagnostic NaniteShadowAsyncOn`: exit 0, 30 PNG/sáu contact.
- RenderConfig xác nhận native 100%, shadow async=1, VSM bật và GI/reflection của Max tùy chỉnh.
- Đã xem một PNG gốc và đủ sáu contact năm góc: FireEngine, CivilianPlane, Helicopter,
  Rowboat, PassengerTrainEast, PassengerTrainWest.
- FireEngine/máy bay/trực thăng: không thấy float/penetration rõ; paint và scene vẫn đơn giản.
  Sân bay, hangar, biển/cầu tàu còn dạng prototype; chưa nghiệm thu đồ họa cuối.
- Rowboat: sàn dưới waterline làm nước hiện trong lòng; góc phải bị bến gỗ che.
- Hai tàu: camera ở độ cao mái ga nên nhiều hình không thấy trọn model.
- Không nhận `visualAccepted=true` từ số lượng PNG hoặc việc GPU capture hoàn tất.

## Sửa có phạm vi

- Thuyền: sàn kín local Z=33 cm, cao hơn waterline 8 cm; dùng gỗ PBR sẵn có.
  Giữ pivot, bounds, actor/collider/draught; bốn FBX khác không thay đổi.
- Reimport riêng mesh hiện có; importer chung trước đây chỉ nhập khi asset chưa tồn tại.
- Camera tàu: eye Z tương đối 350 cm, góc trên 530 cm; thấp hơn mép mái thấp nhất 567,5 cm.
- Camera thuyền: target tính relative mesh Z=-25 cm; góc phải eye world Z=880 cm, vượt bến/người chơi.
  Góc trên chuyển sang phía biển để người chơi đứng trên bến không che lòng thuyền.
- Không giấu bến/mái hoặc dịch chuyển model để làm ảnh QA đẹp hơn.
- Test camera PASS 15 ray mới; tái hiện roof/dock occlusion của hai góc cũ.
- Nguồn thuyền PASS UV/tris/hash/manifold/coverage/FBX và tám render đã xem.

## Gate tiếp theo

1. Unreal reimport: đúng 4.120 tris, ba material slots, bounds dưới 1 cm, ba LOD, collision tồn tại.
2. Input thật E/W/Space/E: chèo/phanh/xuống bến khô, capsule nguyên và từ chối xuống giữa biển.
3. Lưu lượt ảnh lỗi riêng; chụp lại native và xem năm góc của thuyền/hai tàu.
4. Ghi lỗi còn thấy được và kết quả thực; không suy ra gameplay dài/FPS từ ảnh.

## Kết quả tích hợp đang có

- Reimport Unreal PASS exit 0: 4.120 tam giác Nanite, fallback 1.830, ba LOD, ba slot, một collision.
  Bounds chính xác dưới 1 cm; dùng ba material đã có, không tạo material mới.
- Import lần đầu bị gate đếm render fallback từ chối; lần hai thiếu subsystem instance trong commandlet.
  Đã dùng bộ đếm Nanite và default subsystem đúng API; giữ cả hai log lỗi riêng.
- Fixture input mới ghi success=1: chèo 78,19 cm, đỉnh 4,33 km/h, phanh/xuống bến/sea rejection PASS.
  Wrapper từ chối timestamp vì PowerShell 7 parse lại DateTime UTC làm lệch bảy giờ.
- Đã tái hiện sai lệch 07:25:58 thành 00:25:58; sửa DateTimeOffset, bảy regression timestamp PASS.
  Wrapper chạy lại PASS exit 0: chèo 79,08 cm; phanh/xuống bến khô/capsule/sea rejection đầy đủ.
- Lượt 30 ảnh sau sửa geometry PASS capture, nhưng ảnh lộ binding vật liệu sai.
  Unreal giữ slot cũ `[Living_Enamel,Living_Steel,City_wood_floor]`; gán theo index manifest làm sai ba slot.
- Đã sửa reimport gán theo tên slot; sáu regression PASS, tái hiện ba mismatch và bắt thiếu/trùng/sai vật liệu.
  Unreal readback đúng tên/material, giữ 4.120 tris/ba LOD/collision/bounds và không tạo material mới.
- Lượt riêng thuyền PASS năm PNG native/100%, exit 0; đã mở xem đủ năm góc của contact mới.
  Sàn khô và vân gỗ hiện đúng; góc phải/trên không còn che thuyền. Gate sửa placement thuyền PASS.
- Evidence mới: `CityPlacement_metro_Rowboat_NaniteShadowAsyncOn`; lượt binding sai lưu riêng tại
  `CityPlacement_metro_NaniteShadowAsyncOn_MaterialSlotsRejected`, lượt sàn cũ `_BeforeDryFloor`.
- Hai tàu đã thấy rõ hơn dưới mái; cột ga vẫn che một phần ở góc phải/trên, chưa nhận đủ năm góc.
- Không nhận chất lượng toàn cảnh/đồ họa cuối/90 FPS từ lượt thuyền PASS.
- EXE City6800 vẫn chứa mesh thuyền trước sửa; package mới và gameplay/FPS còn phải kiểm sau.
