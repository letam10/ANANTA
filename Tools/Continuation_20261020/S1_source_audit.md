# S1 — audit nguồn streaming City và Coastal, 2026-10-20

**Kết luận: S1 PARTIAL; chưa chạy runtime/cell readback mới.** Audit chỉ đọc source, cấu hình, cấu trúc Content và receipt có sẵn. Không chạy engine, test, build hay benchmark; không sửa map/source/config. Chỉ tạo báo cáo này. Các đường dẫn dưới đây tương đối với `D:/GAME/ANANTA/`.

## Identity và phạm vi của từng map

| Mục | ANANTA_City | ANANTA_CoastalCity |
| --- | --- | --- |
| Map | `Content/ANANTA/Maps/ANANTA_City.umap` | `Content/ANANTA/Maps/ANANTA_CoastalCity.umap` |
| Nguồn tạo | `Tools/Editor/BuildCityMap.py`; mở rộng qua `ApplyCityExpansion.py` và `CityExpansionLayout.py` | `Tools/Upgrade/BuildCoastalCity.py` + các module `coastal_*.py` |
| Chế độ chơi | `ANANTACityGameMode` được gán trong builder | `CoastalGameMode` được gán trong builder; đây là GameDefaultMap trong `Config/DefaultEngine.ini:23` |
| WP/OFPA evidence | Có conversion command, cấu hình spatial hash, và thư mục external actors thực tế | Builder dùng `EditorLevelLibrary.new_level`; không thấy bước conversion/WP hay cấu hình spatial hash dành cho Coastal |
| External actors trên đĩa | `Content/__ExternalActors__/ANANTA/Maps/ANANTA_City/`: 26.763 file tại thời điểm audit | Không có thư mục tên CoastalCity cùng cấp tại thời điểm audit |

Số lượng file external actor là kiểm kê filesystem, không phải native descriptor/cell readback. Không có thư mục external actor Coastal không đủ để chứng minh mọi thuộc tính của UWorld; cần đọc map bằng engine trước khi quyết định chuyển đổi. Không chạy lại builder Coastal trong audit: builder xóa actor `Coast_` trước khi tái tạo nên đây là mutation rộng, không phải phép kiểm tra.

## City: WP, loading range, HLOD và boundary

- `Tools/Build/Convert-CityPartition.ps1` chỉ đích danh `/Game/ANANTA/Maps/ANANTA_City`, dùng `WorldPartitionConvertCommandlet`; có `-ReportOnly`. Command sử dụng NullRHI nên receipt của nó chỉ là gate chuyển đổi, không có ý nghĩa FPS.
- `Content/ANANTA/Maps/ANANTA_City.ini`: editor hash `WorldPartitionEditorSpatialHash`, runtime hash `WorldPartitionRuntimeSpatialHash`, `bConvertActorsNotReferencedByLevelScript=True`, default layer `/Game/ANANTA/City/HLOD/City_HLOD.City_HLOD`. Grid `City`: `CellSize=12800` cm, `LoadingRange=25600` cm, `bBlockOnSlowStreaming=True`. Đây là ý định cấu hình, chưa phải readback runtime grid hiện tại.
- `Tools/Editor/CreateCityHLOD.py` hiện tạo **INSTANCING**, cell 25.600 cm, loading range 120.000 cm, spatially loaded; Nanite được phép, filtering NONE. Không nhầm loading range HLOD 1.200 m với source grid 256 m.
- `Tools/Build/Build-CityHLOD.ps1` kiểm identity apply/readback trước và sau build, log có runId, force `-RebuildHLODs`, receipt ban đầu BUILDING rồi PASS khi log validator thành công. `-BuildSingleHLOD` xuất receipt sample riêng và không được thay full-map gate. Không chạy công cụ này trong audit.
- `Tools/Editor/CityHLODIdentity.py` cố định identity expanded: width `6788.2250993908565` m, 85.386 source groups, 1.660.761 source instances; so SHA256 của `Saved/QA/CityExpansionApplied.json` và `CityMobilityMapReadback.json`. Validator kiểm khoảng thời gian log, hash log, danh sách label duy nhất, và parity GUID giữa descriptor/loaded actor. Tên map/actor đơn thuần không đủ.
- `Tools/Editor/VerifyCityHLODInstances.py` đọc actual instanced geometry/materials và gọi `unreal.CityEditorTools.hlod_source_actor_references`. Bridge native ở `Source/ANANTA/Private/QA/CityEditorHLODReferences.cpp` đọc `UWorldPartitionHLODSourceActorsFromCell`. Boundary exclusion so actual source path/GUID với 4 collider, không suy luận qua proxy mesh.
- `Tools/Editor/VerifyCityBoundaries.py` và `Source/ANANTA/Private/QA/CityEditorBoundaryAudit.cpp` thực hiện capsule sweep persisted collider. `InspectCityBoundaryLoading.py` là phép đối chiếu persisted region load với direct actor load; không lưu map.

### Receipt City lịch sử đã đọc

1. `Saved/QA/CityHLODBuildReceipt.json`: full PASS, 3.557 built actors, run `9a4ba05837584d998162a3092dd72dba`, từ `2026-10-10T03:26:45.5588085Z` đến `03:44:18.7614769Z`. Identity là expanded 6,788 km ở trên. Đây là receipt cũ, chưa được thực thi lại hoặc đối chiếu hash toàn bộ map hiện tại trong audit.
2. `Saved/QA/CityHLODInstances.json`: full PASS, 3.557 descriptors/actors, 1.619.348 HLOD instances; boundary exclusion checked 3.557 HLOD, 83.212 source references, không violation/limitation. Nó tự ghi `fpsAccepted=false`, `renderedArtAccepted=false`. Hai giá trị này phải được giữ nguyên khi trích dẫn.
3. `Saved/QA/CityHLODReadback.json` là snapshot **2026-10-08**, 152 HLOD, thuộc trạng thái trước hơn. `CityHLODSettings.json` cùng ngày còn ghi **MESH_SIMPLIFY**, trong khi source hiện dùng INSTANCING và receipt expanded 2026-10-10 đã khác. Không dùng các file cũ này làm bằng chứng cho graph/layer/cell hiện tại.
4. `Saved/QA/CityWorldBoundaries.json`: 14 sweep samples, 4 loaded collider instances, extent `339411.25496954285` cm, capsule radius 38/half-height 92 cm; `runtimeAccepted=false`. Scope chỉ là sweep sau mesh compilation, không chứng minh người chơi hoặc phương tiện không xuyên rìa trong gameplay mới.

Map City trên đĩa có modified time 2026-10-15, muộn hơn receipt HLOD 2026-10-10. Chỉ mtime không tự chứng minh HLOD lỗi, nhưng receipt cũ không tự động xác nhận mọi thay đổi map/actor sau đó. Fresh identity/hash/readback cần có trước khi kết luận.

## Coastal: batching, biển và rìa map

- `Tools/Upgrade/coastal_scene.py`: batch HISM theo tile 64 m, mesh/material/collision/cull band. `spawn` đổi mét sang centimetre. `instance` đặt start cull `cull_band * 100` cm và end cull `cull_band * 120` cm; đây là per-component distance culling, **không phải** WP/HLOD hoặc loading range của cell. Culling band 0 giữ batch không có khoảng cull hữu hạn.
- `Tools/Upgrade/coastal_landscape.py`: mặt nước đặt ở `(1210,0,0)` m, kích thước `(2000,2000,1)`, không collision. Bốn hidden StaticMeshActor `Coast_Boundary_0..3` dùng BlockAll: x=-225 và x=720 m; y=±270 m. Các wall có bề dày 2 m nên nên readback bounds để xác định mặt trong thực tế, không coi tọa độ tâm là giới hạn chạm cuối cùng.
- Builder dùng bãi biển nghiêng `atan2(2,30)` và kéo mặt biển vượt boundary để tránh hình hồ. Foam hiện có các model `OceanFoam`; sự tồn tại model không xác nhận sóng/foam native W3 đã đạt.
- `Source/ANANTA/Private/CoastalQAGameplay.cpp:142` chỉ có `ocean_boundary_blocks` bằng visibility line trace từ x=71500 đến72500 cm, z=1000 cm. Đây là một ray phía đông, không phải capsule/boat route thử đủ cạnh/góc; cùng fixture có `SetActorLocation` cho chuẩn bị tương tác nên không dùng nó làm hành trình streaming input thường.
- Không thấy pipeline HLOD identity, Coastal cell receipt, hoặc normal-input district streaming journey riêng trong các nguồn `Source/ANANTA`, `Tools/Editor`, `Tools/Upgrade`, `Config` đã rà. Không suy ra chúng từ City hoặc từ report material/import Coastal.

## Data Layers và PCG: khoảng trống chung

Tìm `DataLayer`, `data_layer`, `PCGComponent`, `PCGGraph` trong source/tool/config không tìm thấy thiết lập hay readback day/night/traffic/mission. Roadmap `Docs/ANANTA_MASTER_ROADMAP.md:125` yêu cầu chúng; một mục tiêu trong tài liệu không phải asset đã author. Cần đọc native Data Layer asset/instance và trạng thái runtime riêng ở từng map trước khi thiết kế thay đổi.

`ANANTA.uproject` bật PCG và `Tools/Editor/GenerateFoundation.py` tạo đường dẫn `/Game/ANANTA/Environment/PCG`; không thấy source tạo graph/component hoặc native PCG seed readback. City có procedural layout Python xác định: `Tools/Editor/CityLayout.py:14` seed71026; `CityExpansionData.py:10` seed81026; `CityExpansionLayout.py:111` dùng `random.Random(SEED + int(cx)*31 + int(cy))` theo từng block. Đây là deterministic source generation, **không phải PCG graph runtime**. Coastal builder dùng vòng lặp/placement cố định, chưa có PCG seed contract riêng.

## Hành trình qua district bằng input thường

City có triển khai phù hợp để tái sử dụng làm nền cho kiểm ngắn: `Source/ANANTA/Private/QA/CityStreamingJourney.cpp`, `CityStreamingJourneyRoute.cpp`, `CityStreamingJourneyEvidence.cpp`. Bật `-CityStreamingCheck -CityQASlot`; guard chỉ City game world, QA save tươi, on-foot, không driven vehicle; từ chối NullRHI/benchmark và các QA đồng thời. Input đi qua `PlayerController.InputKey` W/LeftShift, hướng camera qua `SetControlRotation`, không teleport/speed override. Route hiện dài khoảng1.707m, ngân sách300 giây; không phù hợp yêu cầu route ngắn nếu chạy nguyên trạng mà không thu hẹp scope có chủ đích.

Endpoint yêu cầu `UWorldPartitionSubsystem.IsStreamingCompleted()`, đứng yên/on ground, camera đúngyaw, settle2 giây; lưu bốn ảnh forward/reverse ở north/northeast. Mỗi frame trace sàn và kiểm displacement/speed. `Saved/QA/CityStreamingJourney/Report.txt` modified 2026-10-08 ghi success1,277.788giây, path170840.210cm,4settledviews,30.866groundchecks; max wall gap686.948ms. Nó tự ghi `stable_60fps_proven=false`, `perfect_culling_proven=false`, `visual_acceptance_proven=false`. Không chạy lại; không đánh giá lại ảnh cũ trong audit; không gọi đây là 60FPS hoặc fresh S1 PASS.

Coastal cần hành trình ngắn bằng input bình thường ở chính Coastal, xác nhận identity/collision/streaming mode trước. Không dùng API-fixture hay teleport làm route evidence.

## Gate tiếp theo trước sửa hoặc mở rộng district

1. Đọc native identity của **cả hai map**: package/hash, WP mode, external packaging, runtime hash/grids/cell/loading range, actor descriptors. Ghi rõ trường không áp dụng ở map non-WP. Chưa chuyển đổi Coastal trong bước audit.
2. City: readback HLOD layer/builder hiện tại và full descriptor/loaded GUID parity gắn với apply/readback/hash mới; kiểm riêng boundary source exclusion. Chỉ rebuild nếu identity hoặc readback chỉ ra cần thiết; không khởi chạy full rebuild nặng chỉ vì receipt cũ.
3. Đọc Data Layer assets/instances/runtime states và PCG graph/component/seed từng map; nếu chưa tồn tại, đánh dấu NOT AUTHORED và đề xuất tranche nhỏ, không báo PASS từ plugin enable.
4. Review route ngắn có mặt đường/camera ngang tầm người, chạy normal input ở district có identity đúng; thu cell loading/unloading, cảnh thuận/ngược ở điểm chuyển, collision và gap/pop-in. Giữ save QA tách khỏi save người dùng. Không tự xóa ảnh/log cũ; dùng thư mục run mới.
5. Boundary: thử đủ cạnh/góc với capsule và boat/vehicle thích hợp; collision phải tách shader và có bounds thực sau yaw/scale. Một ray trace không đủ.
6. Gắn S1 acceptance với ảnh/runtime/cell evidence mới. Các số wall-frame cũ, build/NullRHI, HISM culling hoặc target config không chứng minh F1~60FPS; F1 vẫn yêu cầu headed CPU/GPU/stat/VRAM/resolution/scalability riêng.

**Đã kiểm:** đọc nguồn và receipt có sẵn, kiểm kê filesystem external actors, đối chiếu timestamp/identity/scope báo cáo. **Chưa kiểm:** engine readback mới, actual cell state, runtime Data Layers/PCG, ảnh gap/pop-in mới, normal-input Coastal route, boundary gameplay đủ cạnh/góc, headed performance. Không có thay đổi Unreal nào trong audit này.
