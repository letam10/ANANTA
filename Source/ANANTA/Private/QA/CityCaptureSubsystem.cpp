#include "QA/CityCaptureSubsystem.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "City/ANANTACityController.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"

namespace
{
    void WriteCityRenderConfiguration(const FString& Directory, const FString& MapName)
    {
        static const TCHAR* Names[] = {
            TEXT("sg.ResolutionQuality"), TEXT("sg.ShadowQuality"), TEXT("sg.GlobalIlluminationQuality"),
            TEXT("sg.ReflectionQuality"), TEXT("r.ScreenPercentage"), TEXT("r.AntiAliasingMethod"),
            TEXT("r.AllowOcclusionQueries"), TEXT("r.HZBOcclusion"), TEXT("r.Nanite"),
            TEXT("r.Nanite.Culling.Frustum"), TEXT("r.Nanite.Culling.HZB"),
            TEXT("r.Nanite.AsyncRasterization"), TEXT("r.Nanite.AsyncRasterization.ShadowDepths"),
            TEXT("r.DynamicGlobalIlluminationMethod"), TEXT("r.ReflectionMethod"), TEXT("r.RayTracing"),
            TEXT("r.Lumen.HardwareRayTracing"), TEXT("r.Lumen.ScreenProbeGather.DownsampleFactor"),
            TEXT("r.Lumen.Reflections.DownsampleFactor"), TEXT("r.Shadow.Virtual.Enable"),
            TEXT("r.Shadow.Virtual.SMRT.RayCountDirectional"), TEXT("r.Shadow.Virtual.SMRT.RayCountLocal"),
            TEXT("r.Shadow.Virtual.SMRT.SamplesPerRayDirectional"),
            TEXT("r.Shadow.Virtual.SMRT.SamplesPerRayLocal"),
            TEXT("r.TextureStreaming"), TEXT("r.Streaming.PoolSize"), TEXT("r.TSR.History.ScreenPercentage")
        };
        FString Report = FString::Printf(TEXT("map=%s\nphase=first_capture_after_ready\n"), *MapName);
        // Doc gia tri sau khi game da ap dung scalability, khong thay doi chat luong.
        for (const TCHAR* Name : Names)
        {
            const IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(Name);
            const FString Value = Variable ? Variable->GetString() : TEXT("not_registered");
            Report += FString::Printf(TEXT("%s=%s\n"), Name, *Value);
        }
        const bool bSaved = FFileHelper::SaveStringToFile(Report, *(Directory / TEXT("RenderConfig.txt")));
        UE_LOG(LogTemp, Display, TEXT("CITY_RENDER_CONFIG_SAVED success=%d"), bSaved);
    }
}

bool UCityCaptureSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && FParse::Param(FCommandLine::Get(), TEXT("CityCapture"));
#endif
}

TStatId UCityCaptureSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityCaptureSubsystem, STATGROUP_Tickables);
}

void UCityCaptureSubsystem::Tick(const float DeltaTime)
{
    if (!GetWorld() || !GetWorld()->HasBegunPlay())
    {
        return;
    }
    if (WallStart == 0)
    {
        WallStart = FPlatformTime::Seconds();
    }
    if (ViewIndex <= CaptureCount && FPlatformTime::Seconds() - WallStart > FMath::Max(180, CaptureCount * 10 + 60))
    {
        UE_LOG(LogTemp, Error, TEXT("CITY_CAPTURE_TIMEOUT view=%d"), ViewIndex);
        FinishCapture();
        ViewIndex = CaptureCount + 1;
        return;
    }
    auto* Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    if (!Controller || !Controller->CanCaptureProgress())
    {
        return;
    }
    if (Elapsed == 0)
    {
        // Giu collision duoi chan nhan vat khi camera QA chuyen sang khu khac.
        auto* Source = NewObject<UWorldPartitionStreamingSourceComponent>(Controller->GetPawn());
        Source->RegisterComponent();
        ApplyReviewLighting();
        if (!InitializePlacementViews())
        {
            ViewIndex = CaptureCount + 1;
            FPlatformMisc::RequestExitWithStatus(false, 1);
            return;
        }
    }
    Elapsed += DeltaTime;
    if (Elapsed > 8 && ViewIndex < CaptureCount)
    {
        FrameSeconds += DeltaTime;
        MaximumFrameSeconds = FMath::Max(MaximumFrameSeconds, DeltaTime);
        ++FrameSamples;
    }
    if (ViewIndex < CaptureCount && Elapsed >= 8 + ViewIndex * 6)
    {
        CaptureView(ViewIndex++);
    }
    if (ViewIndex == CaptureCount && Elapsed > 8 + CaptureCount * 6)
    {
        FinishCapture();
        ++ViewIndex;
    }
}

void UCityCaptureSubsystem::CaptureView(const int32 Index)
{
    static const FVector Locations[] = {
        FVector(-23500, 500, 230),
        FVector(-24000, -600, 220),
        FVector(-25600, 2500, 185),
        FVector(-24500, -200, 1900),
        FVector(1550, 2600, 185),
        FVector(22500, 1500, 280),
        FVector(3000, -600, 230)
    };
    static const FRotator Rotations[] = {
        FRotator(-2, 155, 0),
        FRotator(1, 0, 0),
        FRotator(-6, 165, 0),
        FRotator(-25, 145, 0),
        FRotator(-5, 5, 0),
        FRotator(1, 35, 0),
        FRotator(0, -15, 0)
    };
    static const FVector ExpansionLocations[] = {
        FVector(-46000, -6000, 3500), FVector(-37650, 2700, 185), FVector(-10100, 2500, 185),
        FVector(13700, 2550, 185), FVector(61700, 2450, 185), FVector(-74500, -74200, 1500),
        FVector(-22200, -2800, 185)
    };
    static const FRotator ExpansionRotations[] = {
        FRotator(-15, 40, 0), FRotator(-4, 175, 0), FRotator(-4, 5, 0),
        FRotator(-4, 0, 0), FRotator(-4, 0, 0), FRotator(-8, 45, 0), FRotator(-4, 0, 0)
    };
    static const FVector DressingLocations[] = {
        FVector(37700, 2500, 185), FVector(-25600, 2500, 185), FVector(1550, 2600, 185),
        FVector(-30800, 4700, 850), FVector(4600, 5000, 850), FVector(25400, 7900, 900),
        FVector(-38500, 1400, 250)
    };
    static const FRotator DressingRotations[] = {
        FRotator(-4, 0, 0), FRotator(-6, 165, 0), FRotator(-5, 5, 0),
        FRotator(-22, 42, 0), FRotator(-22, 40, 0), FRotator(-22, 45, 0), FRotator(5, 20, 0)
    };
    static const FVector FinishingLocations[] = {
        FVector(-37900, 2480, 165), FVector(2320, 2260, 185), FVector(-9720, 2230, 170),
        FVector(14180, 2440, 175), FVector(-21750, -2400, 185), FVector(37880, 2500, 185),
        FVector(62200, 2500, 185)
    };
    static const FRotator FinishingRotations[] = {
        FRotator(-8, -45, 0), FRotator(-12, -160, 0), FRotator(-6, 180, 0),
        FRotator(-10, -140, 0), FRotator(-12, -90, 0), FRotator(-10, -28, 0), FRotator(-10, -150, 0)
    };
    static const FVector FixtureLocations[] = {
        FVector(-9340, 2750, 170), FVector(-9510, 2910, 150), FVector(38670, 2860, 175),
        FVector(38550, 2880, 155), FVector(61830, 2700, 180), FVector(61830, 2900, 190),
        FVector(38380, 2910, 180)
    };
    static const FRotator FixtureRotations[] = {
        FRotator(-8, 90, 0), FRotator(-7, 60, 0), FRotator(0, 90, 0), FRotator(-18, 67, 0),
        FRotator(1, 90, 0), FRotator(0, 90, 0), FRotator(-3, 52, 0)
    };
    static const FVector CivicLocations[] = {
        FVector(-59600, 3400, 350), FVector(-47600, 3400, 350), FVector(-33900, -7200, 185),
        FVector(-21900, -7200, 185), FVector(-8300, -7600, 900), FVector(123600, -130800, 1600),
        FVector(127500, -143500, 1800)
    };
    static const FRotator CivicRotations[] = {
        FRotator(-3, 62, 0), FRotator(-3, 42, 0), FRotator(-2, 30, 0), FRotator(-2, 30, 0),
        FRotator(-15, 30, 0), FRotator(-15, 20, 0), FRotator(-16, 25, 0)
    };
    const FString Directory = GetOutputDirectory();
    IFileManager::Get().MakeDirectory(*Directory, true);
    if (Index == 0)
    {
        WriteCityRenderConfiguration(Directory, GetWorld()->GetMapName());
    }
    const FString Filename = Directory / FString::Printf(TEXT("View_%02d.png"), Index);
    OutputFiles.Add(Filename);
    FScreenshotRequest::RequestScreenshot(Filename, Index == 0, false, false);
    UE_LOG(LogTemp, Display, TEXT("CITY_CAPTURE_REQUEST %d %s"), Index, *Filename);
    // Doi camera sau khi anh hien tai da duoc renderer doc o cuoi frame.
    if (Index < CaptureCount - 1)
    {
        if (!PlacementViews.IsEmpty())
        {
            const FTransform Next = PlacementViews[Index + 1];
            GetWorld()->GetTimerManager().SetTimerForNextTick([this, Next]()
            {
                MoveReviewCamera(Next.GetLocation(), Next.Rotator());
            });
            return;
        }
        const bool bExpansion = FParse::Param(FCommandLine::Get(), TEXT("CityExpansionViews"));
        const bool bDressing = FParse::Param(FCommandLine::Get(), TEXT("CityDressingViews"));
        const bool bFinishing = FParse::Param(FCommandLine::Get(), TEXT("CityFinishingViews"));
        const bool bFixtures = FParse::Param(FCommandLine::Get(), TEXT("CityFixtureViews"));
        const bool bCivic = FParse::Param(FCommandLine::Get(), TEXT("CityCivicViews"));
        const FVector Location = bFinishing ? FinishingLocations[Index]
            : (bDressing ? DressingLocations[Index] : (bExpansion ? ExpansionLocations[Index] : Locations[Index]));
        const FRotator Rotation = bFinishing ? FinishingRotations[Index]
            : (bDressing ? DressingRotations[Index] : (bExpansion ? ExpansionRotations[Index] : Rotations[Index]));
        const FVector FinalLocation = bCivic ? CivicLocations[Index] : (bFixtures ? FixtureLocations[Index] : Location);
        const FRotator FinalRotation = bCivic ? CivicRotations[Index] : (bFixtures ? FixtureRotations[Index] : Rotation);
        GetWorld()->GetTimerManager().SetTimerForNextTick([this, FinalLocation, FinalRotation]()
        {
            MoveReviewCamera(FinalLocation, FinalRotation);
        });
    }
}

void UCityCaptureSubsystem::FinishCapture()
{
    bool bAllWritten = OutputFiles.Num() == CaptureCount;
    FString Report;
    for (const FString& Filename : OutputFiles)
    {
        const int64 Size = IFileManager::Get().FileSize(*Filename);
        bAllWritten &= Size > 0;
        Report += FString::Printf(TEXT("%s bytes=%lld\n"), *Filename, Size);
    }
    Report += TEXT("Visual inspection and gameplay acceptance are separate required gates.\n");
    Report += FString::Printf(TEXT("Observed frame mean_ms=%.2f max_ms=%.2f samples=%d\n"),
        FrameSamples > 0 ? FrameSeconds * 1000 / FrameSamples : 0, MaximumFrameSeconds * 1000, FrameSamples);
    Report += TEXT("Frame observations include still views, streaming and screenshots; not a gameplay benchmark.\n");
    FFileHelper::SaveStringToFile(Report, *(GetOutputDirectory() / TEXT("Capture.txt")));
    UE_LOG(LogTemp, Display, TEXT("CITY_CAPTURE_FINISH success=%d"), bAllWritten);
    FPlatformMisc::RequestExitWithStatus(false, bAllWritten ? 0 : 1);
}
