# ANANTA Three.js Water Prototype (W1)

Prototype nước biển độc lập cho ANANTA. Đây là gate trước khi port shader và
parameters sang Unreal; không có file Unreal nào thuộc prototype này.

## Chạy

```powershell
npm install
npm run check
npm run build
npm run dev -- --host 127.0.0.1 --port 4178
```

Mở `http://127.0.0.1:4178/` trong browser. `package-lock.json` được tạo bởi
`npm install` và giữ đúng các phiên bản trong `package.json`.

## Điều khiển và gate

- Kéo chuột để orbit camera; nhấn `C` để chuyển free camera.
- Free camera dùng `WASD` và `R/F`; `B` bật/tắt boundary preview.
- `F` bật/tắt foam khi đang ở orbit; `Space` pause/resume thời gian sóng.
- Overlay góc trên trái hiển thị frame time đo được, draw calls, triangles,
  camera mode, số wave và trạng thái boundary/foam. Mục tiêu 60 FPS tương ứng
  ngân sách 16.667 ms; overlay không tự chứng minh một tier GPU đạt mục tiêu.
- Browser smoke phải thấy `document.body.dataset.qaReady=true`, hook
  `window.__ANANTA_WATER_QA__`, bốn wave, boundary preview, foam và không có
  console error.

## Contract kỹ thuật

- Three.js ES modules dùng Y-up; mặt phẳng nước nằm trên XZ và dùng một
  `PlaneGeometry` cố định. Không rebuild geometry trong animation loop.
- Preset thấp có tối đa bốn sine/Gerstner-like waves. Trường sóng dùng:
  `phase = 2π * (dot(normalize(direction), horizontalPosition) / wavelength`
  `        - speed * time / wavelength) + phaseOffset`

  `height += amplitude * sin(phase)`. Normal lấy từ đạo hàm không gian của
  cùng phase, không dùng normal độc lập.
- `WaveField` là nguồn CPU để bob chiếc boat QA. Boat chỉ là visual fixture;
  nó bám height/normal để kiểm tra mắt, không phải buoyancy gameplay.
- Foam là lớp shader mỏng ở dải boundary. `CoastBoundary` cung cấp rectangle
  preview, containment và clamp để chặn rìa map trong prototype.
- Chưa làm FFT, mô phỏng chất lỏng nặng, collision vật lý hoặc gameplay boat.

## Quy đổi Unreal

Prototype giữ tọa độ ngang Three.js `(X, Z)` và chiều cao `Y`. Khi port sang
Unreal Z-up, mapping mặc định của contract là:

`X_unreal = X_three`, `Y_unreal = Z_three`, `Z_unreal = Y_three`.

Direction Three `[dx, dz]` trở thành Unreal `[dx, dy]`; wavelength, amplitude,
speed và phaseOffset giữ nguyên theo cùng đơn vị. Kiểm tra handedness và dấu
heading trong scene Unreal trước khi chép shader.

## Giới hạn acceptance

Gate W1 chỉ xác nhận module/build/browser prototype: sóng nhìn thấy được, camera
orbit/free hoạt động, foam và boundary preview hiện diện, không seam khi camera
di chuyển, overlay có frame-time/render-info và console sạch. Gate này chưa
chứng minh chất lượng AAA toàn thành phố, native Unreal persistence, interaction
gameplay hoặc 60 FPS trên RTX 3050/4060. Chỉ sau gate này mới xem xét port
shader/parameters sang Unreal trong pha riêng.
