#include "Settings/CityText.h"

#include "Settings/ANANTAGraphicsSettings.h"

FString CityText(const TCHAR* English, const TCHAR* Vietnamese)
{
    const auto* Settings = UANANTAGraphicsSettings::Get();
    return Settings && Settings->GetLanguage() == TEXT("vi") ? Vietnamese : English;
}

FString CityTranslate(const FString& English)
{
    if (CityText(TEXT("en"), TEXT("vi")) != TEXT("vi"))
    {
        return English;
    }
    static const TMap<FString, FString> Translations = {
        { TEXT("ANANTA  |  ANOMALY CASE"), TEXT("ANANTA  |  HỒ SƠ DỊ THƯỜNG") },
        { TEXT("Meet the cafe contact [E]"), TEXT("Gặp người liên lạc tại quán cà phê [E]") },
        { TEXT("Recover the anomaly fragment [E]"), TEXT("Thu hồi mảnh dị thường [E]") },
        { TEXT("Return the fragment to the cafe contact [E]"), TEXT("Mang mảnh vỡ về quán cà phê [E]") },
        { TEXT("Case closed. Reward received: 1 city token"), TEXT("Hoàn tất hồ sơ. Đã nhận 1 thẻ thành phố") },
        { TEXT("Cafe contact"), TEXT("Người liên lạc") },
        { TEXT("Anomaly site"), TEXT("Điểm dị thường") },
        { TEXT("Loading nearby streets..."), TEXT("Đang tải đường phố xung quanh...") },
        { TEXT("Space: brake before exiting"), TEXT("Space: phanh trước khi xuống xe") },
        { TEXT("E: leave car"), TEXT("E: xuống xe") },
        { TEXT("E: drive car"), TEXT("E: lái xe") },
        { TEXT("E: speak with cafe contact"), TEXT("E: nói chuyện với người liên lạc") },
        { TEXT("E: investigate anomaly trace"), TEXT("E: điều tra dấu vết dị thường") },
        { TEXT("E: recover fragment"), TEXT("E: nhặt mảnh vỡ") },
        { TEXT("Progress saved"), TEXT("Đã lưu tiến trình") },
        { TEXT("Progress restored"), TEXT("Đã khôi phục tiến trình") },
        { TEXT("Progress saved to recovery slot"), TEXT("Đã lưu vào bản dự phòng") },
        { TEXT("New city journey"), TEXT("Bắt đầu hành trình mới") },
        { TEXT("New isolated QA journey"), TEXT("Lượt kiểm tra riêng biệt") },
        { TEXT("Save rejected: invalid state"), TEXT("Không thể lưu: trạng thái không hợp lệ") },
        { TEXT("Save failed - check free disk space"), TEXT("Lưu thất bại - kiểm tra dung lượng ổ đĩa") },
        { TEXT("Save verification failed"), TEXT("Kiểm tra bản lưu thất bại") },
        { TEXT("Rested: health restored and progress saved"), TEXT("Đã nghỉ ngơi, hồi máu và lưu tiến trình") },
        { TEXT("Clinic: health restored"), TEXT("Phòng khám: đã hồi máu") },
        { TEXT("Supplies already collected here"), TEXT("Đã nhận tiếp tế tại đây") },
        { TEXT("Collected 1 supply"), TEXT("Đã nhận 1 phần tiếp tế") },
        { TEXT("Location discovered"), TEXT("Đã khám phá địa điểm") },
        { TEXT("Service could not save progress; please try again"), TEXT("Chưa lưu được dịch vụ; hãy thử lại") },
        { TEXT("rest and save"), TEXT("nghỉ ngơi và lưu") },
        { TEXT("restore health"), TEXT("hồi máu") },
        { TEXT("supplies already collected"), TEXT("đã nhận tiếp tế") },
        { TEXT("collect supplies"), TEXT("nhận tiếp tế") },
        { TEXT("read again (discovered)"), TEXT("đọc lại (đã khám phá)") },
        { TEXT("discover this location"), TEXT("khám phá địa điểm") },
        { TEXT("NOVA coffee break"), TEXT("Nghỉ tại quán NOVA") },
        { TEXT("Rest at home"), TEXT("Nghỉ tại nhà") },
        { TEXT("PAPER LANTERN / BOOKS"), TEXT("PAPER LANTERN / HIỆU SÁCH") },
        { TEXT("AOBA / NEIGHBOURHOOD CLINIC"), TEXT("AOBA / PHÒNG KHÁM") },
        { TEXT("EVERYDAY / CORNER MARKET"), TEXT("EVERYDAY / CỬA HÀNG") },
        { TEXT("FRAME / CITY GALLERY"), TEXT("FRAME / PHÒNG TRANH") },
        { TEXT("NORTHSTAR / MOTOR WORKS"), TEXT("NORTHSTAR / XƯỞNG XE") },
        { TEXT("EASTLINE / VISITOR CENTRE"), TEXT("EASTLINE / TRUNG TÂM THÔNG TIN") },
        { TEXT("The Eastline archive records an unusual signal beneath the old station."),
            TEXT("Hồ sơ Eastline ghi nhận tín hiệu bất thường bên dưới nhà ga cũ.") },
        { TEXT("These city studies trace the river district before the transit expansion."),
            TEXT("Các bản nghiên cứu mô tả khu ven sông trước khi mở rộng giao thông.") },
        { TEXT("Workshop notes: brake before leaving the car and keep junctions clear."),
            TEXT("Lưu ý xưởng: phanh trước khi xuống xe và không chắn giao lộ.") },
        { TEXT("Eastline connects the market streets, gardens and eastern business district."),
            TEXT("Eastline kết nối phố chợ, công viên và khu thương mại phía đông.") }
    };
    if (const auto* Translation = Translations.Find(English))
    {
        return *Translation;
    }
    return English;
}
