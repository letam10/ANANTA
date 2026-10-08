#pragma once

#include "CoreMinimal.h"
#include "Framework/SlateDelegates.h"
#include "Settings/ANANTAGraphicsSettings.h"
#include "Widgets/DeclarativeSyntaxSupport.h"
#include "Widgets/SCompoundWidget.h"

class SVerticalBox;

class ANANTA_API SCitySettingsPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SCitySettingsPanel) {}
        SLATE_EVENT(FOnClicked, OnClose)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
    const FCityGraphicsOptions& GetDraftOptions() const;
    void SetDraftOptions(const FCityGraphicsOptions& Options);
    void ApplyDraft();

    virtual bool SupportsKeyboardFocus() const override;
    virtual FReply OnPreviewKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
    virtual FReply OnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
    virtual FReply OnMouseButtonDown(const FGeometry& Geometry, const FPointerEvent& Event) override;

private:
    FCityGraphicsOptions Draft;
    FString AppliedLanguage;
    FOnClicked OnClose;
    bool bHasEdits = false;

    FText L(const TCHAR* Vietnamese, const TCHAR* English) const;
    FText QualityLabel(int32 Quality) const;
    FText PresetLabel() const;
    int32 GetPresetQuality() const;
    void SetPresetQuality(int32 Quality);
    FReply CloseDraft();
    FReply ResetDraft();
    FReply ApplyClicked();

    TSharedRef<SWidget> BuildLayout();
    TSharedRef<SWidget> BuildFooter();
    void AddGraphicsControls(const TSharedRef<SVerticalBox>& Rows);
    void AddDisplayControls(const TSharedRef<SVerticalBox>& Rows);
    void AddSection(const TSharedRef<SVerticalBox>& Rows, const TCHAR* Vietnamese, const TCHAR* English);
    void AddRow(const TSharedRef<SVerticalBox>& Rows, const TCHAR* Vietnamese, const TCHAR* English,
        const TSharedRef<SWidget>& Control);
    TSharedRef<SWidget> MakeChoice(TFunction<FText()> CurrentText, TFunction<TArray<FText>()> Labels,
        TFunction<int32()> Selected, TFunction<void(int32)> Select);
    TSharedRef<SWidget> MakeToggle(bool FCityGraphicsOptions::* Field);
};
