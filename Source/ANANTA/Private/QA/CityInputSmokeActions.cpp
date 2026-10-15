#include "QA/CityInputSmokeSubsystem.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACityInteractable.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"

bool UCityInputSmokeSubsystem::WalkToward(const FVector& Destination, const float Tolerance)
{
    FVector Direction = Destination - GetHero()->GetActorLocation();
    Direction.Z = 0;
    const bool bReached = Direction.SizeSquared() <= FMath::Square(Tolerance);
    SetKey(EKeys::W, !bReached);
    SetKey(EKeys::A, false);
    SetKey(EKeys::S, false);
    SetKey(EKeys::D, false);
    if (!bReached)
    {
        Controller->SetControlRotation(FRotator(-12, Direction.Rotation().Yaw, 0));
    }
    return bReached;
}

void UCityInputSmokeSubsystem::RunPhase()
{
    switch (Phase)
    {
    case ECityInputSmokePhase::WalkToGiver:
    case ECityInputSmokePhase::LeaveCafe:
    case ECityInputSmokePhase::WalkToCar:
        RunWalkingPhase();
        break;
    case ECityInputSmokePhase::StartMission:
        if (!bInputSent)
        {
            if (Controller->FindInteractionTarget() != Giver.Get())
            {
                Finish(false, TEXT("Giver is not the normal E interaction target after walking"));
                return;
            }
            TapKey(EKeys::E);
            bInputSent = true;
        }
        else if (PhaseElapsed > 0.3f)
        {
            if (GetState()->GetMissionStage() != ECityMissionStage::Investigating)
            {
                Finish(false, TEXT("Injected E did not start Investigating through the normal binding"));
                return;
            }
            NextPhase(ECityInputSmokePhase::LeaveCafe, TEXT("E reached giver and mission entered Investigating"));
        }
        break;
    case ECityInputSmokePhase::EnterCar:
    case ECityInputSmokePhase::Drive:
    case ECityInputSmokePhase::Brake:
    case ECityInputSmokePhase::ExitCar:
        RunVehiclePhase();
        break;
    case ECityInputSmokePhase::Save:
        if (!bInputSent)
        {
            SaveAttemptsBefore = GetState()->GetSaveAttemptCount();
            SavesBefore = GetState()->GetSuccessfulSaveCount();
            TapKey(EKeys::F5);
            bInputSent = true;
        }
        else if (PhaseElapsed > 0.4f)
        {
            const bool bSaved = GetState()->GetSaveAttemptCount() > SaveAttemptsBefore
                && GetState()->GetSuccessfulSaveCount() > SavesBefore && VerifySavedProgress();
            Finish(bSaved, bSaved ? TEXT("F5 saved current player, car and Investigating state to QA slot")
                : TEXT("F5 save failed or QA file did not contain the observed state and transforms"));
        }
        break;
    default:
        break;
    }
}

void UCityInputSmokeSubsystem::RunWalkingPhase()
{
    if (Phase == ECityInputSmokePhase::WalkToGiver)
    {
        if (WalkToward(Giver->GetActorLocation() + FVector(0, -220, 0), 25))
        {
            if (FVector::Dist2D(InitialLocation, GetHero()->GetActorLocation()) < 300)
            {
                Finish(false, TEXT("Walking phase produced insufficient observed displacement"));
                return;
            }
            NextPhase(ECityInputSmokePhase::StartMission, TEXT("Held W walked from spawn to the cafe giver"));
        }
        return;
    }
    if (Phase == ECityInputSmokePhase::LeaveCafe)
    {
        static const FVector Waypoints[] = {
            FVector(-25000, 2400, 120),
            FVector(-25620, 2400, 120),
            FVector(-25000, 2400, 120),
            FVector(-25000, 1500, 120),
            FVector(-25000, 1100, 120),
            FVector(-22500, 1100, 120)
        };
        if (WalkToward(Waypoints[CafeWaypoint], 35))
        {
            if (CafeWaypoint == 1)
            {
                UE_LOG(LogTemp, Display, TEXT("CITY_CAFE_THRESHOLD player=%s"),
                    *GetHero()->GetActorLocation().ToString());
            }
            ++CafeWaypoint;
            if (CafeWaypoint == UE_ARRAY_COUNT(Waypoints))
            {
                NextPhase(ECityInputSmokePhase::WalkToCar,
                    TEXT("Walked into cafe, back through entry and along street waypoints"));
            }
        }
        return;
    }
    const FVector Approach = Car->GetActorLocation() - Car->GetActorForwardVector() * 290;
    if (WalkToward(Approach, 15))
    {
        NextPhase(ECityInputSmokePhase::EnterCar, TEXT("Walked into normal vehicle interaction range"));
    }
}

void UCityInputSmokeSubsystem::RunVehiclePhase()
{
    switch (Phase)
    {
    case ECityInputSmokePhase::EnterCar:
        if (!bInputSent)
        {
            if (Controller->FindInteractionTarget() != Car.Get())
            {
                Finish(false, TEXT("PlayerCar is not the normal E interaction target"));
                return;
            }
            TapKey(EKeys::E);
            bInputSent = true;
        }
        else if (PhaseElapsed > 0.65f)
        {
            if (Controller->GetDrivenVehicle() != Car.Get() || !CheckCamera(true))
            {
                Finish(false, TEXT("E failed to enter PlayerCar or the vehicle camera remains too close"));
                return;
            }
            DriveOrigin = Car->GetActorLocation();
            DriveTarget = DriveOrigin + Car->GetActorForwardVector() * 1800;
            NextPhase(ECityInputSmokePhase::Drive, TEXT("E entered vehicle with valid camera separation"));
        }
        break;
    case ECityInputSmokePhase::Drive:
    {
        const FVector Direction = DriveTarget - Car->GetActorLocation();
        const FVector Course = (DriveTarget - DriveOrigin).GetSafeNormal2D();
        const float Remaining = FVector::DotProduct(Direction, Course);
        if (Remaining <= 400)
        {
            NextPhase(ECityInputSmokePhase::Brake, TEXT("Held W and steering keys displaced car toward waypoint"));
            return;
        }
        if (PhaseElapsed > 4 && FVector::Dist2D(DriveOrigin, Car->GetActorLocation()) < 100)
        {
            Finish(false, TEXT("Vehicle produced no meaningful displacement after normal throttle input"));
            return;
        }
        const float Turn = FMath::FindDeltaAngleDegrees(Car->GetActorRotation().Yaw, Direction.Rotation().Yaw);
        SetKey(EKeys::W, true);
        SetKey(EKeys::A, Turn < -3);
        SetKey(EKeys::D, Turn > 3);
        Controller->SetControlRotation(FRotator(-12, Car->GetActorRotation().Yaw, 0));
        break;
    }
    case ECityInputSmokePhase::Brake:
        SetKey(EKeys::SpaceBar, true);
        if (PhaseElapsed > 0.3f && Car->GetSpeedKmh() < 1)
        {
            if (FVector::Dist2D(DriveOrigin, Car->GetActorLocation()) < 800)
            {
                Finish(false, TEXT("Drive and brake completed without the required vehicle displacement"));
                return;
            }
            NextPhase(ECityInputSmokePhase::ExitCar, TEXT("Space brake reduced observed speed below 1 km/h"));
        }
        break;
    case ECityInputSmokePhase::ExitCar:
        if (!bInputSent)
        {
            TapKey(EKeys::E);
            bInputSent = true;
        }
        else if (PhaseElapsed > 0.65f)
        {
            if (Controller->GetDrivenVehicle() || !CheckSafeExit() || !CheckCamera(false))
            {
                Finish(false, TEXT("E exit failed, capsule placement is unsafe or player camera is invalid"));
                return;
            }
            NextPhase(ECityInputSmokePhase::Save, TEXT("E exited to grounded clear capsule with player camera"));
        }
        break;
    default:
        break;
    }
}
