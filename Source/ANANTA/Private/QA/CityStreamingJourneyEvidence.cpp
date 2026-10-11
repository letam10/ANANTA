#include "QA/CityStreamingJourney.h"

#include "Camera/PlayerCameraManager.h"
#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

FString UCityStreamingJourney::EvidenceDirectory() const
{
    return FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir() / TEXT("QA/CityStreamingJourney"));
}

FString UCityStreamingJourney::ScreenshotPath(const int32 Index) const
{
    static const TCHAR* Names[] = {
        TEXT("NorthForward.png"), TEXT("NorthReverse.png"),
        TEXT("NorthEastForward.png"), TEXT("NorthEastReverse.png")
    };
    return EvidenceDirectory() / Names[Index];
}

void UCityStreamingJourney::NextPhase(const ECityStreamingPhase Next, const FString& Detail)
{
    ReleaseKeys();
    Phase = Next;
    PhaseStart = Now;
    SettleStart = 0;
    MotionTime = Now;
    MotionOrigin = GetHero() ? GetHero()->GetActorLocation() : FVector::ZeroVector;
    Observe(Detail);
    if (!WriteReport(false, false))
    {
        Finish(false, TEXT("Cannot persist phase evidence"));
    }
}

void UCityStreamingJourney::Observe(const FString& Detail)
{
    static const TCHAR* Names[] = { TEXT("WaitReady"), TEXT("Route"), TEXT("Settle"), TEXT("Capture") };
    const auto* Hero = GetHero();
    FString Entry = FString::Printf(TEXT("wall_seconds=%.3f phase=%s waypoint=%d view=%d detail=%s\n"),
        Now - StartTime, Names[static_cast<uint8>(Phase)], Waypoint, CaptureIndex, *Detail);
    Entry += FString::Printf(TEXT("player_position=%s held_keys=%d path_distance_cm=%.3f\n"),
        Hero ? *Hero->GetActorLocation().ToString() : TEXT("missing"), HeldKeys.Num(), PathDistance);
    if (Controller.IsValid() && Controller->PlayerCameraManager)
    {
        const auto* Camera = Controller->PlayerCameraManager.Get();
        Entry += FString::Printf(TEXT("control_rotation=%s camera_rotation=%s camera_position=%s\n"),
            *Controller->GetControlRotation().ToString(), *Camera->GetCameraRotation().ToString(),
            *Camera->GetCameraLocation().ToString());
    }
    Observations.Add(Entry);
    UE_LOG(LogTemp, Display, TEXT("CITY_STREAMING_JOURNEY %s"), *Entry);
}

bool UCityStreamingJourney::WriteReport(const bool bComplete, const bool bPass) const
{
    IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
    FString Report = TEXT("ANANTA expanded city ordinary traversal\n");
    Report += FString::Printf(TEXT("complete=%d\nsuccess=%d\nprocess_id=%u\nelapsed_wall_seconds=%.3f\n"),
        bComplete, bPass, FPlatformProcess::GetCurrentProcessId(), Now - StartTime);
    Report += TEXT("maximum_wall_seconds=300\ninput_source=PlayerController.InputKey\nkeys=W,LeftShift\n");
    Report += TEXT("camera_control=SetControlRotation\nteleport=false\nspeed_override=false\nbenchmark=false\n");
    Report += TEXT("save_slot=ANANTA_City_QA\nnormal_save_io=false\nendpoint_tolerance_cm=60\n");
    Report += FString::Printf(TEXT("map=%s\nheld_keys_after_cleanup=%d\nsettled_streaming_views=%d\n"),
        GetWorld() ? *GetWorld()->GetMapName() : TEXT("missing"), HeldKeys.Num(), StreamingEndpoints);
    Report += FString::Printf(TEXT("initial_position=%s\nlast_position=%s\n"),
        *InitialLocation.ToString(), *LastLocation.ToString());
    Report += FString::Printf(TEXT("total_displacement_cm=%.3f\npath_distance_cm=%.3f\nplanned_route_cm=%.3f\n"),
        FVector::Dist(InitialLocation, LastLocation), PathDistance, PlannedDistance);
    Report += FString::Printf(TEXT("ground_collision_checks=%.0f\nwalk_speed_cm_s=%.3f\nsprint_speed_cm_s=%.3f\n"),
        GroundChecks, WalkSpeed, SprintSpeed);
    Report += TEXT("ground_trace=ECC_WorldStatic; hero ignored; feet clearance <=50 cm; normal_z >=0.7\n");
    Report += TEXT("streaming_api=UWorldPartitionSubsystem.IsStreamingCompleted()\n");
    double Total = 0;
    double MaxGap = 0;
    int32 Over33 = 0;
    int32 Over50 = 0;
    for (const double Interval : FrameMilliseconds)
    {
        Total += Interval;
        MaxGap = FMath::Max(MaxGap, Interval);
        Over33 += Interval > 33.3 ? 1 : 0;
        Over50 += Interval > 50 ? 1 : 0;
    }
    TArray<double> Sorted = FrameMilliseconds;
    Sorted.Sort();
    const int32 Count = Sorted.Num();
    const double P95 = Count > 0 ? Sorted[FMath::CeilToInt(Count * 0.95) - 1] : 0;
    Report += FString::Printf(TEXT("frame_samples=%d\nmean_ms=%.3f\np95_ms=%.3f\nmax_gap_ms=%.3f\n"),
        Count, Count > 0 ? Total / Count : 0, P95, MaxGap);
    Report += FString::Printf(TEXT("over_33_3_ms=%d\nover_50_ms=%d\n"), Over33, Over50);
    Report += TEXT("frame_scope=Wall intervals after readiness, including streaming and screenshot work\n");
    Report += TEXT("stable_60fps_proven=false\nperfect_culling_proven=false\nvisual_acceptance_proven=false\n");
    for (int32 Index = 0; Index < 4; ++Index)
    {
        Report += FString::Printf(TEXT("screenshot=%s bytes=%lld\n"),
            *ScreenshotPath(Index), IFileManager::Get().FileSize(*ScreenshotPath(Index)));
    }
    Report += TEXT("\nHeld-key event provenance\n") + FString::Join(InputEvents, TEXT("\n"));
    Report += TEXT("\n\nObserved endpoint positions and cameras\n") + FString::Join(Observations, TEXT("\n"));
    return FFileHelper::SaveStringToFile(Report, *(EvidenceDirectory() / TEXT("Report.txt")));
}

void UCityStreamingJourney::Finish(const bool bPass, const FString& Detail)
{
    if (bFinished)
    {
        return;
    }
    ReleaseKeys();
    Observe(Detail);
    bFinished = true;
    bPassed = bPass;
    if (!WriteReport(true, bPassed))
    {
        bPassed = false;
        UE_LOG(LogTemp, Error, TEXT("CITY_STREAMING_JOURNEY evidence write failed"));
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_STREAMING_JOURNEY_FINISH success=%d"), bPassed);
}
