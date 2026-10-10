# Props nhỏ: review native 2026-10-10

## Lượt đã chạy

- `Test-CityPlacements.ps1 -Scope small -Diagnostic NaniteShadowAsyncOn`: exit 0.
- Chín vị trí/45 PNG native 1920x1080, render scale 100%, quality groups 3; chín contact đã mở xem.
- Đây là diagnostic shadow async On; không nhận performance Max hoặc độ ổn định GPU từ capture.
- Evidence: `Saved/QA/CityPlacement_small_NaniteShadowAsyncOn/` và log cùng tên trong Saved/Logs.

## Các phát hiện

| Vị trí | Review năm góc |
| --- | --- |
| CookingPot | Nồi nằm trong vùng ấm trên quầy, có dấu hiệu chồng hình; góc sau bị lò che. Cần sửa. |
| Saucepan | Đặt trên quầy, chưa thấy nổi/xuyên rõ; ấm lớn che một phần hướng sau. |
| KitchenBowl | Nhìn được năm hướng, chưa thấy nổi/xuyên rõ; hình học đơn giản phù hợp prop nhỏ. |
| CoffeeMug | Năm hướng thấy cốc cạnh đèn, không thấy chồng thân với chân đèn. |
| MakeupCompact | Góc trái bị chân đèn che; chưa nhận đủ năm góc. |
| ToyBlocks | Năm hướng nhìn được, đặt trên sàn; giữ mô hình đơn giản cho đồ chơi nhỏ. |
| RoomVase | Năm hướng nhìn được, chưa thấy nổi/xuyên rõ; đồ bàn hiện có còn lớn/thưa. |
| BathroomSoap | Năm hướng nhìn được trên kệ; chưa thấy nổi/xuyên rõ. |
| KitchenSink | Năm hướng thấy lòng bồn/rim/vòi, không thấy hộp đặc lấp lòng; ánh sáng tối, vòi còn faceting. |

## Sửa tiếp

1. Đối chiếu CookingPot với geometry quầy/ấm hiện có và chuyển tới khoảng trống trên cùng quầy.
   Source hiện tại `(bx+2770,by+1300,120)`; lò `(bx+2700,by+1300,120)`, nên cần kiểm footprint thực.
2. Camera compact/nồi/chảo cần tránh chân đèn/lò/ấm; giữ các model và đồ hiện có trong scene.
3. Apply đúng actor trên map, kiểm bounds/floor/không chồng; cập nhật HLOD nếu actor thuộc proxy.
4. Chụp lại các vị trí đã sửa; các PNG đầy đủ không thay cho manual review.

Chưa sửa source/actor CookingPot trong vòng này. Chưa nghiệm thu toàn scope hoặc đồ họa cuối.
