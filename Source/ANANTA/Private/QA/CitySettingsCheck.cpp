#include "QA/CitySettingsCheck.h"

#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "Engine/World.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Settings/ANANTAGraphicsSettings.h"
#include "Settings/SCitySettingsPanel.h"

bool UCitySettingsCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld()
        && (FParse::Param(FCommandLine::Get(), TEXT("CitySettingsCheck"))
            || FParse::Param(FCommandLine::Get(), TEXT("CitySettingsReload")));
#endif
}

TStatId UCitySettingsCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCitySettingsCheck, STATGROUP_Tickables);
}

bool UCitySettingsCheck::Check(const bool bCondition, const FString& Detail)
{
    Evidence.Add(FString::Printf(TEXT("%s %s"), bCondition ? TEXT("PASS") : TEXT("FAIL"), *Detail));
    if (!bCondition)
    {
        Finish(false, Detail);
    }
    return bCondition;
}

void UCitySettingsCheck::Tick(float DeltaTime)
{
    if (bFinished)
    {
        return;
    }
    const double Now = FPlatformTime::Seconds();
    if (Start == 0)
    {
        Start = Now;
        StepStart = Now;
        bReload = FParse::Param(FCommandLine::Get(), TEXT("CitySettingsReload"));
        FString ConfigPath;
        const bool bIsolated = FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"))
            && FParse::Value(FCommandLine::Get(), TEXT("GameUserSettingsINI="), ConfigPath)
            && ConfigPath.Contains(TEXT("CitySettings"));
        if (!Check(bIsolated, TEXT("Requires isolated save and CitySettings config path")))
        {
            return;
        }
    }
    if (Now - Start > 90)
    {
        Finish(false, TEXT("Settings interaction timeout"));
        return;
    }
    Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    if (!Controller.IsValid() || !Controller->CanCaptureProgress() || !Controller->GetPawn())
    {
        return;
    }
    if (Now - StepStart >= 2)
    {
        RunStep();
        ++Step;
        StepStart = Now;
    }
}

void UCitySettingsCheck::RunStep()
{
    auto* Settings = UANANTAGraphicsSettings::Get();
    if (!Check(Settings != nullptr, TEXT("Custom settings class available")))
    {
        return;
    }
    if (bReload)
    {
        const auto Options = Settings->CaptureOptions();
        if (!Check(Options.Language == TEXT("vi") && Options.bShowFPS && Options.Shadows == 3
            && Options.GlobalIllumination == 3 && Options.Reflections == 3
            && FMath::IsNearlyEqual(Options.ResolutionScale, 100.f)
            && FMath::IsNearlyEqual(Options.FrameRateLimit, 90.f), TEXT("Disk settings restored in new process")))
        {
            return;
        }
        if (Step == 0)
        {
            RecordSettings();
            SendKey(EKeys::F10);
        }
        else if (Step == 1)
        {
            Capture(TEXT("ReloadMenu"));
        }
        else if (Step == 2)
        {
            ScrollMenuBottom();
        }
        else if (Step == 3)
        {
            Capture(TEXT("ReloadLanguage"));
        }
        else
        {
            SendKey(EKeys::Escape, true);
            Finish(true, TEXT("Reload verified"));
        }
        return;
    }
    switch (Step)
    {
    case 0:
    {
        auto Options = UANANTAGraphicsSettings::MakeDefaults();
        Options.bShowFPS = true;
        Settings->ApplyOptions(Options);
        PausedLocation = Controller->GetPawn()->GetActorLocation();
        SendKey(EKeys::Escape);
        break;
    }
    case 1:
    {
        if (!Check(Controller->IsSettingsOpen() && Controller->IsPaused() && Controller->bShowMouseCursor,
            TEXT("Esc opens menu, pauses world and exposes cursor")))
        {
            return;
        }
        auto Options = Settings->CaptureOptions();
        Options.Language = TEXT("en");
        Options.bShowFPS = false;
        Controller->GetSettingsPanel()->SetDraftOptions(Options);
        SendKey(EKeys::W);
        SendKey(EKeys::LeftMouseButton);
        break;
    }
    case 2:
        if (!Check(FVector::Dist(Controller->GetPawn()->GetActorLocation(), PausedLocation) < 2,
            TEXT("Movement remains blocked while menu is open")))
        {
            return;
        }
        SendKey(EKeys::Escape, true);
        break;
    case 3:
        if (!Check(!Controller->IsSettingsOpen() && !Controller->IsPaused() && !Controller->bShowMouseCursor
            && Settings->GetLanguage() == TEXT("vi") && Settings->IsFPSVisible(),
            TEXT("Escape discards draft and restores game input")))
        {
            return;
        }
        SendKey(EKeys::W, false, false);
        SendKey(EKeys::LeftMouseButton, false, false);
        SendKey(EKeys::F10);
        break;
    case 4:
    {
        auto Options = UANANTAGraphicsSettings::MakeDefaults();
        Options.ViewDistance = Options.AntiAliasing = Options.Shadows = Options.GlobalIllumination = 3;
        Options.Reflections = Options.PostProcess = Options.Textures = Options.Effects = 3;
        Options.Foliage = Options.Shading = 3;
        Options.ResolutionScale = 100;
        Options.Language = TEXT("en");
        Options.bShowFPS = true;
        Controller->GetSettingsPanel()->SetDraftOptions(Options);
        break;
    }
    case 5:
        Capture(TEXT("ApplyReview"));
        Check(ClickApply(), TEXT("Keyboard activates focused Apply button"));
        break;
    case 6:
        if (!Check(Settings->GetLanguage() == TEXT("en") && Settings->GetShadowQuality() == 3,
            TEXT("Apply changes language and actual quality")))
        {
            return;
        }
        Capture(TEXT("MenuEnglish"));
        break;
    case 7:
    {
        auto Options = Settings->CaptureOptions();
        Options.Language = TEXT("vi");
        Controller->GetSettingsPanel()->SetDraftOptions(Options);
        break;
    }
    case 8:
        Check(ClickApply(), TEXT("Apply Vietnamese through focused Slate button"));
        break;
    case 9:
        Capture(TEXT("MenuVietnamese"));
        RecordSettings();
        break;
    case 10:
        ScrollMenuBottom();
        break;
    case 11:
        Capture(TEXT("MenuLanguage"));
        break;
    case 12:
        SendKey(EKeys::F10, true);
        SendKey(EKeys::F8);
        break;
    case 13:
        if (!Check(!Settings->IsFPSVisible(), TEXT("F8 hides frame meter")))
        {
            return;
        }
        Capture(TEXT("FPSHidden"));
        break;
    case 14:
        SendKey(EKeys::F8);
        break;
    case 15:
        if (!Check(Settings->IsFPSVisible() && Controller->GetMeasuredFPS() > 0,
            TEXT("F8 restores real wall clock frame meter")))
        {
            return;
        }
        Capture(TEXT("FPSVisible"));
        break;
    default:
        Finish(true, TEXT("Menu apply, cancel, pause, language and FPS checked"));
        break;
    }
}
