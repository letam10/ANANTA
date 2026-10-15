# Rà soát runtime NPC và giao thông thành phố 6,8 km

Phạm vi: đọc source và automation test; không mở Unreal, build hoặc chạy workload.

## 1. Giao thông đường bộ không phủ phần lớn thành phố mở rộng

- **Tác động:** người chơi ở các quận xa trung tâm có thể không thấy xe giao thông
  theo tuyến, dù còn ở trong ranh giới đường 6,8 km.
- `Source/ANANTA/Private/City/Mobility/CityMobilityData.cpp:53-57` đặt
  `X0` trong `[-36000, 36000]`, `X1 = X0 + 24000`, và `Y0` chỉ là `0` hoặc
  `-24000`. Các tuyến xe đường bộ do đó chỉ nằm trong vùng trung tâm, không
  được phân bố theo ranh giới `RoadExtent = 336000`.
- `Source/ANANTA/Private/City/Mobility/CityTransportManager.cpp:64-75` chỉ
  thử spawn cạnh stop đã định nghĩa khi người chơi cách stop từ 1.800 đến
  `ActivationDistance = 7000` cm (`CityMobilityData.h:24`). Vì thế các vị trí
  mới xa vùng tuyến sẽ không kích hoạt xe đường bộ.
- `Source/ANANTA/Private/Tests/CityMobilityTests.cpp:24-49` kiểm tra từng điểm
  nằm trong thành phố, trục đường và làn; không kiểm tra độ phủ tuyến quanh
  vùng mở rộng. Test hiện tại có thể đạt dù khoảng trống này còn tồn tại.
- **Tái hiện đề xuất:** trong map đã load, đặt pawn tại `(200000, 0, Z)`, đợi
  manager tick, kiểm tra `Fleet` không có xe đường bộ; so sánh với pawn gần
  stop tuyến trung tâm. Cần chạy test/runtime trong Unreal để xác nhận hành vi
  spawn và khả năng nhìn thấy xe.
- **Mức chứng cứ:** giới hạn vùng tuyến và điều kiện kích hoạt được chứng minh
  trực tiếp từ source. Chưa có runtime capture chứng minh trải nghiệm trong map
  mới; chưa đánh giá tuyến cầu, bến nước hoặc tình trạng mesh được load.

## Kiểm chứng phạm vi

- Chỉ đọc source và test; không thay đổi code, asset hay map.
- Chưa chạy Unreal automation hoặc gameplay runtime theo hợp đồng review.
