#include "Settings/SCitySettingsPanel.h"

#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Input/SCheckBox.h"
#include "Widgets/Input/SComboButton.h"
#include "Widgets/Input/SSpinBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"

TSharedRef<SWidget> SCitySettingsPanel::MakeChoice(TFunction<FText()> CurrentText,
    TFunction<TArray<FText>()> Labels, TFunction<int32()> Selected, TFunction<void(int32)> Select)
{
    return SNew(SComboButton)
        .ContentPadding(FMargin(10.f, 6.f))
        .OnGetMenuContent_Lambda([Labels, Selected, Select]()
        {
            FMenuBuilder Menu(true, nullptr);
            const TArray<FText> Entries = Labels();
            for (int32 Index = 0; Index < Entries.Num(); ++Index)
            {
                const FUIAction Action(
                    FExecuteAction::CreateLambda([Select, Index]() { Select(Index); }),
                    FCanExecuteAction(),
                    FIsActionChecked::CreateLambda([Selected, Index]() { return Selected() == Index; }));
                Menu.AddMenuEntry(Entries[Index], FText::GetEmpty(), FSlateIcon(), Action,
                    NAME_None, EUserInterfaceActionType::RadioButton);
            }
            return Menu.MakeWidget();
        })
        .ButtonContent()
        [
            SNew(STextBlock)
            .Text_Lambda([CurrentText]() { return CurrentText(); })
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 13))
        ];
}

TSharedRef<SWidget> SCitySettingsPanel::MakeToggle(bool FCityGraphicsOptions::* Field)
{
    return SNew(SCheckBox)
        .IsChecked_Lambda([this, Field]()
        {
            return Draft.*Field ? ECheckBoxState::Checked : ECheckBoxState::Unchecked;
        })
        .OnCheckStateChanged_Lambda([this, Field](ECheckBoxState State)
        {
            Draft.*Field = State == ECheckBoxState::Checked;
            bHasEdits = true;
        })
        [
            SNew(STextBlock)
            .Text_Lambda([this, Field]()
            {
                return Draft.*Field ? L(TEXT("Bật"), TEXT("On")) : L(TEXT("Tắt"), TEXT("Off"));
            })
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 13))
            .ColorAndOpacity(FLinearColor::White)
        ];
}

void SCitySettingsPanel::AddGraphicsControls(const TSharedRef<SVerticalBox>& Rows)
{
    AddSection(Rows, TEXT("ĐỒ HỌA"), TEXT("GRAPHICS"));
    const auto QualityLabels = [this]()
    {
        return TArray<FText>{ QualityLabel(0), QualityLabel(1), QualityLabel(2), QualityLabel(3) };
    };
    AddRow(Rows, TEXT("Thiết lập nhanh"), TEXT("Quality preset"), MakeChoice(
        [this]() { return PresetLabel(); }, QualityLabels,
        [this]() { return GetPresetQuality(); },
        [this](int32 Value) { SetPresetQuality(Value); }));

    struct FQualityRow
    {
        const TCHAR* Vietnamese;
        const TCHAR* English;
        int32 FCityGraphicsOptions::* Field;
    };
    const FQualityRow QualityRows[] = {
        { TEXT("Tầm nhìn"), TEXT("View distance"), &FCityGraphicsOptions::ViewDistance },
        { TEXT("Khử răng cưa"), TEXT("Anti-aliasing"), &FCityGraphicsOptions::AntiAliasing },
        { TEXT("Bóng đổ"), TEXT("Shadows"), &FCityGraphicsOptions::Shadows },
        { TEXT("Chiếu sáng toàn cục"), TEXT("Global illumination"), &FCityGraphicsOptions::GlobalIllumination },
        { TEXT("Phản chiếu"), TEXT("Reflections"), &FCityGraphicsOptions::Reflections },
        { TEXT("Hậu kỳ"), TEXT("Post processing"), &FCityGraphicsOptions::PostProcess },
        { TEXT("Chất lượng bề mặt"), TEXT("Textures"), &FCityGraphicsOptions::Textures },
        { TEXT("Hiệu ứng"), TEXT("Effects"), &FCityGraphicsOptions::Effects },
        { TEXT("Cây cỏ"), TEXT("Foliage"), &FCityGraphicsOptions::Foliage },
        { TEXT("Đổ bóng vật liệu"), TEXT("Shading"), &FCityGraphicsOptions::Shading }
    };
    for (const FQualityRow& Row : QualityRows)
    {
        const auto Field = Row.Field;
        AddRow(Rows, Row.Vietnamese, Row.English, MakeChoice(
            [this, Field]() { return QualityLabel(Draft.*Field); }, QualityLabels,
            [this, Field]() { return Draft.*Field; },
            [this, Field](int32 Value)
            {
                Draft.*Field = Value;
                bHasEdits = true;
            }));
    }
    AddRow(Rows, TEXT("Tỷ lệ dựng hình TSR (%)"), TEXT("TSR render scale (%)"),
        SNew(SSpinBox<float>)
        .MinValue(50.f)
        .MaxValue(100.f)
        .MinSliderValue(50.f)
        .MaxSliderValue(100.f)
        .Delta(1.f)
        .MaxFractionalDigits(1)
        .Font(FCoreStyle::GetDefaultFontStyle("Regular", 13))
        .ContentPadding(FMargin(10.f, 6.f))
        .Value_Lambda([this]() { return Draft.ResolutionScale; })
        .OnValueChanged_Lambda([this](float Value)
        {
            Draft.ResolutionScale = FMath::Clamp(Value, 50.f, 100.f);
            bHasEdits = true;
        }));
}

TArray<float> SCitySettingsPanel::FrameRateChoices(const float CurrentCap)
{
    TArray<float> Limits = { 0, 30, 60, 90, 120, 144, 165, 180, 240 };
    if (FMath::IsFinite(CurrentCap) && CurrentCap >= 30 && CurrentCap <= 240 && !Limits.Contains(CurrentCap))
    {
        // Hien muc FPS tuy chinh da luu, ke ca khi khong nam trong cac preset.
        Limits.Add(CurrentCap);
        Limits.Sort();
    }
    return Limits;
}

void SCitySettingsPanel::AddDisplayControls(const TSharedRef<SVerticalBox>& Rows)
{
    AddSection(Rows, TEXT("HIỂN THỊ & NGÔN NGỮ"), TEXT("DISPLAY & LANGUAGE"));
    const TArray<float> FrameLimits = FrameRateChoices(Draft.FrameRateLimit);
    AddRow(Rows, TEXT("Giới hạn khung hình"), TEXT("Frame rate limit"), MakeChoice(
        [this]()
        {
            return Draft.FrameRateLimit <= 0.f ? L(TEXT("Không giới hạn"), TEXT("Unlimited"))
                : FText::FromString(FString::Printf(TEXT("%g FPS"), Draft.FrameRateLimit));
        },
        [this, FrameLimits]()
        {
            TArray<FText> Labels;
            for (const float Limit : FrameLimits)
            {
                Labels.Add(Limit == 0 ? L(TEXT("Không giới hạn"), TEXT("Unlimited"))
                    : FText::FromString(FString::Printf(TEXT("%g FPS"), Limit)));
            }
            return Labels;
        },
        [this, FrameLimits]() { return FrameLimits.IndexOfByKey(Draft.FrameRateLimit); },
        [this, FrameLimits](int32 Index)
        {
            Draft.FrameRateLimit = FrameLimits[Index];
            bHasEdits = true;
        }));
    AddRow(Rows, TEXT("Đồng bộ dọc (VSync)"), TEXT("Vertical sync (VSync)"),
        MakeToggle(&FCityGraphicsOptions::bVSync));
    AddRow(Rows, TEXT("Hiển thị FPS"), TEXT("Show FPS"), MakeToggle(&FCityGraphicsOptions::bShowFPS));
    AddRow(Rows, TEXT("Ngôn ngữ"), TEXT("Language"), MakeChoice(
        [this]() { return FText::FromString(Draft.Language == TEXT("en") ? TEXT("English") : TEXT("Tiếng Việt")); },
        []() { return TArray<FText>{ FText::FromString(TEXT("Tiếng Việt")), FText::FromString(TEXT("English")) }; },
        [this]() { return Draft.Language == TEXT("en") ? 1 : 0; },
        [this](int32 Index)
        {
            Draft.Language = Index == 1 ? TEXT("en") : TEXT("vi");
            bHasEdits = true;
        }));
    Rows->AddSlot()
        .AutoHeight()
        .Padding(14.f, 12.f)
        [
            SNew(STextBlock)
            .Text_Lambda([this]()
            {
                return L(TEXT("Tối đa dùng Epic (3), TSR 100%. FPS thực tế tùy cảnh và phần cứng. "
                    "VSync có thể giới hạn FPS theo màn hình. Esc / F10 đóng và bỏ thay đổi chưa áp dụng."),
                    TEXT("Max uses Epic (3), TSR 100%. Actual FPS depends on the scene and hardware. "
                    "VSync may limit FPS to your display. Esc / F10 closes and discards unapplied changes."));
            })
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 11))
            .ColorAndOpacity(FLinearColor(0.67f, 0.77f, 0.85f))
            .AutoWrapText(true)
        ];
}
