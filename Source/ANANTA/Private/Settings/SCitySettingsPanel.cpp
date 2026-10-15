#include "Settings/SCitySettingsPanel.h"

#include "Framework/Application/SlateApplication.h"
#include "InputCoreTypes.h"
#include "Types/NavigationMetaData.h"

void SCitySettingsPanel::Construct(const FArguments& InArgs)
{
    OnClose = InArgs._OnClose;
    Draft = UANANTAGraphicsSettings::Get()->CaptureOptions();
    AppliedLanguage = Draft.Language;
    const TSharedRef<FNavigationMetaData> Navigation = MakeShared<FNavigationMetaData>();
    Navigation->SetNavigationWrap(EUINavigation::Next);
    Navigation->SetNavigationWrap(EUINavigation::Previous);
    AddMetadata(Navigation);
    ChildSlot[BuildLayout()];
}

const FCityGraphicsOptions& SCitySettingsPanel::GetDraftOptions() const
{
    return Draft;
}

void SCitySettingsPanel::SetDraftOptions(const FCityGraphicsOptions& Options)
{
    Draft = UANANTAGraphicsSettings::SanitizeOptions(Options);
    bHasEdits = true;
}

void SCitySettingsPanel::ApplyDraft()
{
    UANANTAGraphicsSettings* Settings = UANANTAGraphicsSettings::Get();
    Settings->ApplyOptions(Draft);
    Draft = Settings->CaptureOptions();
    AppliedLanguage = Draft.Language;
    bHasEdits = false;
}

bool SCitySettingsPanel::SupportsKeyboardFocus() const
{
    return true;
}

FReply SCitySettingsPanel::OnPreviewKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
    if (Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::F10)
    {
        return CloseDraft();
    }
    return SCompoundWidget::OnPreviewKeyDown(Geometry, Event);
}

FReply SCitySettingsPanel::OnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
    if (Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::F10)
    {
        return CloseDraft();
    }
    if (Event.GetKey() == EKeys::Tab)
    {
        const EUINavigation Direction = Event.IsShiftDown() ? EUINavigation::Previous : EUINavigation::Next;
        return FReply::Handled().SetNavigation(Direction, ENavigationGenesis::Keyboard);
    }
    // Chặn phím gameplay khi focus nằm trong bảng cài đặt.
    return FReply::Handled();
}

FReply SCitySettingsPanel::OnMouseButtonDown(const FGeometry& Geometry, const FPointerEvent& Event)
{
    return FReply::Handled();
}

FText SCitySettingsPanel::L(const TCHAR* Vietnamese, const TCHAR* English) const
{
    return FText::FromString(AppliedLanguage == TEXT("en") ? English : Vietnamese);
}

FText SCitySettingsPanel::QualityLabel(int32 Quality) const
{
    switch (Quality)
    {
    case 0:
        return L(TEXT("Thấp"), TEXT("Low"));
    case 1:
        return L(TEXT("Trung bình"), TEXT("Medium"));
    case 2:
        return L(TEXT("Cao"), TEXT("High"));
    case 3:
        return L(TEXT("Tối đa · Epic"), TEXT("Max · Epic"));
    default:
        return L(TEXT("Tùy chỉnh"), TEXT("Custom"));
    }
}

int32 SCitySettingsPanel::GetPresetQuality() const
{
    const int32 Quality = Draft.ViewDistance;
    const int32 Values[] = { Draft.AntiAliasing, Draft.Shadows, Draft.GlobalIllumination, Draft.Reflections,
        Draft.PostProcess, Draft.Textures, Draft.Effects, Draft.Foliage, Draft.Shading };
    for (int32 Value : Values)
    {
        if (Value != Quality)
        {
            return INDEX_NONE;
        }
    }
    const float Scales[] = { 50.f, 66.666667f, 83.333333f, 100.f };
    return FMath::IsNearlyEqual(Draft.ResolutionScale, Scales[Quality], 0.02f) ? Quality : INDEX_NONE;
}

FText SCitySettingsPanel::PresetLabel() const
{
    return QualityLabel(GetPresetQuality());
}

void SCitySettingsPanel::SetPresetQuality(int32 Quality)
{
    Draft.ViewDistance = Quality;
    Draft.AntiAliasing = Quality;
    Draft.Shadows = Quality;
    Draft.GlobalIllumination = Quality;
    Draft.Reflections = Quality;
    Draft.PostProcess = Quality;
    Draft.Textures = Quality;
    Draft.Effects = Quality;
    Draft.Foliage = Quality;
    Draft.Shading = Quality;
    const float Scales[] = { 50.f, 66.666667f, 83.333333f, 100.f };
    Draft.ResolutionScale = Scales[Quality];
    bHasEdits = true;
}

FReply SCitySettingsPanel::CloseDraft()
{
    Draft = UANANTAGraphicsSettings::Get()->CaptureOptions();
    bHasEdits = false;
    FSlateApplication::Get().DismissAllMenus();
    return OnClose.IsBound() ? OnClose.Execute() : FReply::Handled();
}

FReply SCitySettingsPanel::ResetDraft()
{
    SetDraftOptions(UANANTAGraphicsSettings::MakeDefaults());
    return FReply::Handled();
}

FReply SCitySettingsPanel::ApplyClicked()
{
    ApplyDraft();
    return FReply::Handled();
}
