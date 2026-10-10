# Rowboat: sàn khô và vật liệu gỗ

Ngày 2026-10-10. Nguồn chuẩn: `Tools/CityAssets`; Blender 5.2.0 LTS, CPU hai thread.

## Thay đổi

- Thêm sàn kín dày 3 cm: mặt đi lại thấp nhất local Z=33 cm, cao hơn waterline 25 cm là 8 cm.
- Sàn bám hình thân, dốc lên tại hai đầu; mép chồng vào thành 8 mm. Giữ keel, pivot và bounds.
- `living_manifest.json` không có bộ gỗ. Dùng bộ `City_wood_floor` hiện có trong `source_catalog.json`:
  `Textures/wood_floor/{color,normal,roughness}.jpg`, nguồn Poly Haven `wood_floor`, CC0.
- UV theo kích thước thật, scale 1,8 m; gỗ không dùng swatch nâu hoặc vertex color tint.
- `--asset Rowboat` build/render riêng, giữ đủ năm ID trong manifest và năm model trong blend.
- Bản generator đã đồng bộ tại `Assets/City/MetroDetails/Sources/Generator/`.

## Kiểm chứng

- Rowboat: **4.120 tris / budget 5.000**, ba material slots; UV0 12.360 loops, 0 UV triangle suy biến.
- Sàn riêng là closed manifold, volume dương; raycast 7.421 điểm trên footprint nước đều được sàn che.
- Bounds cm và FBX roundtrip: min `[-208.8749,-90.5,0]`, max `[208.8749,90.5,88.7]`.
- Bốn FBX FireEngine, PassengerTrain, Helicopter, CivilianPlane byte/hash giữ nguyên so với trước sửa.
- Toàn bộ `meshes`/`sourceFiles` manifest hash PASS; texture sRGB/Non-Color đúng, không sửa texture.
- Python compile PASS; `git diff --check` trên file sở hữu PASS.
- Tám PNG mới 800x600, 20 samples, Cycles CPU hai thread: `Rowboat_DryFloor_000.png` tới `_315.png`.
- Đã mở xem đủ tám ảnh: sàn liền, silhouette giữ nguyên; gỗ đọc được grain và độ nhám.
- Các mặt hull vốn có vẫn mang faceting nhẹ, bench ends vốn có vẫn lộ qua bên thành.
  Không sửa các chi tiết đó trong vòng sửa sàn này.

Evidence tại `Saved/QA/CityMetroAssets/`:

- `rowboat_dry_floor_build_audit.json`: UV, tris, material slots và FBX roundtrip.
- `rowboat_dry_floor_geometry_audit.json`: sàn kín, coverage, bounds, material, hash.
- `rowboat_dry_floor_render_audit.json`: tám view, hash PNG, camera, CPU/thread.
- `dry_floor_before_hashes.json`: baseline hash năm FBX.
- `audit_rowboat_dry_floor.py`: kiểm tra độc lập blend đã lưu.

## Chạy lại

```powershell
$blenderExe = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
& $blenderExe -b --factory-startup --threads 2 --python-exit-code 1 `
    -P Tools/CityAssets/metro_build.py -- --asset Rowboat
& $blenderExe -b --factory-startup --threads 2 --python-exit-code 1 `
    -P Tools/CityAssets/metro_render.py -- --asset Rowboat
& $blenderExe -b --factory-startup --threads 2 --python-exit-code 1 `
    -P Saved/QA/CityMetroAssets/audit_rowboat_dry_floor.py
```

## Tích hợp Unreal do agent chính kiểm

- Reimport PASS: 4.120 tam giác Nanite/fallback 1.830, ba LOD/slot, một collision, bounds sai số dưới 1 cm.
- Importer đã sửa binding theo tên slot vì Unreal giữ thứ tự cũ; sáu regression mapping PASS.
- Wrapper input sau sửa đọc UTC PowerShell 7 PASS exit 0, bảy regression timestamp PASS.
  Chèo 79,08 cm, phanh dừng, xuống bến khô/capsule nguyên, từ chối xuống giữa biển.
- Chụp riêng thuyền đủ năm góc native 1080p/100%, shadow async diagnostic; mở xem đủ contact.
  Sàn khô và vật liệu gỗ đúng, không bị bến/người chơi che sau sửa camera. Không đổi actor/draught/map.
- Evidence: `Saved/QA/CityRowboatCheck/Report.json`, `rowboat_dry_floor_import.json`,
  `Saved/QA/CityPlacement_metro_Rowboat_NaniteShadowAsyncOn/`.
- EXE City6800 còn mesh cũ; chưa nghiệm thu package mới/chuyến biển dài/90 FPS.
