# Props nhỏ: review native 2026-10-10

## Lượt hiện hành

- `Test-CityPlacements.ps1 -Scope small -Diagnostic Dred`: exit 0.
- Chín vị trí/45 PNG native 1920x1080, scale 100%, quality groups 3; đã xem đủ chín contact.
- Runtime `D3D12.TrackAllAllocations=true`, shadow async=0; 11 regression gate tracking PASS.
- Đây là lượt DRED có overhead, không dùng để nhận performance Max hoặc ổn định GPU.
- Evidence: `Saved/QA/CityPlacement_small_Dred/`, `ManualReview.json` và log cùng tên.

## Kết quả năm góc

| Vị trí | Review năm góc |
| --- | --- |
| CookingPot | Năm góc hiện rõ; góc trước/sau mới tránh ấm/lò. Không thấy nổi/xuyên. |
| Saucepan | Năm góc hiện rõ; góc sau mới tránh phần ấm che. Đặt trên quầy. |
| KitchenBowl | Nhìn được năm hướng, chưa thấy nổi/xuyên rõ; hình học đơn giản phù hợp prop nhỏ. |
| CoffeeMug | Năm hướng thấy cốc cạnh đèn, không thấy chồng thân với chân đèn. |
| MakeupCompact | Góc trái mới nhìn rõ phía trên bình trang trí, đủ năm góc. |
| ToyBlocks | Năm hướng nhìn được, đặt trên sàn; giữ mô hình đơn giản cho đồ chơi nhỏ. |
| RoomVase | Năm hướng nhìn được, chưa thấy nổi/xuyên rõ; đồ bàn hiện có còn lớn/thưa. |
| BathroomSoap | Năm hướng nhìn được trên kệ; chưa thấy nổi/xuyên rõ. |
| KitchenSink | Năm hướng thấy lòng bồn/rim/vòi, không thấy hộp đặc lấp lòng; ánh sáng tối, vòi còn faceting. |

## Đối chiếu placement

- Native read-only: 85 source actor/43 bounds, exit 0; tám props PASS parity, kê đỡ và AABB.
- Sai lệch nguồn/native tối đa 0,0000381 cm; nồi–ấm cách 2,9555 cm, không chồng hình học.
- Tám props dùng NoCollision/spatial loading; gate này không nghiệm thu mọi va chạm thành phố.
- Chỉ sửa camera; geometry/actor/material không đổi nên không cần rebuild HLOD cho lượt này.
- Bảy test camera PASS: tái hiện ba góc cũ bị che, 15 center ray/32 corner ray mới tránh vật cản.

Evidence: `Saved/QA/CitySmallNativeBounds.json`, `CitySmallNativePlacement.json`,
`Saved/Logs/CitySmallNativeBoundsAll.log`. Geometry/actor không đổi nên không làm HLOD mất hiệu lực.
## Phạm vi nhận và phần còn mở

- Nhận camera visibility của chín vị trí và placement trong phạm vi tám props đã đọc bounds.
- Chưa nhận mỹ thuật cuối: lòng bồn tối, vòi faceting, highlight nền/quầy mạnh, dressing còn thưa.
- Chưa nhận toàn bộ physics, Player/reload hoặc 90 FPS từ những ảnh này.
- Lượt DRED đầu bị từ chối vì thiếu tracking runtime vẫn giữ ở `CityPlacement_small_Dred_TrackingUnverified`.
- Lượt shadow On cũ giữ làm đối chứng; không dùng các góc bị che để nhận lượt hiện hành.
