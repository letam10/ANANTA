# Vật thể lặp và instancing

Cập nhật 2026-10-09. Áp dụng cho Unreal, không phụ thuộc Ctrl+D hay Ctrl+V.

- Tái sử dụng cùng mesh và material cho cửa sổ, ghế, cây/hoa cùng loại.
- Gom vật thể phù hợp bằng ISM/HISM; không tạo mesh/material riêng cho từng bản sao.
- Chia nhóm theo ô streaming, mesh, material và collision; không gom toàn thành phố thành một khối.
- HISM hợp với nhiều vật thể tĩnh. Với nhóm chỉ dùng Nanite, đánh giá ISM vì Nanite đã có culling/LOD riêng.
- Dùng dữ liệu theo instance cho khác màu nhỏ khi shader hỗ trợ, tránh material động riêng cho từng vật.
- Cửa tương tác và xe đang chạy cần trạng thái/chuyển động/collision riêng; vẫn chia sẻ asset mesh/texture.
- Cùng hãng xe nhưng khác mesh/material không phải một nhóm giống nhau để instancing.
- Instancing giảm lệnh vẽ/bộ nhớ; GPU vẫn xử lý hình học, pixel và bóng của các instance thấy được.
- Số lệnh vẽ còn tùy material section, pass, LOD và culling; không hứa toàn bộ chỉ một lần vẽ.
- Ctrl+D/Ctrl+V là thao tác editor; nhân bản actor không bảo đảm đã chuyển thành ISM/HISM.

## Đã kiểm trong dự án

- Tools/Editor/CityScene.py tạo HierarchicalInstancedStaticMeshComponent và gọi add_instances.
- Map đọc lại: 25.021 nhóm / 602.953 instance, gồm 12.010 instance collision ẩn.
- 113.907 instance khối đục đã chuyển sang mesh Nanite, giữ geometry/material/collision.
- Xe NPC hiện là actor riêng dùng chung asset; chưa gom rendering động toàn đội xe.
- Số instance/group không phải số draw call đo được hoặc bằng chứng đạt 90 FPS.

Nguồn: [Epic — Instanced Static Mesh](https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-static-mesh-component-in-unreal-engine).
