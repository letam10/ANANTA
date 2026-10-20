#include "QA/CityGraphicsObservation.h"

#include "City/ANANTACityController.h"
#include "DynamicRHI.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/CoreDelegates.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "RenderTimer.h"
#include "Settings/ANANTAGraphicsSettings.h"
#include "GameFramework/PlayerController.h"

bool UCityGraphicsObservation::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    const FString CommandLine = FCommandLine::Get();
    // CityObserveGraphics là cờ opt-in đầy đủ; slot chỉ phân loại receipt.
    return World && World->IsGameWorld() && FParse::Param(*CommandLine, TEXT("CityObserveGraphics"));
#endif
}

void UCityGraphicsObservation::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    EnginePreExitHandle = FCoreDelegates::OnEnginePreExit.AddUObject(
        this, &UCityGraphicsObservation::HandleEnginePreExit);
}

TStatId UCityGraphicsObservation::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityGraphicsObservation, STATGROUP_Tickables);
}

void UCityGraphicsObservation::Tick(float DeltaTime)
{
    const auto* PC = GetWorld()->GetFirstPlayerController();
    const auto* CityController = Cast<AANANTACityController>(PC);
    if (!PC || !PC->GetPawn() || PC->IsPaused()
        || (CityController && !CityController->CanCaptureProgress()))
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
    if (Rows.Num() > 1 && Rows.Num() % 120 == 0)
    {
        WriteRows();
    }
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
    const FString CommandLine = FCommandLine::Get();
    Lines.Add(FString::Printf(TEXT("observation_slot=%s"),
        FParse::Param(*CommandLine, TEXT("CoastalQASlot")) ? TEXT("coastal") : TEXT("city")));
    Lines.Add(FString::Printf(TEXT("map=%s"), *GetWorld()->GetMapName()));
    static const TCHAR* Names[] = {
        TEXT("sg.ViewDistanceQuality"), TEXT("sg.AntiAliasingQuality"), TEXT("sg.ShadowQuality"),
        TEXT("sg.GlobalIlluminationQuality"), TEXT("sg.ReflectionQuality"), TEXT("sg.PostProcessQuality"),
        TEXT("sg.TextureQuality"), TEXT("sg.EffectsQuality"), TEXT("sg.FoliageQuality"),
        TEXT("sg.ShadingQuality"), TEXT("r.ScreenPercentage"), TEXT("t.MaxFPS"), TEXT("r.VSync"),
        TEXT("r.Nanite.Culling.Frustum"), TEXT("r.Nanite.Culling.HZB"), TEXT("r.Streaming.PoolSize"),
        TEXT("r.Nanite.Streaming.ReservedResources"), TEXT("r.Nanite.AsyncRasterization"),
        TEXT("r.Nanite.AsyncRasterization.ShadowDepths"),
        TEXT("r.Lumen.HardwareRayTracing"), TEXT("r.Shadow.Virtual.SMRT.RayCountDirectional"),
        TEXT("r.Shadow.Virtual.SMRT.SamplesPerRayDirectional"), TEXT("r.Shadow.Virtual.SMRT.RayCountLocal"),
        TEXT("r.Lumen.ScreenProbeGather.DownsampleFactor"), TEXT("r.Lumen.Reflections.DownsampleFactor"),
        TEXT("r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor"),
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

void UCityGraphicsObservation::WriteRows() const
{
    if (Rows.Num() <= 1)
    {
        return;
    }
    const FString Path = FPaths::ProjectSavedDir() / TEXT("QA/CityMaxGraphics/FrameTimes.csv");
    FFileHelper::SaveStringArrayToFile(Rows, *Path);
}

void UCityGraphicsObservation::Deinitialize()
{
    if (EnginePreExitHandle.IsValid())
    {
        FCoreDelegates::OnEnginePreExit.Remove(EnginePreExitHandle);
        EnginePreExitHandle.Reset();
    }
    Flush();
    Super::Deinitialize();
}

void UCityGraphicsObservation::HandleEnginePreExit()
{
    Flush();
}

void UCityGraphicsObservation::Flush()
{
    if (bFlushed)
    {
        return;
    }
    bFlushed = true;
    if (Rows.Num() > 1)
    {
        WriteRows();
        UE_LOG(LogTemp, Display, TEXT("CITY_GRAPHICS_OBSERVATION_WRITTEN samples=%d"), Rows.Num() - 1);
    }
}
