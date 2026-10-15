#include "City/ANANTACityController.h"

#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "Framework/Application/SlateApplication.h"
#include "HAL/PlatformTime.h"
#include "Settings/ANANTAGraphicsSettings.h"
#include "Settings/SCitySettingsPanel.h"

void AANANTACityController::ToggleSettings()
{
    if (IsSettingsOpen())
    {
        CloseSettings();
        return;
    }
    auto* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
    if (!Viewport || !UANANTAGraphicsSettings::Get())
    {
        return;
    }
    bPausedBeforeSettings = IsPaused();
    SaveNow();
    SetPause(true);
    SettingsPanel = SNew(SCitySettingsPanel).OnClose_Lambda([this]()
    {
        CloseSettings();
        return FReply::Handled();
    });
    Viewport->AddViewportWidgetContent(SettingsPanel.ToSharedRef(), 100);
    bShowMouseCursor = true;
    FInputModeUIOnly InputMode;
    InputMode.SetWidgetToFocus(SettingsPanel);
    InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
    SetInputMode(InputMode);
    FlushPressedKeys();
    FSlateApplication::Get().SetKeyboardFocus(SettingsPanel, EFocusCause::SetDirectly);
}

void AANANTACityController::CloseSettings(const bool bResumeGame)
{
    auto* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
    if (SettingsPanel.IsValid())
    {
        if (Viewport)
        {
            Viewport->RemoveViewportWidgetContent(SettingsPanel.ToSharedRef());
        }
        SettingsPanel.Reset();
        if (bResumeGame)
        {
            SetPause(bPausedBeforeSettings);
            bShowMouseCursor = false;
            SetInputMode(FInputModeGameOnly());
            FlushPressedKeys();
        }
    }
    if (!bResumeGame && SettingsOverlay.IsValid())
    {
        if (Viewport)
        {
            Viewport->RemoveViewportWidgetContent(SettingsOverlay.ToSharedRef());
        }
        SettingsOverlay.Reset();
    }
}

void AANANTACityController::ToggleFPS()
{
    if (auto* Settings = UANANTAGraphicsSettings::Get())
    {
        auto Options = Settings->CaptureOptions();
        Options.bShowFPS = !Options.bShowFPS;
        Settings->ApplyOptions(Options);
    }
}

void AANANTACityController::ShowMenuCursor()
{
    if (!IsSettingsOpen())
    {
        bShowMouseCursor = true;
        FInputModeGameAndUI InputMode;
        InputMode.SetHideCursorDuringCapture(false);
        InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
        SetInputMode(InputMode);
    }
}

void AANANTACityController::HideMenuCursor()
{
    if (!IsSettingsOpen())
    {
        bShowMouseCursor = false;
        SetInputMode(FInputModeGameOnly());
    }
}

void AANANTACityController::UpdateFrameMeter()
{
    const double Now = FPlatformTime::Seconds();
    if (FrameMeterStart == 0)
    {
        FrameMeterStart = Now;
        return;
    }
    ++FrameMeterCount;
    const double Elapsed = Now - FrameMeterStart;
    if (Elapsed >= 0.5)
    {
        // Dùng thời gian thực: pause hoặc giới hạn FPS không tạo số đo giả.
        MeasuredFPS = FrameMeterCount / Elapsed;
        MeasuredFrameMs = 1000.0 * Elapsed / FrameMeterCount;
        FrameMeterCount = 0;
        FrameMeterStart = Now;
    }
}
