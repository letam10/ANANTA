# ANANTA full-build report — 2026-10-17

## Kết quả build

`Run-FullBuild.ps1` đã chạy xong với receipt:
`Tools/FullBuild_20261017/FULL_BUILD_RECEIPT.json`.

- Required gate aggregate: `true`.
- AST parse không ghi bytecode: exit `0`, `files=18`.
- ThreeWater: `npm run check` exit `0`, `npm run build` exit `0`, spec validator exit `0`.
  Hash `f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f`, 4 waves,
  3 scenes, 10 giây/scene.
- A3C: exit `0`, 5 objects, 40 model views, 25 placement views.
- A3D: exit `0`, 8 objects, 64 model views, 40 placement views.
- A4: exit `0`, 11 objects, 88 model views, 55 placement views.
- A5: exit `0`, 12 objects, 96 model views, 60 placement views.
- A6: exit `0`, 1 Citizen, 8 model views, 5 placement views, 5 material groups.
- W3 readback: exit `0`; opaque water + dynamic normal có, nhưng exact wave tuple,
  native boundary collision và same-camera comparison vẫn `false`.
- `Validate-ANANTA.ps1`: exit `0`.
- `Build-ANANTA.ps1 -MaxParallelActions 2`: exit `0`, ANANTA build completed.
- `git diff --check`: exit `0`.
- `git lfs fsck`: exit `1`, nhiều `unexpectedGitObject` pre-existing dưới
  `Assets/CoastalUpgrade/*`, tree `5268d9a15649fd5ad59e5bc5d6878131834ddacf`.

## Phân loại chính xác

**DONE**

- Full-build orchestration và receipt có thể lặp lại.
- Source/AST, ThreeWater source/spec/build, A3C–A6 fixture validators, W3 readback,
  Unreal foundation validation và Unreal source build.
- Review contract cho asset fixtures: 8 hướng và 5 placement views với transformed bounds.

**PARTIAL**

- Đây là integration/source build của checkout hiện tại. Các artifact Blender đã có
  detail và review, nhưng chưa được native import/readback toàn bộ vào Unreal.
- A6 Citizen khóa đúng ranh giới anime character; interaction vẫn chưa phải runtime NPC.

**UNVERIFIED**

- Native Unreal import/readback, LOD/collision và venue enterable state.
- Interaction/persistence native cho nhà, NPC, prop, phương tiện, rail, ga, sân bay,
  thuyền, xuồng và venue.
- W3 material function `MF_AnantaWater`, native boundary collision và camera comparison.
- F1 headed CPU/GPU/VRAM, các stat bắt buộc và 60 FPS.
- AAA visual acceptance toàn map, World Partition/HLOD/Data Layers/PCG.

**BLOCKED**

- Native Unreal asset edits bị giữ ngoài phạm vi vì ownership dirty-file.
- LFS repository có `unexpectedGitObject` pre-existing; không rewrite/xóa object.

## File scope

Tác vụ này chỉ tạo:

- `PLAN.md`
- `GATE_MATRIX.json`
- `Run-FullBuild.ps1`
- `ast_parse.py`
- `FULL_BUILD_RECEIPT.json`
- `logs/*`

Không có `Content`, `Source`, map, ExternalActors hoặc Docs hiện hữu bị sửa bởi runner.
Do AGENTS.md mới yêu cầu mỗi task chỉ sửa file do task tạo, handoff chính hiện tại không
bị ghi đè; báo cáo này là addendum của task và là nguồn receipt mới.

## Quyết định delivery

Không commit/push. Build source đạt nhưng native/runtime/F1 gates chưa đạt và LFS check
vẫn lỗi pre-existing. Bước được phép tiếp theo là native import/readback một hero tranche
trong ownership riêng, sau đó W3 và F1; không dùng build/config/NullRHI để thay thế các gate đó.
