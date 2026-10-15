#include "QA/CitySettingsCheck.h"

#include "City/ANANTACityController.h"
#include "Engine/World.h"
#include "Framework/Application/SlateApplication.h"
#include "Widgets/Layout/SScrollBox.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Settings/ANANTAGraphicsSettings.h"
#include "Settings/SCitySettingsPanel.h"
#include "UnrealClient.h"
#include "Widgets/Text/STextBlock.h"

namespace CitySettingsEvidence
{
bool ContainsApplyText(const TSharedRef<SWidget>& Widget)
{
    if (Widget->GetTypeAsString() == TEXT("STextBlock"))
    {
        const FString Text = StaticCastSharedRef<STextBlock>(Widget)->GetText().ToString();
        return Text.Contains(TEXT("Apply")) || Text.Contains(TEXT("Áp dụng"));
    }
    FChildren* Children = Widget->GetChildren();
    for (int32 Index = 0; Index < Children->Num(); ++Index)
    {
        if (ContainsApplyText(Children->GetChildAt(Index)))
        {
            return true;
        }
    }
    return false;
}

TSharedPtr<SWidget> FindApply(const TSharedRef<SWidget>& Widget)
{
    if (Widget->GetTypeAsString() == TEXT("SButton") && ContainsApplyText(Widget))
    {
        return Widget;
    }
    FChildren* Children = Widget->GetChildren();
    for (int32 Index = 0; Index < Children->Num(); ++Index)
    {
        if (auto Found = FindApply(Children->GetChildAt(Index)))
        {
            return Found;
        }
    }
    return nullptr;
}
}

FString UCitySettingsCheck::Directory() const
{
    return FPaths::ProjectSavedDir() / TEXT("QA/CitySettings");
}

void UCitySettingsCheck::SendKey(const FKey& Key, const bool bSlate, const bool bDown)
{
    if (bSlate)
    {
        auto& Slate = FSlateApplication::Get();
        const FKeyEvent Event(Key, FModifierKeysState(), 0, false, 0, 0);
        Slate.ProcessKeyDownEvent(Event);
        Slate.ProcessKeyUpEvent(Event);
        return;
    }
    const auto Dispatch = [&](const EInputEvent Type)
    {
        Controller->InputKey(FInputKeyEventArgs(nullptr, INPUTDEVICEID_NONE, Key, Type,
            Type == IE_Pressed ? 1.f : 0.f, false, FPlatformTime::Cycles64()));
    };
    Dispatch(bDown ? IE_Pressed : IE_Released);
    if (bDown && Key != EKeys::W && Key != EKeys::LeftMouseButton)
    {
        Dispatch(IE_Released);
    }
}

bool UCitySettingsCheck::ClickApply()
{
    if (!Controller->GetSettingsPanel())
    {
        return false;
    }
    auto Button = CitySettingsEvidence::FindApply(Controller->GetSettingsPanel().ToSharedRef());
    if (!Button || !Button->IsEnabled())
    {
        return false;
    }
    auto& Slate = FSlateApplication::Get();
    Slate.SetKeyboardFocus(Button, EFocusCause::SetDirectly);
    const FKeyEvent Enter(EKeys::Enter, FModifierKeysState(), 0, false, 0, 0);
    const bool bDown = Slate.ProcessKeyDownEvent(Enter);
    const bool bUp = Slate.ProcessKeyUpEvent(Enter);
    return bDown || bUp;
}

void UCitySettingsCheck::ScrollMenuBottom()
{
    TFunction<void(const TSharedRef<SWidget>&)> Visit;
    Visit = [&Visit](const TSharedRef<SWidget>& Widget)
    {
        if (Widget->GetTypeAsString() == TEXT("SScrollBox"))
        {
            StaticCastSharedRef<SScrollBox>(Widget)->ScrollToEnd();
            return;
        }
        FChildren* Children = Widget->GetChildren();
        for (int32 Index = 0; Index < Children->Num(); ++Index)
        {
            Visit(Children->GetChildAt(Index));
        }
    };
    if (Controller->GetSettingsPanel())
    {
        Visit(Controller->GetSettingsPanel().ToSharedRef());
    }
}

void UCitySettingsCheck::Capture(const FString& Name)
{
    IFileManager::Get().MakeDirectory(*Directory(), true);
    const FString Path = Directory() / (Name + TEXT(".png"));
    IFileManager::Get().Delete(*Path, false);
    Captures.Add(Path);
    FScreenshotRequest::RequestScreenshot(Path, true, false, false);
}

void UCitySettingsCheck::RecordSettings()
{
    const auto Options = UANANTAGraphicsSettings::Get()->CaptureOptions();
    Evidence.Add(FString::Printf(TEXT("language=%s fps_meter=%d cap=%.1f scale=%.3f"),
        *Options.Language, Options.bShowFPS, Options.FrameRateLimit, Options.ResolutionScale));
    static const TCHAR* Names[] = {
        TEXT("sg.ViewDistanceQuality"), TEXT("sg.AntiAliasingQuality"), TEXT("sg.ShadowQuality"),
        TEXT("sg.GlobalIlluminationQuality"), TEXT("sg.ReflectionQuality"), TEXT("sg.PostProcessQuality"),
        TEXT("sg.TextureQuality"), TEXT("sg.EffectsQuality"), TEXT("sg.FoliageQuality"),
        TEXT("sg.ShadingQuality"), TEXT("r.ScreenPercentage"), TEXT("t.MaxFPS"), TEXT("r.VSync"),
        TEXT("r.Nanite.Culling.Frustum"), TEXT("r.Nanite.Culling.HZB"), TEXT("r.Streaming.PoolSize"),
        TEXT("r.Lumen.HardwareRayTracing"), TEXT("r.Shadow.Virtual.SMRT.RayCountDirectional")
    };
    for (const TCHAR* Name : Names)
    {
        const auto* Variable = IConsoleManager::Get().FindConsoleVariable(Name);
        Evidence.Add(FString::Printf(TEXT("%s=%s"), Name, Variable ? *Variable->GetString() : TEXT("MISSING")));
    }
}

void UCitySettingsCheck::Finish(bool bSuccess, const FString& Detail)
{
    if (bFinished)
    {
        return;
    }
    bFinished = true;
    for (const FString& Path : Captures)
    {
        bSuccess &= IFileManager::Get().FileSize(*Path) > 0;
    }
    Evidence.Add(Detail);
    Evidence.Add(TEXT("Input: PlayerController keys and Slate focused button keyboard events; ")
        TEXT("no desktop input or benchmark."));
    Evidence.Add(FString::Printf(TEXT("success=%d reload=%d"), bSuccess, bReload));
    IFileManager::Get().MakeDirectory(*Directory(), true);
    FFileHelper::SaveStringArrayToFile(Evidence, *(Directory() / (bReload ? TEXT("Reload.txt") : TEXT("Check.txt"))));
    UE_LOG(LogTemp, Display, TEXT("CITY_SETTINGS_FINISH mode=%s success=%d detail=%s"),
        bReload ? TEXT("Reload") : TEXT("Check"), bSuccess, *Detail);
    FPlatformMisc::RequestExitWithStatus(false, bSuccess ? 0 : 1);
}
