#include "CoastalGameMode.h"

#include "CoastalCharacter.h"
#include "CoastalHUD.h"
#include "CoastalQA.h"
#include "GameFramework/GameUserSettings.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

ACoastalGameMode::ACoastalGameMode()
{
    DefaultPawnClass = ACoastalCharacter::StaticClass();
    HUDClass = ACoastalHUD::StaticClass();
}

void ACoastalGameMode::BeginPlay()
{
    Super::BeginPlay();
    if (UGameUserSettings* Settings = UGameUserSettings::GetGameUserSettings())
    {
        Settings->SetOverallScalabilityLevel(2);
        Settings->SetTextureQuality(3);
        Settings->SetVisualEffectQuality(2);
        Settings->SetVSyncEnabled(false);
        Settings->ApplyNonResolutionSettings();
    }
    const TPair<const TCHAR*, float> Variables[] = {
        {TEXT("r.AntiAliasingMethod"), 4},
        // 1600/1920 = 900/1080: TSR dựng lại từ ảnh 900p lên 1080p.
        {TEXT("r.ScreenPercentage"), 100.f * 900.f / 1080.f},
        {TEXT("r.Lumen.HardwareRayTracing"), 0},
        {TEXT("r.MotionBlurQuality"), 0},
        {TEXT("r.VSync"), 0},
        {TEXT("t.MaxFPS"), 60},
    };
    for (const auto& Pair : Variables)
    {
        if (IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(Pair.Key))
        {
            Variable->Set(Pair.Value, ECVF_SetByCode);
        }
    }
    UE_LOG(LogTemp, Display, TEXT("COASTAL_PROFILE High Lumen, TSR 900p/1080p, target 16.667 ms"));
    if (FParse::Param(FCommandLine::Get(), TEXT("CoastalQA")))
    {
        IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS"))->Set(0, ECVF_SetByCode);
        GetWorld()->SpawnActor<ACoastalQA>();
    }
}
