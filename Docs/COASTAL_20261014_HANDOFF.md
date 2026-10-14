# Coastal City — bàn giao ngày 14/10/2026

## Phạm vi hiện tại

Tiếp tục bản Coastal City của commit `cc28fc6b50`, Unreal Engine 5.8.3.
Chỉ sửa bộ nguồn/asset CoastalUpgrade và cấu hình đóng gói liên quan.
Theo yêu cầu mới: **không chạy game thật, PIE, gameplay test hoặc benchmark**.
Chụp model trong Blender và cảnh editor không thay thế kiểm chứng gameplay/FPS.

Nhánh giao hàng: `codex/coastal-interiors-20261014`. `origin/main` có 77 commit
riêng so với bản cục bộ (bản cục bộ có 2 commit riêng), nên không force push hoặc
trộn trở lại hàng chục nghìn file thành phố cũ.

## Thay đổi

- 14 model sinh hoạt mới: đĩa, dao/nĩa, ấm, bình xà phòng, khăn gấp, gương,
  tranh, kệ sách, đèn đứng, bàn nhỏ, tủ TV, khay tắm, thớt/dao, khay chai.
  216–2.808 tam giác/model; một vật liệu màu đỉnh, 3 LOD sau import.
- Bộ kit tổng cộng 55 model. Mái nhà hát được dựng lại thành ba vỏ cong có
  bề dày 12 cm, 3.456 tam giác, không còn các đỉnh trùng tại cực bán cầu.
- 9 nhà/căn hộ/khách sạn/studio có 36 phòng: khách, ngủ, bếp và vệ sinh.
  Hành lang rộng 2,4 m, lỗ cửa phòng 1,2 m; bounds model đã xoay/scale được
  kiểm khi dựng để không vượt giới hạn phòng.
- 23 tòa nhà có cửa sổ tầng trệt thật, khung/cửa kính mỏng; trần và vách ngăn
  dùng plaster mịn. Không còn dùng một phòng lớn với vách tắm che camera cũ.
- Đèn phòng dùng lumen, cull 70 m, fade 15 m, bán kính 6,5 m, không tạo shadow
  map riêng. HISM/LOD/cull đồ nhỏ tiếp tục được dùng.
- Import xóa collision cũ trước khi tạo đúng một box: không tích lũy collision
  sau mỗi lần reimport. HUD dùng một truy vấn tương tác mỗi chu kỳ thay vì hai.
- Tranh, gương, bồn rửa, bồn cầu, khay tắm và bếp đặt lưng cách tường 1 cm, suy từ bounds mesh;
  bảng dịch vụ dời khỏi cửa bếp để giữ lối đi.
- GameDefaultMap chuyển sang CoastalCity; bổ sung script đóng gói Windows Shipping
  chỉ cook map này và các dependency, dùng pak/IoStore/nén.

## Kiểm chứng hiện có

- Blender 4.5.1 LTS: sinh 55 model thành công, nhiều nhất 9.678 tam giác/model.
- 440 ảnh = 55 model × 8 góc; đã xem contact sheets. Coverage lưu SHA-256
  nguồn FBX để phát hiện ảnh cũ sau khi model đổi.
- Import commandlet r2: exit 0, 55 model; kích thước mét → cm sai số dưới 0,1 cm,
  mỗi model 3 LOD và đúng một collision shape.
- Build map r5: 23 tòa nhà, 6.859 instance / 884 HISM batch; 180 vị trí camera
  trong 36 phòng, mỗi phòng 5 góc.
- C++ Editor build: thành công; Validate-ANANTA.ps1 exit 0.
- Capture editor r1/r2 xuất ảnh bị trắng; bộ ghép ảnh đã từ chối ảnh này.
  Không coi commandlet exit 0 hoặc đủ số file là đã kiểm xong hình ảnh.
- Dùng ReviewRoomGeometry.py để dựng kiểm hình học từ đúng mesh gốc và manifest
  placement đã xuất từ map. Đây là Blender; ánh sáng/material Unreal chưa được
  xác nhận bằng ảnh trong lượt này.
- Lượt xem 5 góc đã phát hiện khoảng hở quá lớn sau thiết bị vệ sinh/bếp;
  đã tính lại theo bounds và dựng lại map trước khi đóng gói lần cuối.
- ReviewRoomGeometry r2 và ComposeEditorReviews --geometry: exit 0, 180 ảnh /
  36 phòng, đã xem toàn bộ 9 contact sheet. Thư mục bằng chứng:
  `Saved/Upgrade/RoomGeometry/20261014-120753`.
- Package-ANANTA.ps1 r3: Windows Shipping, BUILD SUCCESSFUL, exit 0; 63,65 giây.
  ZIP có 29 file, kiểm CRC đạt; chưa chạy executable.
- Git LFS fsck đạt. Cảnh báo build còn lại thuộc API deprecated trong Engine.

## Còn tồn đọng / chưa xác nhận

- Không chạy lại tương tác, collision người chơi, xe/thuyền, đóng mở cửa hay thang máy.
- Chưa đo 60 FPS. Máy đang nhận RTX 4060 Laptop GPU; ghi chú RTX 3050 cũ không
  mô tả phần cứng của lượt này. Không suy FPS từ triangle count hoặc thời gian build.
- Thành phố còn thưa và nhiều model còn đơn giản. Các tầng trên chủ yếu là mặt dựng;
  chưa có World Partition/HLOD cho CoastalCity.
- NPC chưa có lịch sinh hoạt; phương tiện còn kinematic; chưa có lái bay, chèo tay,
  minigame, save kinh tế đầy đủ. Gương trang trí chưa có phản chiếu camera riêng.
- 5 góc mỗi phòng chưa tương đương 5 góc cận từng instance trong toàn thành phố.
- Ảnh editor Unreal vẫn chưa đạt (trắng); chỉ ảnh Blender được chấp nhận cho hình học.

## Bản đóng gói

- Thư mục: `Saved/Packages/ANANTA-Coastal-Windows/Windows`.
- Launcher: `Windows/ANANTA.exe`; executable thực:
  `Windows/ANANTA/Binaries/Win64/ANANTA-Win64-Shipping.exe`.
- ZIP: `Saved/Packages/ANANTA-Coastal-Windows-20261014.zip`, 401.479.970 byte.
- SHA-256: `6c2d5bf38609b51a1e55546e5286090bc1412e010024a419c0fda5abfb3c84c3`.
- [Hướng dẫn mở bản Windows](COASTAL_WINDOWS_README.md).
- [Ảnh kiểm bố trí 5 góc bằng Blender](Evidence/Coastal20261014/rooms-five-views.jpg).
- [Ảnh mái nhà hát 8 hướng](Evidence/Coastal20261014/model-review.jpg).
- Source/asset/map/Docs được giao trên nhánh `codex/coastal-interiors-20261014`.
  Không gộp thay đổi `AGENTS.md` có sẵn của người dùng. ZIP nằm trên máy,
  không tự tạo GitHub Release.

## Lệnh tái tạo

Từ thư mục dự án:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --factory-startup --python-exit-code 1 --python Tools/Upgrade/GenerateCoastalModels.py
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --factory-startup --python-exit-code 1 --python Tools/Upgrade/ReviewModels.py
python Tools/Upgrade/ComposeModelReviews.py
& .\Tools\Build\Build-ANANTA.ps1 -MaxParallelActions 2
& .\Tools\Build\Validate-ANANTA.ps1
& .\Tools\Build\Package-ANANTA.ps1
```

Import và dựng map dùng `UnrealEditor-Cmd.exe ANANTA.uproject -run=pythonscript`
với `-script=<đường dẫn ImportCoastalModels.py hoặc BuildCoastalCity.py>`,
`-NullRHI -unattended -nosplash`. Không dùng `-game` hoặc `-CoastalQA`.
CaptureEditorPlacements dùng `-AllowCommandletRendering -RenderOffscreen`,
không dùng NullRHI; đây là editor world, không chạy BeginPlay.
