# ANANTA full-build plan — 2026-10-17

## Mục tiêu

Chốt một đường build có thể lặp lại cho ANANTA và tách rõ bốn loại bằng chứng:
source/build, Blender visual fixture, native Unreal/runtime, và headed performance.
Kế hoạch này không biến build, config hoặc NullRHI thành bằng chứng 60 FPS.

## Ràng buộc hiện tại

- Làm trong `D:/GAME/ANANTA` và chỉ tạo/sửa file trong `Tools/FullBuild_20261017/`.
- Giữ nguyên `AGENTS.md`, mọi file Unreal/map/ExternalActors dirty và các evidence cũ.
- Không port W3 vào Unreal trong lượt này: graph hiện tại chưa phải `MF_AnantaWater` và
  native boundary/camera comparison chưa có evidence đủ.
- Không stage/commit/push khi ma trận gate có BLOCKED hoặc UNVERIFIED bắt buộc.

## Trình tự build chuẩn

1. **Inventory và ownership** → `git status`, remote hash, kiểm tra không có process
   Blender/Unreal bất ngờ.
2. **Source validators** → py_compile, A3C/A3D/A4/A5/A6 validators, W3 readback,
   ThreeWater spec/check/build.
3. **Unreal source build** → `Validate-ANANTA.ps1`, `Build-ANANTA.ps1`.
4. **Receipt** → ghi exit code, stdout marker, file scope và blocker vào JSON/Markdown.
5. **Release decision** → chỉ gọi PASS cho gate đúng phạm vi; runtime/FPS/native
   visual vẫn giữ UNVERIFIED nếu chưa có headed evidence.

## Definition of done cho full build

- Source/build validators exit 0.
- ThreeWater contract canonical hash đúng, tối đa bốn waves, fixed mesh và `fpsClaim=false`.
- A3C/A3D/A4/A5/A6 artifacts có review 8 hướng, placement 5 góc từ transformed bounds,
  save/reopen ownership và interaction/static-dressing classification.
- Unreal foundation validation và editor build exit 0.
- Không có file ngoài thư mục tác vụ bị ghi bởi orchestration.

## Gate chưa được phép gọi đạt

- W3 native `MF_AnantaWater`, boundary collision readback và same-camera Three/Unreal.
- Native import/readback, LOD/collision, enterable venue state và interaction/persistence.
- F1 headed CPU/GPU/VRAM với `stat unit`, `stat gpu`, `stat sceneRendering`,
  `stat initviews`, `stat levels` ở downtown/traffic, interior/alley và coast/streaming.
- AAA visual acceptance toàn map, World Partition/HLOD/Data Layers/PCG.

## Kế hoạch sau full-build receipt

- Pha N1: native import/readback cho một hero tranche, không đụng file dirty.
- Pha N2: W3 material function + boundary collision trong branch/ownership riêng.
- Pha N3: headed hero camera ngang tầm người và interaction/static-dressing audit.
- Pha N4: F1 three-scene headed capture, rồi mới tối ưu theo bằng chứng.
- Chỉ sau N1–N4 đạt mới xét commit/push theo allowlist.
