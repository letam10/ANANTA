# Vòng props nhỏ/camera native 2026-10-10

## Đã kiểm

- Branch `codex/city-expansion`, tiếp tục từ checkpoint `75e65f3`.
- Native read-only commandlet exit 0: 85 actor nguồn, 43 bounds mesh/instance trên map đã lưu.
- Đủ tám props PASS kê đỡ, source/native parity, NoCollision, spatial loading, không chồng AABB.
- Nồi–ấm cách 2,9555 cm. Sai lệch nguồn/native lớn nhất 0,0000381 cm.
- CookingPot không xuyên ấm; camera cũ đi qua ấm/lò. Compact-left bị bình trên bàn che.
- Giữ geometry/actor/material/quality, không cần rebuild HLOD từ lượt đọc này.
- Không sửa model nhân vật hoặc save cá nhân.

## Kết quả vòng

- Camera mới đã tích hợp; bảy test PASS, tái hiện ba góc cũ bị che.
- Công trình shadow On FAIL GPU frame 811, exit 3, chưa ghi PNG đầu tiên.
- Props DRED đầu có 45 PNG nhưng wrapper FAIL vì tracking chỉ có khai báo deferred.
  Giữ evidence `CityPlacement_small_Dred_TrackingUnverified` và log `.TrackingUnverified.log`.
- RenderConfig mới quan sát `D3D12.TrackAllAllocations=true`; 11 gate regression PASS.
- Build QA PASS 42,47 giây. Props DRED PASS 45 PNG/9 contact native 1920x1080, scale 100%.
- Đã xem đủ chín contact: năm góc mỗi vị trí hiện rõ; nồi/chảo/compact hết góc bị đồ khác che.
- Nhận phạm vi camera/placement props; chưa nhận mỹ thuật cuối, toàn bộ va chạm hoặc FPS.
- Công trình DRED PASS 50 PNG/10 contact; đã review đủ mười công trình, còn ở mức prototype.
- Factory cần rà chi tiết bốc hàng lệch; Airport cần góc gần mặt đất để kiểm terminal.
- DRED có overhead; không dùng ảnh để nghiệm thu performance Max hoặc ổn định GPU.

## Bằng chứng

- `Saved/QA/CitySmallNativeBounds.json`, `CitySmallNativePlacement.json`.
- `Saved/Logs/CitySmallNativeBoundsAll.log`, marker CITY_SMALL_NATIVE_BOUNDS_OK, exit 0.
- `python Tools/QA/VerifyCitySmallNativePlacement.py`: CITY_SMALL_NATIVE_PLACEMENT_OK, props=8.
- Source camera round: `Docs/CITY_SMALL_CAMERA_ROUND_CONTRACT.md`.
- `Saved/QA/CityPlacement_small_Dred/ManualReview.json`: phạm vi review và SHA256 của 45 ảnh.
- `Saved/QA/CityPlacement_facilities_Dred/`; review: `CITY_6800_FACILITIES_VISUAL_REVIEW.md`.

## Còn mở

- 90 FPS Max native, lỗi GPU khởi động/reload, package có thuyền mới.
- Camera props đã nhận; Factory/Airport, góc tàu bị cột che, cảng/biển/art toàn thành phố còn mở.
- Gate EXE rìa map và hành trình biển dài vẫn chưa chạy.
