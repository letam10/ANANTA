# ANANTA Master Roadmap

Ngày cập nhật: 2026-10-15
Checkout: `D:\GAME\ANANTA`
Engine: Unreal Engine 5.8.3
Nhánh làm việc: `codex/coastal-interiors-20261014`

Tài liệu này là roadmap duy nhất của chương trình ANANTA. Trạng thái từng chat,
lệnh và evidence mới nằm trong [ANANTA_CURRENT_HANDOFF.md](ANANTA_CURRENT_HANDOFF.md).
[COASTAL_FINAL_HANDOFF_20261015.md](COASTAL_FINAL_HANDOFF_20261015.md) chỉ là
snapshot lịch sử của tranche coastal và không được sửa để biến thành evidence mới.
Các handoff cũ khác là tài liệu lịch sử.

## Mục tiêu chương trình

- Thành phố nguyên bản, bán thực tế, có nhiều building vào được và có tương tác.
- Model/prop có pivot, hướng trục, vật liệu, LOD, collision và provenance rõ ràng.
- Model mới hoặc model sửa có review 8 hướng.
- Placement quan trọng có review 5 góc từ transform và transformed bounds.
- Thành phố có biển rộng nhưng khóa biên, đường phố, phương tiện, rail hai chiều,
  ga, sân bay, nhà hàng, khách sạn, opera, cinema, cafe, bar, công viên, hồ bơi,
  helipad, factory, police/fire/clinic và prop nhỏ trong nhà.
- Tối ưu và đo riêng cho RTX 3050 và RTX 4060 Laptop.
- Chỉ gọi một gate đạt khi có lệnh, exit code và evidence mới phù hợp với gate đó.

## Bất biến

- Không sửa, stage, xóa hoặc commit `AGENTS.md`; giữ mọi dirty map/ExternalActors có sẵn.
- Headless là mặc định. Build, static parse, Blender render và NullRHI không thay thế
  headed visual, material graph, GPU/VRAM, frame-time hoặc 60 FPS proof.
- Giữ quy ước `+X` là hướng tiến, `+Z` là hướng lên. Yaw, wheel/vehicle/rail và
  chuyển động phải suy ra từ transform; placement sát tường phải kiểm bằng bounds sau
  yaw/scale.
- Asset mới phải có nguồn/licence, pivot, bounds, LOD, triangle budget và collision policy.
- Không mở rộng map hoặc làm pha sau khi gate pha hiện tại chưa đạt.
- Không force-push, reset mù hoặc tự merge remote commit chưa được đọc.

## P0 — Khóa baseline, Git và ngữ cảnh

**Mục đích:** khóa một baseline có thể truy nguyên trước khi sửa nội dung.

**Gate:**

- Có local HEAD, branch, dirty-state và remote ref đã đối chiếu.
- Roadmap và handoff ghi rõ DONE, PARTIAL, UNVERIFIED và BLOCKED.
- `Validate-ANANTA.ps1` và `git diff --check` có kết quả mới.
- Không claim runtime/FPS từ source gate.

P0 ngày 2026-10-15 đã đạt sau khi đọc parent history và fast-forward an toàn từ
`dcc05d8...` lên remote merge `9057c9...`. `AGENTS.md` không nằm trong diff và hai Docs P0 không nằm trên remote nên được giữ nguyên; không có reset mù hoặc force-push.

## P1 — Asset, prop nhỏ và geometry pipeline

**Phạm vi:** source/generator/import-readback/review/placement; chưa mở rộng toàn map.

- Giữ 72 model đã đạt gate; chỉ sửa lỗi có evidence hoặc thêm nhóm còn thiếu.
- Ưu tiên sidewalk, sign, railing, monument, playground, traffic light, factory,
  police/fire/ambulance, station, airport, boat, restaurant, hotel, opera, cinema,
  cafe, park, pool, helipad, highway, beach và prop nội thất nhỏ.
- Mỗi model ghi AssetId, category, source, licence, pivot, `+X`, bounds,
  LOD0/1/2, triangle count, material slots và collision policy.
- Sinh/review 8 yaw; placement review dùng 5 camera transform và transformed bounds.
- Import Unreal phải đọc lại dimensions, LOD, material và collision.
- Small prop không tick và collision=false nếu không cần tương tác.

**Gate:** generator/audit, 8-view coverage, 5-view placement, transformed-bounds không
lỗi, import readback, `py_compile`/build cần thiết đạt. Chưa claim headed visual hoặc FPS.

## P2 — Hero slice, material graph và headed visual

**Phạm vi:** một hero slice 200–300 m, không nhân rộng district trước khi hình ảnh đạt.

- Readback graph/output thật cho BaseColor, Roughness, Normal và Emissive.
- Dựng nền/đường liên tục, mặt dựng có chiều sâu, ánh sáng, exposure và camera cố định.
- Capture headed chỉ trong gate được phép; lưu preset, resolution, renderer và ảnh mới.

**Gate:** ảnh day/blue-hour đọc được chất liệu, bóng, phản xạ, scale người; graph output
không null; không dùng ảnh Blender/editor-only hoặc NullRHI làm visual acceptance.

## P3 — Streaming và mở rộng thành phố

**Phạm vi:** chỉ sau P2.

- Chuyển persistent map sang World Partition, OFPA và runtime hash phù hợp.
- Tách Data Layers cho day/night, traffic và mission; dựng HLOD/PCG có seed cố định.
- Đo streaming source, loading range, HLOD identity và boundary khi đi qua district.

**Gate:** không gap/pop-in nghiêm trọng; có readback World Partition/HLOD/Data Layers/PCG
và evidence mới ở ranh giới district.

## P4 — Gameplay và mobility

**Phạm vi:** gameplay thật sau khi geometry/streaming ổn.

- Hoàn thiện aircraft control, rowing animation và railway signal control.
- Hoàn thiện interaction state, save/load, economy và nhiệm vụ vertical slice.
- Kiểm tra input, collision cảm nhận, boarding, respawn, persistence và UI trong headed/PIE
  khi prompt pha cho phép.

**Gate:** test runtime phù hợp có log/evidence mới; không suy ra từ C++ compile hoặc NullRHI.

## P5 — Performance và 60 FPS

- Tách tier RTX 3050 và RTX 4060 Laptop, ghi preset/resolution/renderer.
- Thu headed `stat unit`, `stat gpu`, `stat sceneRendering`, `stat initviews`,
  `stat levels`, VRAM và frame-time percentile ở downtown/interior/traffic.
- Ngân sách 60 FPS là `1000/60 = 16.667 ms`; đây chỉ là mục tiêu cho tới khi số đo
  headed mới đạt.

**Gate:** số đo GPU/CPU/VRAM và percentile đạt ngưỡng đã ghi cho từng tier, không hitch
shader/streaming, có log mới. Không dùng target cấu hình hoặc NullRHI để tuyên bố 60 FPS.

## P6 — AAA toàn map và closure

- Review visual toàn map, material consistency, lighting, collision, navigation,
  density, audio và regression sau các pha trước.
- Lặp lại source/import/runtime/performance gates; chốt provenance và package inventory.
- Chỉ đóng chương trình khi mọi mục UNVERIFIED/BLOCKED đã có evidence hoặc được ghi rõ
  quyết định loại khỏi scope.

## Baseline đã xác nhận

- Local HEAD sau baseline sync: `9057c9beecd2ef1e1cc433eb4f672b9130343e79`.
- Remote ref sau fetch: `9057c9beecd2ef1e1cc433eb4f672b9130343e79`.
- Remote commit là merge `main` vào branch, parents là `dcc05d8fc3...` và
  `77c9ba76fe67834730d3989781c4bea6e51575f3`.
- Fetch exit 0; `git merge-base --is-ancestor` và `git merge-tree` không có conflict;
  `git merge --ff-only origin/codex/coastal-interiors-20261014` exit 0; không reset mù hoặc force-push.
- Foundation validation exit 0: BridgeDescriptor và WorkflowConfig đúng, không thiếu file/plugin.
- Tranche coastal: 72 FBX/model, `max triangles=9678`, model 8-view coverage;
  36 review unit/180 room placement views; 23 building, 6745 instance và 816 HISM;
  r15 bounded NullRHI `COASTAL_QA_COMPLETE failures=0 views=122`.
- Các con số trên không chứng minh headed visual/material/FPS.

## Evidence hygiene

- `Saved/Upgrade/ModelViews/coverage.json` hiện có 72 entries.
- `Saved/Upgrade/coastal-quality-report.json` là audit cũ với `manifest_models=65`;
  không dùng nó làm proof mới của 72 model.
- `Saved/Upgrade/city-layout.json` là source layout cũ có 195 review views; room
  geometry proof hiện hành được tách ở coverage 180 views. Không trộn hai số này.
- Hai warning commandlet còn được giữ trong handoff: UE-MCP Slate startup và API
  `save_current_level` deprecated; chúng không được ghi thành content PASS.

## Thứ tự chat

1. P0 đã khóa baseline `9057c9...`; bắt đầu P1 bằng audit source/readback/review, chưa mở rộng map.
2. Chạy P1 theo một nhóm asset/placement có contract và evidence riêng.
3. Chỉ chuyển P2, P3, P4, P5, P6 khi gate pha trước đạt.
4. Mỗi chat cập nhật roadmap này và handoff hiện hành; không tạo roadmap cạnh tranh.