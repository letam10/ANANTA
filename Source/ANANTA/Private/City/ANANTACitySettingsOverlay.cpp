#include "City/ANANTACityController.h"

#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "Settings/ANANTAGraphicsSettings.h"
#include "Settings/CityText.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Notifications/SProgressBar.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

void AANANTACityController::InitializeSettingsUI()
{
    auto* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
    if (!Viewport || !IsLocalController())
    {
        return;
    }
    SettingsOverlay = SNew(SOverlay)
        + SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Top).Padding(24)
        [
            SNew(SBox).WidthOverride(260)
            [
                SNew(SVerticalBox)
                + SVerticalBox::Slot().AutoHeight()
                [
                    SNew(SButton).ContentPadding(FMargin(14, 9))
                    .OnClicked_Lambda([this]()
                    {
                        ToggleSettings();
                        return FReply::Handled();
                    })
                    [
                        SNew(STextBlock).Text_Lambda([]()
                        {
                            return FText::FromString(CityText(TEXT("SETTINGS  [Esc / F10]"),
                                TEXT("CÀI ĐẶT  [Esc / F10]")));
                        })
                    ]
                ]
                + SVerticalBox::Slot().AutoHeight().Padding(0, 5)
                [
                    SNew(STextBlock).ColorAndOpacity(FLinearColor(0.65f, 0.85f, 0.95f))
                    .Text_Lambda([]()
                    {
                        return FText::FromString(CityText(TEXT("Hold Alt: cursor   |   F8: FPS"),
                            TEXT("Giữ Alt: chuột   |   F8: FPS")));
                    })
                ]
                + SVerticalBox::Slot().AutoHeight().Padding(0, 6)
                [
                    SNew(SBorder).Padding(10).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                    .BorderBackgroundColor(FLinearColor(0.02f, 0.04f, 0.07f, 0.94f))
                    .Visibility_Lambda([]()
                    {
                        const auto* Settings = UANANTAGraphicsSettings::Get();
                        return Settings && Settings->IsFPSVisible() ? EVisibility::HitTestInvisible
                            : EVisibility::Collapsed;
                    })
                    [
                        SNew(SVerticalBox)
                        + SVerticalBox::Slot().AutoHeight()
                        [
                            SNew(STextBlock).Text_Lambda([this]()
                            {
                                return FText::FromString(FString::Printf(TEXT("%.0f FPS  |  %.2f ms"),
                                    MeasuredFPS, MeasuredFrameMs));
                            })
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 6)
                        [
                            SNew(SProgressBar).Percent_Lambda([this]()
                            {
                                return TOptional<float>(FMath::Clamp(float(MeasuredFPS / 90.0), 0.f, 1.f));
                            })
                            .FillColorAndOpacity(FLinearColor(0.15f, 0.8f, 0.65f))
                        ]
                        + SVerticalBox::Slot().AutoHeight()
                        [
                            SNew(STextBlock).Text_Lambda([]()
                            {
                                return FText::FromString(CityText(TEXT("Target: 90 FPS | 0.5s average"),
                                    TEXT("Mục tiêu: 90 FPS | TB 0,5 giây")));
                            })
                        ]
                    ]
                ]
            ]
        ];
    Viewport->AddViewportWidgetContent(SettingsOverlay.ToSharedRef(), 10);
}
