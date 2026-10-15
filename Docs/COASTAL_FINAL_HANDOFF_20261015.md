# ANANTA Coastal City — final handoff and report

Ngày chốt: 2026-10-15  
Nhánh: `codex/coastal-interiors-20261014`  
Commit nền trước báo cáo: `93a8d5e707` (`Expand coastal interior interactions`)

## 1. Phạm vi đã hoàn thành và có bằng chứng

- Pipeline model hiện có 72 model low-poly, pivot nền và hướng đọc nhất quán; generator đã đạt `COASTAL_MODELS_OK 72 models; max triangles=9678`.
- Review model đạt 8 hướng/model: `MODEL_VIEW_COVERAGE_OK 72 models x 8 views`; compose model đạt 576 view.
- Review hình học phòng đạt 5 góc/unit cho 36 review unit, tổng 180 view. Đây là kiểm tra placement/bounds bằng Blender, không phải gameplay headed.
- CoastalCity có 23 building vào được, bãi biển/nước mở rộng, biên collision chặn rìa, sân ga hai ray, sân bay, công viên, nhà hàng/cafe/bar, police/fire/clinic/factory/cinema/opera/arcade/hotel/home/beauty.
- Bộ nội thất và prop nhỏ đã có 72 model, gồm nhóm trang điểm, đồ chơi, dụng cụ bếp, đồ phòng tắm, đồ phòng khách, sân bay, đường phố và OceanFoam.
- Tương tác Kind=5 đã mở rộng ở home/hotel/beauty/cafe/restaurant/bar/cinema/opera/factory/arcade. Các placement giữ model, yaw, scale, bounds và lối đi đã review; prop nhỏ không bật tick riêng.
- Runtime đã có resident schedule nhẹ, 72 traffic signal actor tại 36 giao lộ, hai train chạy ngược chiều, xe cảnh sát/cứu hỏa/cứu thương, rowboat và boundary biển.
- OceanFoam là lớp visual nhẹ, collision=false và gom HISM; nước vẫn là mặt opaque có normal động, không phải mô phỏng buoyancy.

## 2. Kiểm chứng cuối

Lệnh foundation verify:\n
```powershell
& .\\Tools\\Build\\Validate-ANANTA.ps1
```

Kết quả mới: `ANANTA foundation validation passed.`; `BridgeDescriptor: True`, `WorkflowConfig: True`, không thiếu plugin/file.

Map commandlet dùng project path tuyệt đối:\n
```powershell
& 'C:\\Program Files\\Epic Games\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe' `
  'D:\\GAME\\ANANTA\\ANANTA.uproject' -run=pythonscript `
  -script='D:\\GAME\\ANANTA\\Tools\\Upgrade\\BuildCoastalCity.py' `
  -NullRHI -unattended -NoSplash
```

Evidence mới trong `Saved/Upgrade/build-coastal-interactive.log`:

- `MapCheck: Map check complete: 0 Error(s), 0 Warning(s)`.
- `COASTAL_MAP_OK 23 enterable buildings, 6745 instances / 816 HISM batches`.
- Python script exit 0; hai cảnh báo còn lại là UE-MCP Slate startup và API `save_current_level` deprecated.

Quick gameplay bounded:\n
```powershell
& 'C:\\Program Files\\Epic Games\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe' `
  'D:\\GAME\\ANANTA\\ANANTA.uproject' -game -CoastalQA -NullRHI `
  -unattended -NoSound
```

Evidence mới trong `Saved/Upgrade/runtime-r15-interactive.log`:

- Profile: `High Lumen, TSR 900p/1080p, target 16.667 ms`.
- PASS: cửa 23 building, 23 service, 23 NPC, 23 NPC schedule, micro props, traffic signals, train two-way, ocean boundary, đi bộ, xe và xuồng.
- Tổng kết: `COASTAL_QA_COMPLETE failures=0 views=122`.
- Đây là bounded NullRHI QA, không phải benchmark/soak và không đo headed GPU.

## 3. Dọn dẹp và trạng thái Git

- Không còn file `.tmp` dưới `Saved` sau commandlet/capture.
- Các material `.uasset` bị Unreal serialize lại trong commandlet đã được khôi phục vì không thuộc thay đổi gameplay của tranche.
- `AGENTS.md` có thay đổi dirty từ trước, không được stage, sửa hoặc xóa.
- Trạng thái trước khi ghi báo cáo chỉ còn `AGENTS.md` dirty; các source/asset của tranche trước đã được push ở `93a8d5e707`.

## 4. Visual/FPS và các giới hạn phải giữ nguyên trong bàn giao

- Capture editor-only 195 ảnh đã chạy thành công, nhưng pixel variance của toàn bộ ảnh dưới ngưỡng compose. Vì vậy ảnh đó không được coi là visual acceptance; không ghi nhận headed material/lighting proof.
- Chưa có GPU/VRAM/frame-time percentile trên headed player, nên chưa tuyên bố đạt 60 FPS. `16.667 ms` chỉ là ngân sách cấu hình.
- CoastalCity vẫn là persistent level thường; chưa chuyển World Partition/HLOD/Data Layers/PCG district.
- Xe và thuyền còn kinematic; chưa có điều khiển máy bay, animation chèo tay, signal railway control, âm thanh tàu, economy/save đầy đủ hoặc nhiệm vụ vertical slice.
- Visual toàn map chưa đạt photoreal/AAA; 8-view model và 5-view room review chứng minh hình học/placement, không thay thế người chơi tự do trên headed build.

## 5. Kế hoạch tiếp tục sau bàn giao

1. Sửa capture/editor lighting để tạo ảnh có variance và visual acceptance thật.
2. Readback material graph/output và dựng hero slice 200–300 m.
3. Chuyển streaming theo World Partition/HLOD/Data Layers sau khi hero slice đạt gate.
4. Chạy headed capture có preset, resolution, GPU/VRAM và frame-time percentile; chỉ khi số liệu đạt mới tuyên bố 60 FPS.
5. Mở rộng save/economy, aircraft/rowing, railway signals và interaction state.

## 6. Kết luận chốt

Tranche coastal/interiors đã được kiểm chứng bounded và sẵn sàng bàn giao với evidence/log nêu trên. Dự án chưa đạt toàn bộ yêu cầu AAA/60 FPS headed; các phần chưa đạt được ghi rõ để không nhầm giữa logic QA và acceptance người chơi.
