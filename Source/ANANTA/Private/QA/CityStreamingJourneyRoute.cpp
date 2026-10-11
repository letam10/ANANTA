#include "QA/CityStreamingJourney.h"

#include "Camera/PlayerCameraManager.h"
#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "Components/CapsuleComponent.h"
#include "Components/TraversalComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/FileManager.h"
#include "UnrealClient.h"
#include "WorldPartition/WorldPartitionSubsystem.h"

bool UCityStreamingJourney::CheckMovement(const float DeltaTime)
{
    const auto* Hero = GetHero();
    const auto* Movement = Hero->GetCharacterMovement();
    const FVector Location = Hero->GetActorLocation();
    const double Distance = FVector::Dist(Location, LastLocation);
    if (Location.ContainsNaN() || Location.Z < -100
        || Distance > FMath::Max(100.0, SprintSpeed * FMath::Max(0.f, DeltaTime) * 1.25)
        || !Hero->TraversalComponent || Hero->TraversalComponent->SprintSpeed != SprintSpeed
        || Hero->TraversalComponent->WalkSpeed != WalkSpeed || Movement->MaxWalkSpeed > SprintSpeed + 1)
    {
        Finish(false, TEXT("Unexpected displacement, fall or ordinary movement speed changed"));
        return false;
    }
    PathDistance += Distance;
    LastLocation = Location;
    const float HalfHeight = Hero->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityStreamingGround), false, Hero);
    FHitResult Floor;
    ++GroundChecks;
    if (!GetWorld()->LineTraceSingleByChannel(Floor, Location,
            Location - FVector(0, 0, HalfHeight + 50), ECC_WorldStatic, Params)
        || Floor.ImpactNormal.Z < 0.7)
    {
        Finish(false, TEXT("No walkable ground collision within 50 cm of the feet"));
        return false;
    }
    // Cho phep roi rat ngan khi buoc xuong mep via he 15 cm, nhung khong chap nhan roi tu do.
    if (!Movement->IsMovingOnGround())
    {
        if (AirborneStart == 0)
        {
            AirborneStart = Now;
        }
        if (Now - AirborneStart > 1)
        {
            Finish(false, TEXT("Ground movement mode was lost for more than one second"));
            return false;
        }
    }
    else
    {
        AirborneStart = 0;
    }
    return true;
}

void UCityStreamingJourney::RunRoute()
{
    FVector Direction = Waypoints[Waypoint] - GetHero()->GetActorLocation();
    Direction.Z = 0;
    const double Distance = Direction.Size();
    if (Distance <= 24)
    {
        ReleaseKeys();
        Observe(FString::Printf(TEXT("reached_waypoint=%d target=%s error_cm=%.3f"),
            Waypoint, *Waypoints[Waypoint].ToString(), Distance));
        if (Waypoint >= 3)
        {
            CaptureIndex = Waypoint == 3 ? 0 : 2;
            Controller->SetControlRotation(FRotator(-12, Waypoint == 3 ? 90 : 0, 0));
            NextPhase(ECityStreamingPhase::Settle, TEXT("Endpoint reached; settling forward view"));
        }
        else
        {
            ++Waypoint;
            NextPhase(ECityStreamingPhase::Route, TEXT("Proceeding to the next adjacent route segment"));
        }
        return;
    }
    Controller->SetControlRotation(FRotator(-12, Direction.Rotation().Yaw, 0));
    SetKey(EKeys::W, true);
    SetKey(EKeys::LeftShift, Distance > 500);
    if (FVector::Dist2D(MotionOrigin, GetHero()->GetActorLocation()) > 80)
    {
        MotionOrigin = GetHero()->GetActorLocation();
        MotionTime = Now;
    }
    else if (Now - MotionTime > 8)
    {
        Finish(false, TEXT("Ordinary held-key movement stalled for eight seconds"));
    }
}

void UCityStreamingJourney::RunCapture()
{
    const double EndpointError = FVector::Dist2D(GetHero()->GetActorLocation(), Waypoints[Waypoint]);
    if (EndpointError > 60 || !HeldKeys.IsEmpty())
    {
        Finish(false, TEXT("Endpoint drift exceeded 60 cm or a movement key remained held"));
        return;
    }
    auto* Partition = GetWorld()->GetSubsystem<UWorldPartitionSubsystem>();
    const bool bStreamingComplete = Partition && Partition->IsStreamingCompleted();
    const float DesiredYaw = (Waypoint == 3 ? 90.f : 0.f) + (CaptureIndex % 2 == 1 ? 180.f : 0.f);
    const auto* Camera = Controller->PlayerCameraManager.Get();
    const bool bFacing = Camera
        && FMath::Abs(FMath::FindDeltaAngleDegrees(Camera->GetCameraRotation().Yaw, DesiredYaw)) <= 2;
    const bool bStationary = GetHero()->GetVelocity().Size() < 5
        && GetHero()->GetCharacterMovement()->IsMovingOnGround();
    if (Phase == ECityStreamingPhase::Settle)
    {
        if (!bStreamingComplete || !bStationary || !bFacing)
        {
            SettleStart = 0;
            return;
        }
        if (SettleStart == 0)
        {
            SettleStart = Now;
        }
        if (Now - SettleStart < 2 || FScreenshotRequest::IsScreenshotRequested())
        {
            return;
        }
        ++StreamingEndpoints;
        Observe(FString::Printf(TEXT("settled_view=%d streaming_complete=1 endpoint_error_cm=%.3f"),
            CaptureIndex, EndpointError));
        FScreenshotRequest::RequestScreenshot(ScreenshotPath(CaptureIndex), false, false, false);
        NextPhase(ECityStreamingPhase::Capture,
            FString::Printf(TEXT("screenshot_requested=%s"), *ScreenshotPath(CaptureIndex)));
        return;
    }
    if (!bStationary || !bFacing)
    {
        Finish(false, TEXT("Camera orientation or stationary state changed during screenshot capture"));
        return;
    }
    if (FScreenshotRequest::IsScreenshotRequested()
        || IFileManager::Get().FileSize(*ScreenshotPath(CaptureIndex)) <= 0)
    {
        return;
    }
    Observe(FString::Printf(TEXT("screenshot_written=%s bytes=%lld streaming_complete=%d"),
        *ScreenshotPath(CaptureIndex), IFileManager::Get().FileSize(*ScreenshotPath(CaptureIndex)),
        bStreamingComplete));
    if (CaptureIndex % 2 == 0)
    {
        ++CaptureIndex;
        Controller->SetControlRotation(FRotator(-12, DesiredYaw + 180, 0));
        NextPhase(ECityStreamingPhase::Settle, TEXT("Movement released; camera turned 180 degrees"));
    }
    else if (Waypoint == 3)
    {
        ++Waypoint;
        NextPhase(ECityStreamingPhase::Route, TEXT("North views saved; ordinary traversal east to northeast"));
    }
    else
    {
        bool bAllWritten = StreamingEndpoints == 4;
        for (int32 Index = 0; Index < 4; ++Index)
        {
            bAllWritten &= IFileManager::Get().FileSize(*ScreenshotPath(Index)) > 0;
        }
        Finish(bAllWritten, bAllWritten ? TEXT("Both endpoints reached and all four settled views saved")
            : TEXT("Missing screenshot or settled streaming endpoint evidence"));
    }
}
