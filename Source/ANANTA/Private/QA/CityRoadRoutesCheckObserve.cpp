#include "QA/CityRoadRoutesCheck.h"

#include "City/Mobility/CityRouteVehicle.h"
#include "Components/BoxComponent.h"
#include "Engine/World.h"

void UCityRoadRoutesCheck::Observe(FCityRoadResult& Result, FCityRoadProbe& Probe, const double Now)
{
    if (Probe.Status != TEXT("PENDING"))
    {
        return;
    }
    Probe.Elapsed = Now - ReadyAt;
    auto Fail = [&Probe](const FString& Reason)
    {
        Probe.Status = TEXT("FAIL");
        Probe.Reason = Reason;
    };
    if (!Probe.Vehicle.IsValid())
    {
        Fail(TEXT("Fixture vehicle disappeared"));
        return;
    }
    const auto* Vehicle = Probe.Vehicle.Get();
    const FVector Position = Vehicle->GetActorLocation();
    const auto* Body = Cast<UBoxComponent>(Vehicle->GetRootComponent());
    if (Position.ContainsNaN() || !Vehicle->GetActorEnableCollision() || !Body
        || !Body->IsQueryCollisionEnabled() || Body->GetCollisionResponseToChannel(ECC_WorldStatic) != ECR_Block
        || Body->GetCollisionResponseToChannel(ECC_WorldDynamic) != ECR_Block)
    {
        Fail(TEXT("Invalid position or missing blocking vehicle collision"));
        return;
    }
    FVector FlatPosition = Position;
    FlatPosition.Z = 0;
    double Nearest = TNumericLimits<double>::Max();
    for (int32 Point = 0; Point < Result.Route.Points.Num(); ++Point)
    {
        const FVector A = Result.Route.Points[Point];
        const FVector B = Result.Route.Points[(Point + 1) % Result.Route.Points.Num()];
        Nearest = FMath::Min(Nearest, FVector::Dist(FlatPosition,
            FMath::ClosestPointOnSegment(FlatPosition, A, B)));
        if (FVector::Dist2D(Position, A) < 200)
        {
            Probe.PointMask |= 1 << Point;
        }
    }
    Probe.MaxDeviation = FMath::Max(Probe.MaxDeviation, Nearest);
    if (Nearest > 100)
    {
        Fail(TEXT("Vehicle left the authored road lane centre path by more than 100 cm"));
        return;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRoadQASupport), false, Vehicle);
    if (GetWorld()->OverlapBlockingTestByChannel(Position, Vehicle->GetActorQuat(), ECC_WorldDynamic,
        FCollisionShape::MakeBox(Body->GetScaledBoxExtent()), Params))
    {
        Fail(TEXT("Vehicle body penetrates a blocking object on the authored route"));
        return;
    }
    FHitResult Floor;
    if (!GetWorld()->LineTraceSingleByObjectType(Floor, Position + FVector(0, 0, 400),
        Position - FVector(0, 0, 1600), FCollisionObjectQueryParams(ECC_WorldStatic), Params)
        || Floor.ImpactNormal.Z < 0.85)
    {
        Fail(TEXT("Vehicle lacks actual loaded road floor support"));
        return;
    }
    const double FloorGap = FMath::Abs(Position.Z - Probe.OriginHeight - Floor.ImpactPoint.Z);
    Probe.MaxFloorGap = FMath::Max(Probe.MaxFloorGap, FloorGap);
    if (FloorGap > 10 || Position.Z < -100)
    {
        Fail(TEXT("Vehicle fell below road or detached from the supporting floor"));
        return;
    }
    const FVector Motion = Position - Probe.Previous;
    const double Step = Motion.Size2D();
    Probe.Travel += Step;
    if (Step > 0.1)
    {
        const int32 Side = FMath::Abs(Motion.X) > FMath::Abs(Motion.Y)
            ? (Motion.X > 0 ? 0 : 2) : (Motion.Y > 0 ? 1 : 3);
        Probe.SideTravel[Side] += Step;
    }
    Probe.Previous = Position;
    const int32 Boarded = Vehicle->GetBoardingCount();
    const int32 Alighted = Vehicle->GetAlightingCount();
    if (Step > 0.1 || Boarded != Probe.Boarded || Alighted != Probe.Alighted)
    {
        Probe.LastProgressAt = Now;
    }
    if (!Vehicle->GetBlockedReason().IsEmpty())
    {
        Probe.LastBlocker = Vehicle->GetBlockedReason();
    }
    if (Boarded != Probe.Boarded || Alighted != Probe.Alighted)
    {
        int32 StopIndex = INDEX_NONE;
        for (int32 Stop = 0; Stop < Result.Route.Stops.Num(); ++Stop)
        {
            if (FVector::Dist2D(Position, Result.Route.Points[Result.Route.Stops[Stop]]) < 200)
            {
                StopIndex = Stop;
            }
        }
        if (!Vehicle->IsStopped() || StopIndex == INDEX_NONE || Boarded < Probe.Boarded
            || Alighted < Probe.Alighted || Boarded - Probe.Boarded > 1 || Alighted - Probe.Alighted > 1)
        {
            Fail(TEXT("Passenger count changed away from a stopped authored stop or skipped observations"));
            return;
        }
        if (Boarded > Probe.Boarded)
        {
            Probe.BoardedMask |= 1 << StopIndex;
        }
        if (Alighted > Probe.Alighted)
        {
            Probe.AlightedMask |= 1 << StopIndex;
        }
    }
    Probe.Boarded = Boarded;
    Probe.Alighted = Alighted;
    Probe.StartDistance = FVector::Dist2D(Position, Result.Route.Points[Probe.InitialPoint]);
    bool bAllSides = true;
    for (const double Distance : Probe.SideTravel)
    {
        bAllSides &= Distance > 10000;
    }
    Probe.bReturned = bAllSides && Probe.PointMask == 255 && Probe.StartDistance < 200 && Vehicle->IsStopped();
    if (Probe.bReturned && Probe.Boarded >= 2 && Probe.Alighted >= 2)
    {
        Probe.Status = TEXT("PASS");
        Probe.Reason = TEXT("Full ordinary-speed loop, both passenger cycles, all sides, return and floor verified");
    }
    else if (Now - Probe.LastProgressAt > 35)
    {
        Fail(TEXT("No movement or passenger progress for 35 seconds; blocker: ") + Probe.LastBlocker);
    }
}
