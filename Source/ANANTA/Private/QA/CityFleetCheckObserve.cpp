#include "QA/CityFleetCheck.h"

#include "City/Mobility/CityRouteVehicle.h"
#include "City/Mobility/CityTransitPassenger.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"

bool UCityFleetCheck::ObservePassenger(FCityFleetFixture& Fixture)
{
    if (!Fixture.Passenger.IsValid())
    {
        for (TActorIterator<ACityTransitPassenger> It(GetWorld()); It; ++It)
        {
            if (It->GetOwner() == Fixture.Vehicle.Get())
            {
                Fixture.Passenger = *It;
                Fixture.PassengerStart = It->GetActorLocation();
                break;
            }
        }
    }
    ACityTransitPassenger* Passenger = Fixture.Passenger.Get();
    if (!Passenger)
    {
        return true;
    }
    const ECityPassengerPhase Phase = Passenger->GetPhase();
    if (Phase == ECityPassengerPhase::Seated)
    {
        if (Passenger->GetActorEnableCollision() || Passenger->GetAttachParentActor() != Fixture.Vehicle.Get())
        {
            Finish(false, Fixture.Name + TEXT(": seated passenger lacks safe attachment/collision state"));
            return false;
        }
        Fixture.bSeated = true;
        return true;
    }
    const FVector Position = Passenger->GetActorLocation();
    if (!Passenger->GetActorEnableCollision() || Passenger->IsHidden()
        || !Passenger->GetMesh()->GetSkeletalMeshAsset())
    {
        Finish(false, Fixture.Name + TEXT(": walking passenger must be visible with active collision and mesh"));
        return false;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityFleetPassenger), false, Passenger);
    const UCapsuleComponent* Capsule = Passenger->GetCapsuleComponent();
    const FCollisionShape Shape = FCollisionShape::MakeCapsule(
        Capsule->GetScaledCapsuleRadius() - 2, Capsule->GetScaledCapsuleHalfHeight() - 2);
    if (GetWorld()->OverlapBlockingTestByChannel(Position, FQuat::Identity, ECC_Pawn, Shape, Params))
    {
        Finish(false, Fixture.Name + TEXT(": walking passenger penetrated fixture geometry"));
        return false;
    }
    FHitResult Floor;
    if (!GetWorld()->LineTraceSingleByObjectType(Floor, Position, Position - FVector(0, 0, 150),
        FCollisionObjectQueryParams(ECC_WorldStatic), Params) || Floor.ImpactNormal.Z < .8f
        || Position.Z - Floor.ImpactPoint.Z < Capsule->GetScaledCapsuleHalfHeight() - 3)
    {
        Finish(false, Fixture.Name + TEXT(": walking passenger lost clear supported floor/pier"));
        return false;
    }
    ++Fixture.WalkingChecks;
    if (Phase == ECityPassengerPhase::Approaching)
    {
        Fixture.bApproached |= FVector::Dist2D(Position, Fixture.PassengerStart) > 100;
    }
    if (Phase == ECityPassengerPhase::Alighting && !Fixture.bAlighted)
    {
        Fixture.bAlighted = true;
        Fixture.AlightStart = Position;
    }
    if (Phase == ECityPassengerPhase::Finished
        && (!Fixture.bAlighted || FVector::Dist2D(Position, Fixture.AlightStart) < 100))
    {
        Finish(false, Fixture.Name + TEXT(": alighting skipped observable walking distance"));
        return false;
    }
    return true;
}

bool UCityFleetCheck::UpdateFixture(FCityFleetFixture& Fixture, const float DeltaTime)
{
    if (Fixture.Stage == 4)
    {
        return true;
    }
    if (Fixture.Stage == 3)
    {
        if (Fixture.Vehicle.IsValid() && !Fixture.Vehicle->IsActorBeingDestroyed())
        {
            Finish(false, Fixture.Name + TEXT(": vehicle destruction failed"));
            return false;
        }
        if (Fixture.Passenger.IsValid() && !Fixture.Passenger->IsActorBeingDestroyed())
        {
            Finish(false, Fixture.Name + TEXT(": vehicle destruction leaked its passenger"));
            return false;
        }
        Fixture.Stage = 4;
        const FString Row = FString::Printf(
            TEXT("kind=%s passed=1 doorBlocked=1 laneBlocked=1 boarded=1 travelCm=%.1f ")
            TEXT("alighted=1 cleanup=1 walkingChecks=%d\n"), *Fixture.Name, Fixture.Travel, Fixture.WalkingChecks);
        Evidence += Row;
        UE_LOG(LogTemp, Display, TEXT("CITY_FLEET_FIXTURE_PASS %s"), *Row.TrimEnd());
        return true;
    }
    Fixture.Elapsed += DeltaTime;
    ACityRouteVehicle* Vehicle = Fixture.Vehicle.Get();
    if (!Vehicle || Fixture.Elapsed > 120)
    {
        Finish(false, FString::Printf(TEXT("%s: vehicle missing or fixture timeout at stage %d"),
            *Fixture.Name, Fixture.Stage));
        return false;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityFleetBody), false, Vehicle);
    if (GetWorld()->OverlapBlockingTestByChannel(Vehicle->GetActorLocation(), Vehicle->GetActorQuat(),
        ECC_WorldDynamic, FCollisionShape::MakeBox(Fixture.Extent - FVector(1)), Params))
    {
        Finish(false, Fixture.Name + TEXT(": moving body penetrated road/pier/obstruction"));
        return false;
    }
    Fixture.Travel = FVector::Dist2D(Fixture.Start, Vehicle->GetActorLocation());
    if (!ObservePassenger(Fixture))
    {
        return false;
    }
    if (Fixture.Stage == 0)
    {
        if (Vehicle->GetBoardingCount() != 0 || Fixture.Passenger.IsValid() || Fixture.Travel > 1)
        {
            Finish(false, Fixture.Name + TEXT(": blocked door admitted a passenger or moved vehicle"));
            return false;
        }
        if (Fixture.Elapsed > 1.5f)
        {
            Fixture.DoorBlocker->Destroy();
            Fixture.Stage = 1;
        }
    }
    else if (Fixture.Stage == 1 && !Vehicle->IsStopped())
    {
        if (!Fixture.bApproached || !Fixture.bSeated || Vehicle->GetBoardingCount() != 1)
        {
            Finish(false, Fixture.Name + TEXT(": vehicle departed without completing observed boarding"));
            return false;
        }
        Fixture.BlockedElapsed += DeltaTime;
        if (Fixture.Travel > 60)
        {
            Finish(false, Fixture.Name + TEXT(": vehicle crossed the blocking lane fixture"));
            return false;
        }
        if (Fixture.BlockedElapsed > 1.5f)
        {
            Fixture.LaneBlocker->Destroy();
            Fixture.Stage = 2;
        }
    }
    else if (Fixture.Stage == 2 && Vehicle->GetAlightingCount() == 1)
    {
        if (!Fixture.bAlighted || Fixture.Travel < 4900 || Fixture.WalkingChecks < 10)
        {
            Finish(false, Fixture.Name + TEXT(": travel/alighting evidence incomplete"));
            return false;
        }
        Vehicle->Destroy();
        Fixture.Stage = 3;
    }
    return true;
}
