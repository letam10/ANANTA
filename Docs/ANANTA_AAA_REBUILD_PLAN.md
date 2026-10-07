# ANANTA / Nova City — kế hoạch dựng lại vertical slice đô thị

Ngày cập nhật: 2026-09-28

Tài liệu này là kế hoạch thực thi sau khi kiểm tra ảnh chụp và trạng thái UE hiện tại. Mục tiêu là một vertical slice nguyên bản có chất lượng hình ảnh và mật độ đô thị thuyết phục trên RTX 3050; không gọi blockout hiện tại là AAA.

## Bằng chứng và chẩn đoán hiện tại

- Ảnh overview hiện tại cho thấy bốn cụm sao chép giống nhau, nền/mặt đất bị ngắt quãng và khoảng trống màu xanh lớn. Đây là bố cục blockout, chưa phải thành phố liên tục.
- Bộ nhà hiện tại chủ yếu là hộp, cửa sổ lặp theo lưới, roof cap và cây hình trụ. Chưa có mặt dựng có chiều sâu, ban công, mái che, cửa ra vào, biển hiệu, decal, xe, NPC, giao thông hoặc địa hình chuyển tiếp.
- Bộ vật liệu mới chỉ có albedo cho facade/road/sidewalk và texture emissive cho glass. Chưa có bộ normal/roughness/AO đầy đủ. Material graph trước đó đã được asset slot xác nhận nhưng output BaseColor vẫn từng đọc là `Expression=null`; mọi material phải được kiểm tra graph output, không chỉ slot của StaticMesh.
- Map đang là persistent level thường, chưa có World Partition, HLOD, Data Layers hoặc PCG graph đô thị. 1.526 actor được đặt thủ công bằng cách nhân bản kit; cách này vừa tạo gap hình học vừa không phải kiến trúc mở rộng thành phố.
- Config hiện bật DX12/SM6, Lumen/VSM và Ray Tracing nhưng đồng thời có Substrate/Ray Tracing toàn dự án; chưa có preset RTX 3050, exposure reference, post-process volume hoặc các profile đo `stat unit/stat gpu`.
- UE-MCP hiện đã mất kết nối trong lúc kiểm tra; nhiều tiến trình `ue-mcp@1.3.9` trùng project còn tồn tại. Không được thêm asset hoặc gọi editor khi chưa dọn tiến trình dư và khôi phục đúng một bridge/editor.

## Nguyên tắc quyết định

1. **Khóa chất lượng ở một hero slice trước khi nhân rộng.** Hero slice rộng 200–300 m gồm một giao lộ, hai mặt phố, ba loại mặt dựng, một hẻm, một landmark mảnh Ananta và một góc nội thất nhìn thấy được.
2. **Đạt gate hình ảnh trước gate số lượng.** Nếu camera hero vẫn thấy nền trống, vật liệu phẳng, ánh sáng không đọc được hoặc graph output chưa nối đúng thì không thêm block, không nhân bản actor.
3. **Tách nguồn nghệ thuật khỏi lắp ráp UE.** Blender/Pillow tạo mesh và texture lặp lại được; UE-MCP chỉ import, xây material graph, lắp level, đặt ánh sáng, PCG, gameplay và kiểm chứng.
4. **Mỗi thay đổi phải có readback và ảnh.** Slot material, output graph, transform, bounds, light activation và package save đều phải đọc lại; ảnh hero và PIE là bằng chứng cuối.
5. **Giữ phạm vi nguyên bản.** Lấy cảm hứng từ nhịp sống đô thị anime, không sao chép asset/nhân vật/nhãn hiệu của ANANTA, Genshin Impact hoặc GTA V.

## Các pha thực thi

### Pha 0 — ổn định và baseline

- Xác định đúng một Unreal Editor của `D:/GAME/ANANTA/ANANTA.uproject` và một UE-MCP bridge; dừng các node/bridge dư đã xác minh thuộc tác vụ này.
- Mở lại map hiện tại, lưu các package đang dirty theo lựa chọn có kiểm soát và chụp baseline editor/PIE.
- Bật log/profiling tối thiểu; ghi GPU renderer, resolution, VRAM, map package và actor count.
- Thành công khi bridge connected, map clean, không có crash/shader compile đang chạy và baseline mở lại được.

### Pha 1 — hero slice có vật liệu và ánh sáng đúng

- Thay bố cục bốn cụm rời bằng một nền liên tục: asphalt, curb, sidewalk, crosswalk, drainage, hẻm và một quảng trường nhỏ. Đường phải nối với đường; không để mép tile lộ ra ở camera hero.
- Dựng ba module mặt dựng nguyên bản có cửa, ban công, mái che, ledge, biển hiệu và biến thể chiều cao; thêm một mặt dựng cũ, một mặt dựng thương mại và một mặt dựng ga tàu/metro. Hạn chế lặp texture bằng UV scale/variation/decals.
- Tạo bộ PBR đầy đủ: albedo sRGB; normal, roughness, AO linear; emissive riêng cho kính/biển. Dùng giá trị trong khoảng PBR và kiểm tra `BaseColor`, `Roughness`, `Normal`, `Emissive` đã có expression output thật.
- Dùng một movable directional sun, một skylight, VSM và fog; bật `bEnabled`/`bAutoActivate` ở actor/component. Thêm PostProcessVolume với ACES và manual exposure cho capture hero; gameplay dùng eye adaptation có giới hạn.
- Dùng Lumen Software RT làm mặc định cho RTX 3050. Hardware RT chỉ là tier thử nghiệm sau khi có GPU capture.
- Gate: ảnh hero ban ngày và blue-hour đọc được chất liệu, cạnh/chiều sâu, bóng, phản xạ và quy mô người; không còn nền xanh trống trong khung; graph readback không còn expression null.

### Pha 2 — mật độ đô thị và tương tác

- Tạo PCG graph có seed cố định, bám road spline/sidewalk: street lamps, traffic lights, signs, benches, bins, planters, utility boxes, bollards, foliage và parking.
- Thêm xe static trước để kiểm tra bố cục; sau đó thêm spline traffic với số lượng giới hạn, collision và LOD. NPC chỉ thêm sau khi đường và điểm dừng xe đã ổn.
- Tạo landmark shard và một điểm nhiệm vụ: trigger, interaction prompt, collectible state và HUD marker. Mỗi props có collision và LOD phù hợp.
- Gate: camera đường phố có đủ dấu hiệu thành phố hiện đại trong 10 giây nhìn, nhưng không có object lặp vô hạn hoặc spawn xuyên hình học.

### Pha 3 — mở rộng thành phố đúng kiến trúc

- Chuyển map sang World Partition persistent level với một runtime hash grid; bật OFPA. Dùng Data Layers cho day/night, traffic và mission state.
- Tạo HLOD cho skyline trước khi dùng Lumen Far Field; kiểm tra streaming source và loading range bằng `stat levels`.
- Mở rộng từ hero slice thành ba district có quy tắc khác nhau, thay vì sao chép một kit cùng transform. Mỗi district có road graph, skyline silhouette, palette và prop density riêng.
- Gate: đi bộ/xe qua ranh giới district không thấy gap, pop-in nghiêm trọng hoặc nền ngoài thế giới; HLOD/cell load có readback.

### Pha 4 — gameplay vertical slice

- Giữ HUD C++/UMG persistent. Thêm traversal cơ bản, leo/nhảy, combat nhóm tối thiểu, interaction với môi trường, xe và nhiệm vụ thu thập mảnh vỡ.
- Kiểm tra input, save state, respawn, camera collision, nav/AI và UI ở PIE; không coi Blueprint compile là bằng chứng gameplay chạy.

### Pha 5 — RTX 3050 performance gate

- Output 1080p, internal 720p/900p + TSR; bắt đầu target 30 FPS, sau đó 45 FPS. 60 FPS chỉ khi đo đạt.
- Chạy ba view: downtown, interior/hẻm, traffic. Thu `stat unit`, `stat gpu`, `stat sceneRendering`, `stat initviews`, `stat levels` và Unreal Insights trace.
- Gate: 30 FPS <=33,3 ms hoặc 45 FPS <=22,2 ms, VRAM còn 15–20%, không shader hitch/streaming hitch; ghi lại preset và renderer.

## Thứ tự sửa ngay sau khi khôi phục editor

1. Dọn bridge dư và xác nhận đúng editor/port.
2. Readback material graph hiện tại; sửa output connection trước khi tạo texture mới.
3. Tạo nền/đường liên tục và một hero camera cố định.
4. Thêm PostProcessVolume + exposure và kiểm tra ánh sáng actor/component.
5. Nhập hero materials PBR và render lại hai ảnh (day/blue-hour).
6. Chỉ khi hai ảnh đạt gate mới tạo PCG props/xe, rồi mới chuyển World Partition và nhân rộng district.

Playbook toàn cục dùng cho mọi lượt code/bug UE: `C:/Users/TAM/Documents/Codex/Codex-Desktop-Profiles/ChatGPT/codex-home/memories/extensions/ad_hoc/notes/20260928-161133-ue-aaa-3050-playbook.md`.
