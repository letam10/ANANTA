# ANANTA Coastal City — Windows Shipping

Giải nén toàn bộ ZIP vào một thư mục rồi mở `Windows/ANANTA.exe`.
Giữ nguyên các thư mục `ANANTA` và `Engine` cạnh launcher; không chép riêng file EXE.
Nếu thiếu Microsoft Visual C++ Runtime, dùng bộ cài trong
`Engine/Extras/Redist/en-us/UEPrereqSetup_x64.exe` (nếu máy cần).

Điều khiển: WASD di chuyển, chuột xoay camera, Shift chạy, Space nhảy, E tương tác.
E mở cửa, dùng bảng dịch vụ, lên xe/thuyền; khi đang lái, E dừng và xuống ở vị trí an toàn.
W/S tiến/lùi, A/D rẽ. Bảng thang máy dẫn lên sân thượng/hồ bơi tại các khách sạn.

Bản ngày 14/10/2026 mở map `ANANTA_CoastalCity`: 55 model trong bộ kit,
23 địa điểm vào được, 36 phòng được phân khu ở 9 tòa nhà.
Đồ họa mặc định dùng High, Lumen software, TSR 83,33%, giới hạn 60 FPS.
Giới hạn 60 FPS là cấu hình mục tiêu, không phải kết quả benchmark.

Theo yêu cầu, bản này chỉ được build/cook/đóng gói, **chưa mở chạy game thật**.
Ảnh kiểm bố trí mới dùng Blender với cùng mesh/tọa độ map; ánh sáng và gameplay
trong bản Windows vẫn cần người dùng kiểm tra. NPC, xe/thuyền và dịch vụ còn đơn giản;
chưa có lái máy bay, hoạt ảnh chèo, lịch NPC hoặc hệ thống lưu kinh tế hoàn chỉnh.

Nguồn và bàn giao: nhánh `codex/coastal-interiors-20261014` tại
https://github.com/letam10/ANANTA/tree/codex/coastal-interiors-20261014
`Docs/COASTAL_20261014_HANDOFF.md` liệt kê thay đổi, bằng chứng và việc còn lại.
