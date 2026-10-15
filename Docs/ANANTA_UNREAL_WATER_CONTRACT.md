# ANANTA Unreal Water Contract (W3)

Version: W3, 2026-10-16
Source: `Prototypes/ThreeWater/public/wave-spec.json`

## Mục tiêu

Contract này là cầu nối tham số từ prototype Three.js sang Unreal. Nó không thêm
water physics, buoyancy hoặc boundary logic vào shader. Unreal phải giữ water
opaque, normal động và foam nhẹ; collision boundary là actor/component riêng.

## Source và integrity

- Wave spec schema: `ananta.three-water.wave-spec.v2`.
- Source SHA-256: `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f`.
- Hash được tính trên sorted UTF-8 JSON sau khi đặt `hash.value` về
  `PENDING_HASH`; contract JSON giữ cùng hash tại
  `Prototypes/ThreeWater/public/unreal-water-contract.json`.
- Validator phải reject khi source hash, schema, wave count hoặc parameter tuple
  không khớp.

## Material Function contract

Tên dự kiến: `MF_AnantaWater`.

```text
MF_AnantaWater(WorldPosition, Time, Wave[]) ->
  { BaseColor, Normal, Roughness, Emissive }
```

Mỗi wave giữ nguyên các trường từ source, không đoán lại:
| Trường | Kiểu | Đơn vị |
| --- | --- | --- |
| direction | float2 | hướng ngang đã chuẩn hóa |
| wavelength | float | meters |
| amplitude | float | meters |
| speed | float | meters/second |
| phase | float | radians |

Công thức dùng cùng source:
```text
phase = 2π * (dot(normalize(direction), horizontalPosition) / wavelength
              - speed * time / wavelength) + phase
height += amplitude * sin(phase)
```

Normal lấy đạo hàm cùng trường sóng. UE dùng `float3(-dHeightDx, -dHeightDy,
1)` sau khi đổi trục, rồi normalize.

## Trục và boundary

```text
UE.X = Three.X
UE.Y = Three.Z
UE.Z = Three.Y
```

Boundary W2/W3 là box biển riêng:
```text
minX = -700 m   maxX = 700 m
minZ = -400 m   maxZ = 400 m
cameraMargin = 14 m
boatMargin = 8 m
```

Material chỉ dùng boundary để fade foam nếu cần. Chặn camera/thuyền phải dùng
collision/route bounds riêng, không suy ra collision từ shader hoặc opacity.

## Foam và graph readback

- BaseColor: opaque blue water color.
- Normal: dynamic normal từ bốn wave source.
- Roughness: scalar đọc lại được.
- Emissive: cheap foam/shore contribution, không dùng translucent water.
- Foam width `6 m`, shoreline depth `16 m`, distance field là cạnh boundary gần
  nhất, falloff `smoothstep`.

Gate Unreal vẫn cần readback thật bốn output, boundary collision ở đúng rìa và
ảnh so sánh cùng camera `coast`, `beach_boat`, `offshore`. Contract này không
được gọi là material graph PASS nếu chưa có các evidence đó.

## Performance boundary

W2 chỉ chạy quick QA khoảng 10 giây mỗi cảnh. F1 mới được phép tuyên bố 60 FPS;
config, build, NullRHI, browser overlay hoặc contract hash không thay thế số đo
GPU/CPU/VRAM headed.
