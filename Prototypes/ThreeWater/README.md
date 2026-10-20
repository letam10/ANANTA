# ANANTA Three.js Coastal Water Prototype

Prototype nước biển độc lập cho W2. Đây là gate trước khi port shader và tham số
sang Unreal; không có file Unreal nào thuộc prototype này.

## Chạy

```powershell
npm install
npm run check
npm run build
npm run dev -- --host 127.0.0.1 --port 4178
```

Mở `http://127.0.0.1:4178/` trong browser. `package-lock.json` pin dependency
Three.js/Vite. Validator contract chạy từ repository root:

```powershell
python Tools/QA/ValidateThreeWaterSpec.py
```

Kiểm tra contract không cần browser:

```powershell
npm run test:contract
```

Bộ kiểm tra so đạo hàm số với normal giải tích tại nhiều tọa độ/thời điểm,
đối chiếu cả ba camera với spec và kiểm margin camera/thuyền ở cạnh/góc.
Ca âm cố tình đổi target camera phải bị phát hiện. `boundary.type=box` được
ưu tiên ngay cả khi JSON kèm polygon để trao đổi với Unreal.

Receipt mới ngày 20/10/2026: `Tools/Continuation_20261020/W2_browser.json` tại
repository root; ảnh coast/orbit đi kèm. Đây là browser prototype evidence,
không chứng minh Unreal runtime/FPS.

## Điều khiển và W2 quick QA

- Orbit bằng kéo chuột; nhấn `C` để chuyển free camera.
- Free camera dùng `WASD` và `R/F`; `B` bật/tắt boundary preview.
- `F` bật/tắt foam khi orbit; `Space` pause/resume thời gian sóng.
- `1`, `2`, `3` chọn lần lượt `coast`, `beach_boat`, `offshore`.
- Auto QA chạy đúng ba cảnh, mỗi cảnh 10 giây, rồi dừng và hiển thị report.
- Overlay hiển thị frame time, p95, max, outlier, draw calls, triangles,
  geometries, textures, wave count và trạng thái boundary/foam.
- Overlay là số đo browser quick QA; mục tiêu 60 FPS chỉ được kết luận trong F1.

W2 dùng biển rộng từ `boundary` trong `public/wave-spec.json`, không dùng hồ
nhỏ. Camera và boat được clamp theo margin riêng. Foam là một mặt phẳng cố định,
fragment shader tính khoảng cách tới cạnh boundary; không rebuild CPU mesh trong
animation loop.

## Contract kỹ thuật

- Three.js ES modules dùng Y-up; mặt phẳng nước nằm trên XZ và dùng một
  `PlaneGeometry` cố định.
- Preset thấp có tối đa bốn sine/Gerstner-like waves. Trường sóng dùng:
  `phase = 2π * (dot(normalize(direction), horizontalPosition) / wavelength`
  `        - speed * time / wavelength) + phase` và
  `height += amplitude * sin(phase)`. Normal lấy từ đạo hàm của cùng phase.
- `WaveField` chỉ làm nguồn CPU để bob chiếc boat QA. Không có FFT, fluid
  simulation nặng, physics hoặc buoyancy gameplay.
- `CoastBoundary` có box/polygon preview, containment, distance và clamp.
- `public/wave-spec.json` ghi schema version, hash SHA-256, units, axes, wave
  tuples, foam width/depth, boundary và ba camera preset.

## W3 Unreal handoff

`public/unreal-water-contract.json` và `Docs/ANANTA_UNREAL_WATER_CONTRACT.md`
ghi cùng direction, wavelength, amplitude, speed và phase. Mapping là
`Three.X → UE.X`, `Three.Z → UE.Y`, `Three.Y → UE.Z`. Material function dự kiến
`MF_AnantaWater` trả `BaseColor`, `Normal`, `Roughness`, `Emissive`; boundary
collision nằm ngoài shader. Unreal graph readback và ảnh so sánh cùng camera
vẫn là gate W3 riêng, chưa được prototype này tự nhận là PASS.

## Giới hạn acceptance

W2 chỉ xác nhận module/build/browser quick QA: sóng nhìn thấy ở gần và xa,
foam fade, boundary preview/clamp, ba scene report và console sạch. Gate này
chưa chứng minh chất lượng AAA toàn thành phố, native Unreal persistence,
interaction gameplay, collision native hoặc 60 FPS trên phần cứng mục tiêu.
