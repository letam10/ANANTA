#include "City/Mobility/CityRouteVehicle.h"

#include "City/Mobility/CityTransitPassenger.h"
#include "Engine/World.h"

bool ACityRouteVehicle::DoorAndSidewalk(FVector& Door, FVector& Sidewalk) const
{
    Door = GetActorLocation() + GetActorRightVector() * (Route.bRail ? 430.f : Extent.Y + 65);
    Sidewalk = GetActorLocation()
        + GetActorRightVector() * (Route.bRail ? 800.f : (Route.bWater ? Extent.Y + 320 : 730));
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRouteStop), false, this);
    Params.AddIgnoredActor(Passenger);
    const FCollisionObjectQueryParams Objects(ECC_WorldStatic);
    const float SurfaceZ = GetActorLocation().Z - OriginHeight;
    const float AllowedRise = Route.bWater || Route.bRail ? 180.f : 40.f;
    for (FVector* Position : {&Door, &Sidewalk})
    {
        // Do tu cao do mat chay de tim san duoi mai, khong bat nham noc mai san ga.
        const FVector TraceStart(Position->X, Position->Y, SurfaceZ + AllowedRise + 1.f);
        FHitResult Floor;
        if (!GetWorld()->LineTraceSingleByObjectType(Floor, TraceStart,
            *Position - FVector(0, 0, 1500), Objects, Params) || Floor.ImpactNormal.Z < 0.8f)
        {
            return false;
        }
        // Khong dung noc vat can lam san len xe; mat ben tau co the cao hon mat nuoc.
        if (Floor.ImpactPoint.Z - SurfaceZ > AllowedRise || Floor.ImpactPoint.Z - SurfaceZ < -40.f)
        {
            return false;
        }
        Position->Z = Floor.ImpactPoint.Z + 95;
        if (GetWorld()->OverlapBlockingTestByChannel(*Position, FQuat::Identity, ECC_Pawn,
            FCollisionShape::MakeCapsule(32, 92), Params))
        {
            return false;
        }
    }
    FHitResult Passage;
    FVector ClearanceStart = Door;
    FVector ClearanceEnd = Sidewalk;
    // CharacterMovement buoc qua le duong 18 cm; khong nham no voi buc tuong chan loi len xe.
    ClearanceStart.Z = ClearanceEnd.Z = FMath::Max(Door.Z, Sidewalk.Z) + 5;
    return !GetWorld()->SweepSingleByChannel(Passage, ClearanceStart, ClearanceEnd, FQuat::Identity, ECC_Pawn,
        FCollisionShape::MakeCapsule(32, 92), Params);
}

void ACityRouteVehicle::ServiceStop(const float DeltaTime)
{
    StopElapsed += DeltaTime;
    if (!bServiced)
    {
        FVector Door;
        FVector Sidewalk;
        if (DoorAndSidewalk(Door, Sidewalk))
        {
            if (IsValid(Passenger) && Passenger->GetPhase() == ECityPassengerPhase::Seated)
            {
                bServiced = Passenger->Alight(Door, Sidewalk);
            }
            else
            {
                FActorSpawnParameters Params;
                Params.Owner = this;
                Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::DontSpawnIfColliding;
                Passenger = GetWorld()->SpawnActor<ACityTransitPassenger>(Sidewalk,
                    (Door - Sidewalk).Rotation(), Params);
                if (Passenger)
                {
                    Passenger->Approach(this, Door);
                    bServiced = true;
                }
            }
        }
    }
    const bool bPassengerReady = bServiced && (!IsValid(Passenger)
        || Passenger->GetPhase() == ECityPassengerPhase::Seated
        || Passenger->GetPhase() == ECityPassengerPhase::Finished);
    if ((StopElapsed > 4 && bPassengerReady) || StopElapsed > 24)
    {
        // Neu loi vao bi chan thi huy luot, khong keo NPC dang di theo xe.
        if (IsValid(Passenger) && Passenger->GetPhase() == ECityPassengerPhase::Approaching)
        {
            Passenger->Destroy();
        }
        bStopped = false;
    }
}

void ACityRouteVehicle::RecordBoarding()
{
    ++BoardingCount;
    UE_LOG(LogTemp, Display, TEXT("CITY_NPC_BOARDED kind=%s route=%s count=%d"),
        CityMobility::MeshName(Kind), *Route.Id.ToString(), BoardingCount);
}

void ACityRouteVehicle::RecordAlighting()
{
    ++AlightingCount;
    UE_LOG(LogTemp, Display, TEXT("CITY_NPC_ALIGHTED kind=%s route=%s count=%d"),
        CityMobility::MeshName(Kind), *Route.Id.ToString(), AlightingCount);
}
