#include "QA/CityCaptureSubsystem.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "City/ANANTACityController.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"

namespace
{
    constexpr int32 CaptureCount = 8;
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
    if (ViewIndex <= CaptureCount && FPlatformTime::Seconds() - WallStart > 180)
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
    if (ViewIndex == CaptureCount && Elapsed > 56)
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
    const FString Directory = GetOutputDirectory();
    IFileManager::Get().MakeDirectory(*Directory, true);
    const FString Filename = Directory / FString::Printf(TEXT("View_%02d.png"), Index);
    OutputFiles.Add(Filename);
    FScreenshotRequest::RequestScreenshot(Filename, Index == 0, false, false);
    UE_LOG(LogTemp, Display, TEXT("CITY_CAPTURE_REQUEST %d %s"), Index, *Filename);
    // Doi camera sau khi anh hien tai da duoc renderer doc o cuoi frame.
    if (Index < CaptureCount - 1)
    {
        const bool bExpansion = FParse::Param(FCommandLine::Get(), TEXT("CityExpansionViews"));
        const bool bDressing = FParse::Param(FCommandLine::Get(), TEXT("CityDressingViews"));
        const FVector Location = bDressing ? DressingLocations[Index]
            : (bExpansion ? ExpansionLocations[Index] : Locations[Index]);
        const FRotator Rotation = bDressing ? DressingRotations[Index]
            : (bExpansion ? ExpansionRotations[Index] : Rotations[Index]);
        GetWorld()->GetTimerManager().SetTimerForNextTick([this, Location, Rotation]()
        {
            if (!ReviewCamera)
            {
                ReviewCamera = GetWorld()->SpawnActor<ACameraActor>();
                ReviewCamera->GetCameraComponent()->SetFieldOfView(75);
                auto* Source = NewObject<UWorldPartitionStreamingSourceComponent>(ReviewCamera);
                Source->RegisterComponent();
            }
            ReviewCamera->SetActorLocationAndRotation(Location, Rotation);
            GetWorld()->GetFirstPlayerController()->SetViewTarget(ReviewCamera);
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
