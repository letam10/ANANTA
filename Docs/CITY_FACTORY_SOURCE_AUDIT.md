# Factory source audit

Cập nhật: 11/10/2026. Phạm vi là hình học AABB từ source, chưa phải nghiệm thu Unreal.

## Đã sửa

- Apron loading rộng 3.000 cm, nằm trong shell từ `x+300` đến `x+3.300` và không chặn lane `x±300`.
- Apron chạy sát mặt trước shell tại `y-2.000`; hai shutter có mặt sau flush với tường.
- Đáy shutter cùng cao độ 40 cm với mặt apron.
- Bốn bollard dùng cao 110 cm, nằm trong mục tiêu 80–140 cm.
- Dải cảnh báo vàng được dời ra ngoài AABB planter mặt trước.

## Bằng chứng source-only

- `VerifyCityFactorySource.py`: PASS, 96 instances, `issues=[]`.
- `TestCityFactorySource.py`: 7 tests PASS; mutation tests bắt lại mép shell, cao độ shutter,
  chiều cao bollard và planter clearance bị lệch.
- `VerifyCity6800Layout.py`: PASS, 10.750 buildings, 6,788.225 m source width, 9 access lanes,
  4 hidden boundaries và 3 ocean surfaces.

## Giới hạn

Receipt này không chứng minh import Unreal, saved actor map, simple collision, NPC traversal,
HLOD, visual five-angle, GPU stability hay FPS. Map và external actor tree không được sửa trong
vòng này; cần controlled apply/readback trước khi gọi factory đã nghiệm thu runtime.
