#include "City/ANANTACityCrowd.h"
#include "City/CityWorldBounds.h"

#include "City/ANANTACityPedestrian.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"

AANANTACityCrowd::AANANTACityCrowd()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 2;
}

void AANANTACityCrowd::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    const APlayerController* PC = GetWorld()->GetFirstPlayerController();
    if (PC && PC->GetPawn())
    {
        MaintainPopulation(PC->GetPawn()->GetActorLocation(), false);
    }
}

bool AANANTACityCrowd::MakeRoute(const FVector& Player, const bool bTraffic, FVector& Start, FVector& End)
{
    const bool bHorizontal = Random.RandRange(0, 1) == 0;
    const float Across = bHorizontal ? Player.Y : Player.X;
    const float Along = bHorizontal ? Player.X : Player.Y;
    constexpr float RoadSpacing = CityWorldBounds::RoadSpacing;
    constexpr float CityEdge = CityWorldBounds::RoadExtent;
    const float Road = FMath::Clamp(FMath::RoundToFloat(Across / RoadSpacing) * RoadSpacing,
        -CityEdge, CityEdge);
    if (FMath::Abs(Road - Across) > 6500)
    {
        return false;
    }
    const float Side = Random.RandRange(0, 1) ? 1.f : -1.f;
    const float Lane = Road + Side * (bTraffic ? 420.f : 1130.f);
    float StartAlong = FMath::Clamp(Along + Random.FRandRange(-5000, 5000), -CityEdge + 3000, CityEdge - 3000);
    float EndAlong = FMath::Clamp(StartAlong + Side * (bTraffic ? 8000.f : 1600.f), -CityEdge + 2000, CityEdge - 2000);
    if (!bTraffic)
    {
        // Nguoi di bo chi di tren via he giua hai nga tu, khong cat ngang toa nha.
        const float Block = FMath::FloorToFloat((StartAlong + CityEdge) / RoadSpacing) * RoadSpacing - CityEdge;
        StartAlong = FMath::Clamp(StartAlong, Block + 1550, Block + RoadSpacing - 1550);
        EndAlong = FMath::Clamp(EndAlong, Block + 1550, Block + RoadSpacing - 1550);
    }
    const float Height = bTraffic ? 70.f : 110.f;
    Start = bHorizontal ? FVector(StartAlong, Lane, Height) : FVector(Lane, StartAlong, Height);
    End = bHorizontal ? FVector(EndAlong, Lane, Height) : FVector(Lane, EndAlong, Height);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityCrowdSpawn), false, this);
    FHitResult Ground;
    if (!GetWorld()->LineTraceSingleByChannel(Ground, Start + FVector(0, 0, 100),
        Start - FVector(0, 0, 200), ECC_WorldStatic, Params) || Ground.ImpactNormal.Z < 0.8f)
    {
        return false;
    }
    Start.Z = Ground.ImpactPoint.Z + Height;
    const FCollisionShape Shape = bTraffic ? FCollisionShape::MakeBox(FVector(220, 100, 65))
        : FCollisionShape::MakeCapsule(35, 92);
    return FVector::DistSquared2D(Start, Player) > 500 * 500
        && !GetWorld()->OverlapBlockingTestByChannel(Start, (End - Start).Rotation().Quaternion(),
            ECC_Pawn, Shape, Params);
}

void AANANTACityCrowd::MaintainPopulation(const FVector& Player, const bool bTraffic)
{
    auto& Population = bTraffic ? Traffic : Pedestrians;
    for (int32 Index = Population.Num() - 1; Index >= 0; --Index)
    {
        AActor* Actor = Population[Index];
        if (!IsValid(Actor) || FVector::DistSquared2D(Actor->GetActorLocation(), Player) > 9000 * 9000)
        {
            if (IsValid(Actor))
            {
                Actor->Destroy();
            }
            Population.RemoveAtSwap(Index);
        }
    }
    const int32 Limit = bTraffic ? FMath::Clamp(TrafficLimit, 0, 6) : FMath::Clamp(PedestrianLimit, 0, 24);
    for (int32 Attempt = 0; Attempt < 12 && Population.Num() < Limit; ++Attempt)
    {
        FVector Start;
        FVector End;
        if (!MakeRoute(Player, bTraffic, Start, End))
        {
            continue;
        }
        FActorSpawnParameters Params;
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::DontSpawnIfColliding;
        if (bTraffic && TrafficMesh)
        {
            auto* Car = GetWorld()->SpawnActor<AANANTACityTraffic>(Start, (End - Start).Rotation(), Params);
            if (Car)
            {
                Car->BodyMesh->SetStaticMesh(TrafficMesh);
                Car->Destination = End;
                Population.Add(Car);
            }
        }
        else if (!bTraffic)
        {
            auto* Person = GetWorld()->SpawnActor<AANANTACityPedestrian>(Start, (End - Start).Rotation(), Params);
            if (Person)
            {
                Person->Origin = Start;
                Person->Destination = End;
                Population.Add(Person);
            }
        }
    }
}

void AANANTACityCrowd::EndPlay(const EEndPlayReason::Type Reason)
{
    for (AActor* Actor : Pedestrians)
    {
        if (IsValid(Actor))
        {
            Actor->Destroy();
        }
    }
    for (AActor* Actor : Traffic)
    {
        if (IsValid(Actor))
        {
            Actor->Destroy();
        }
    }
    Super::EndPlay(Reason);
}
