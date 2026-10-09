#include "QA/CityGraphicsObservation.h"

#include "City/ANANTACityController.h"
#include "DynamicRHI.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "RenderTimer.h"
#include "Settings/ANANTAGraphicsSettings.h"

bool UCityGraphicsObservation::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && FParse::Param(FCommandLine::Get(), TEXT("CityObserveGraphics"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityGraphicsObservation::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityGraphicsObservation, STATGROUP_Tickables);
}

void UCityGraphicsObservation::Tick(float DeltaTime)
{
    const auto* PC = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    if (!PC || !PC->CanCaptureProgress() || !PC->GetPawn() || PC->IsPaused())
    {
        LastTime = 0;
        return;
    }
    const double Now = FPlatformTime::Seconds();
    if (!bConfigured)
    {
        RecordConfiguration();
        bConfigured = true;
        FirstTime = Now;
        Rows.Add(TEXT("elapsed_s,wall_ms,game_ms,render_ms,rhi_ms,gpu_ms,x_cm,y_cm"));
    }
    if (LastTime > 0)
    {
        const FVector Location = PC->GetPawn()->GetActorLocation();
        Rows.Add(FString::Printf(TEXT("%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.1f,%.1f"),
            Now - FirstTime, (Now - LastTime) * 1000, FPlatformTime::ToMilliseconds(GGameThreadTime),
            FPlatformTime::ToMilliseconds(GRenderThreadTime), FPlatformTime::ToMilliseconds(GRHIThreadTime),
            FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles()), Location.X, Location.Y));
    }
    LastTime = Now;
    if (!bProfileRequested && Now - FirstTime > 20
        && FParse::Param(FCommandLine::Get(), TEXT("CityProfileRender")))
    {
        bProfileRequested = true;
        GEngine->Exec(GetWorld(), TEXT("r.ProfileGPU.ShowUI 0"));
        GEngine->Exec(GetWorld(), TEXT("r.ProfileGPU.Sort 1"));
        GEngine->Exec(GetWorld(), TEXT("ProfileGPU"));
    }
}

void UCityGraphicsObservation::RecordConfiguration()
{
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityMaxGraphics");
    IFileManager::Get().MakeDirectory(*Directory, true);
    TArray<FString> Lines;
    Lines.Add(TEXT("Ordinary service gameplay observation. No benchmark. CPU/GPU counters can lag a frame."));
    static const TCHAR* Names[] = {
        TEXT("sg.ViewDistanceQuality"), TEXT("sg.AntiAliasingQuality"), TEXT("sg.ShadowQuality"),
        TEXT("sg.GlobalIlluminationQuality"), TEXT("sg.ReflectionQuality"), TEXT("sg.PostProcessQuality"),
        TEXT("sg.TextureQuality"), TEXT("sg.EffectsQuality"), TEXT("sg.FoliageQuality"),
        TEXT("sg.ShadingQuality"), TEXT("r.ScreenPercentage"), TEXT("t.MaxFPS"), TEXT("r.VSync"),
        TEXT("r.Nanite.Culling.Frustum"), TEXT("r.Nanite.Culling.HZB"), TEXT("r.Streaming.PoolSize"),
        TEXT("r.Lumen.HardwareRayTracing"), TEXT("r.Shadow.Virtual.SMRT.RayCountDirectional"),
        TEXT("r.Shadow.Virtual.Enable"), TEXT("r.Shadow.Virtual.ResolutionLodBiasDirectional"),
        TEXT("r.Shadow.Virtual.NonNanite.Batch"), TEXT("r.Shadow.Virtual.NonNanite.UseHZB"),
        TEXT("r.Shadow.Virtual.NonNanite.IncludeInCoarsePages"), TEXT("r.TSR.History.ScreenPercentage")
    };
    for (const TCHAR* Name : Names)
    {
        const auto* Variable = IConsoleManager::Get().FindConsoleVariable(Name);
        Lines.Add(FString::Printf(TEXT("%s=%s"), Name, Variable ? *Variable->GetString() : TEXT("MISSING")));
    }
    if (const auto* Settings = UANANTAGraphicsSettings::Get())
    {
        Lines.Add(FString::Printf(TEXT("output=%dx%d"), Settings->GetScreenResolution().X,
            Settings->GetScreenResolution().Y));
    }
    FFileHelper::SaveStringArrayToFile(Lines, *(Directory / TEXT("RenderConfig.txt")));
}

void UCityGraphicsObservation::Deinitialize()
{
    const FString Path = FPaths::ProjectSavedDir() / TEXT("QA/CityMaxGraphics/FrameTimes.csv");
    if (Rows.Num() > 1)
    {
        FFileHelper::SaveStringArrayToFile(Rows, *Path);
        UE_LOG(LogTemp, Display, TEXT("CITY_GRAPHICS_OBSERVATION_WRITTEN samples=%d"), Rows.Num() - 1);
    }
    Super::Deinitialize();
}
