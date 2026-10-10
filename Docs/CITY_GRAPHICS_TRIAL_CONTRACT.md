# Gameplay đồ họa: ba thử nghiệm có đối chứng

Repo D:\GAME\ANANTA, UE 5.8.3. Main đang chạy Collision/13 gate, không mở thêm Unreal.
Đọc Docs/CITY_GPU_COST_AUDIT.md và Source/ANANTA/Private/QA/CityGraphicsObservation.cpp.
Không sửa DefaultScalability/DefaultEngine, C++, map, asset, nhân vật hoặc save thường.

## API dùng chung

- Tools/Build/Test-CityMaxGraphics.ps1 giữ mọi tham số/mode cũ.
- Thêm QualityTrial: Base (mặc định), GI32, Reflections4, VsmBias0.
- Non-Base chỉ cho ExecutablePath, Diagnostic=None, ProfileRender=false; gameplay vài phút, không benchmark.
- Base 24/2/-1.5; GI32=32/2/-1.5; Reflections4=24/4/-1.5; VsmBias0=24/2/0.
  Ba giá trị theo thứ tự: ScreenProbeGather.DownsampleFactor, Reflections.DownsampleFactor,
  Shadow.Virtual.ResolutionLodBiasDirectional. Mỗi variant chỉ đổi một cvar qua ForceDPCVars.
- Thư mục QA/log biến thể riêng, không ghi đè baseline. Giữ Base/Diagnostic directory legacy.
- FrameTimes.csv và RenderConfig.txt do game ghi tại Saved/QA/CityMaxGraphics, phải copy sang variant.
- Chạy SummarizeCityFrameTimes.py sau thành công, giữ mọi frame và stable90Accepted=false.

## Provenance và save

- Trial.json schemaVersion=1, qualityTrial, diagnostic, profileRender, runtimeKind, startedUtc,
  completedUtc, gameplayPassed, artifactFingerprint, qaSlotsReset, qaSlotsRestored.
- Packaged artifactFingerprint gồm SHA256 EXE và danh sách tên tương đối/SHA256 của mọi pak/utoc/ucas.
  Tính trước game, không suy map/quality packaged từ source worktree; không nhận package thiếu container.
- Editor Base được giữ behavior cũ; comparator chỉ nhận Packaged với fingerprint giống hệt nhau.
- Xác định SavedRoot đúng như runner cũ. Hai tệp duy nhất được backup/reset/restore:
  Saved/SaveGames/ANANTA_City_QA.sav và ANANTA_City_QA_Backup.sav.
- Reset cùng trạng thái sạch trước mỗi run, restore chính xác trong finally, kể cả game lỗi.
  Nếu trước run tệp không tồn tại, xóa tệp QA mới sau run. Không glob/xóa save thường.
- Trước Remove/Move phải kiểm path đã resolve bên trong SavedRoot/SaveGames và basename đúng hai tên.
- Không tác động save/cấu hình cá nhân. Không chạy game trong lúc main đang chạy Unreal.

## Hàm Python và định dạng so sánh

- CityGraphicsTrialData.py: load_run(directory: pathlib.Path) -> dict.
- CompareCityGraphicsTrials.py: compare_runs(baseline: pathlib.Path, candidates: list[Path]) -> dict.
- CLI: python Tools/QA/CompareCityGraphicsTrials.py BASE CANDIDATE... --output OUTPUT.json.
- Input mỗi thư mục: Trial.json, FrameTimes.csv, RenderConfig.txt, Report.txt từ journey.
- Chỉ Base làm baseline; ứng viên non-Base độc nhất. Reject profile/diagnostic, fingerprint khác,
  slots không reset/restore, gameplay thiếu marker, thời gian tệp ngoài run, CSV rỗng/không hợp lệ.
- RenderConfig thực phải output=1920x1080, r.ScreenPercentage=100, VSync=0, t.MaxFPS=90,
  mười sg quality=3, HWRT=0, directional/local ray=4, samples directional=4, VSM=1,
  frustum/HZB=1, TSR history=100; đọc giá trị từ file, không lấy từ INI chỉ định.
- Expected GI/reflection/bias theo variant; mọi cvar còn lại giống baseline.
- Mọi wall_ms hữu hạn >0; counter hữu hạn >=0; GPU trung bình >0; elapsed tăng đều.
- Tính lại số frame/thời gian/mean/p95/max/slow frame/CPU-GPU từ CSV, không tin Summary cũ.
- Kết quả có từng variant và delta FPS/GPU/render/p95 so baseline, includesAllFrames=true,
  visualAccepted=false, stable90Accepted=false; ghi rõ cần xem ảnh và không chứng minh 90 FPS.

## Tệp độc quyền

- Tools/Build/Test-CityMaxGraphics.ps1
- NEW Tools/Build/CityGraphicsTrialEvidence.ps1 nếu cần để mỗi tệp <300 dòng.
- NEW Tools/QA/CityGraphicsTrialData.py
- NEW Tools/QA/CompareCityGraphicsTrials.py
- NEW Tools/QA/TestCityGraphicsTrialComparison.py

Done: PS AST parse, py_compile, git diff --check, <300 dòng/<120 ký tự.
Self-test bằng tempfile: baseline+ba variant hợp lệ; reject fingerprint khác/cvar sai/CSV lỗi/
profile/diagnostic/save không phục hồi. Không lấy số giả làm bằng chứng gameplay/hiệu năng.
Không mở/build Unreal, download, sửa ngoài tệp được giao, commit/push hay tạo agent con.
Báo một lần tối đa 15 dòng: tệp, kiểm chứng, vấn đề còn mở; runtime sẽ do main chạy sau package.
