#include "City/Mobility/CityTransportManager.h"

#include "City/Mobility/CityRouteVehicle.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"

ACityTransportManager::ACityTransportManager()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 1;
}

void ACityTransportManager::BeginPlay()
{
    Super::BeginPlay();
    // Tai cung luc khoi tao, khong nap mesh dong bo moi lan camera quay.
    for (int32 Index = 0; Index < static_cast<int32>(ECityTransportKind::Count); ++Index)
    {
        const FString Path = FString::Printf(TEXT("/Game/ANANTA/City/Meshes/SM_%s.SM_%s"),
            CityMobility::MeshName(static_cast<ECityTransportKind>(Index)),
            CityMobility::MeshName(static_cast<ECityTransportKind>(Index)));
        Meshes.Add(LoadObject<UStaticMesh>(nullptr, *Path));
    }
}

void ACityTransportManager::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    const auto* PC = GetWorld()->GetFirstPlayerController();
    const APawn* Player = PC ? PC->GetPawn() : nullptr;
    if (!Player)
    {
        return;
    }
    const FVector Location = Player->GetActorLocation();
    for (int32 Index = Fleet.Num() - 1; Index >= 0; --Index)
    {
        if (!IsValid(Fleet[Index]) || FVector::Dist2D(Fleet[Index]->GetActorLocation(), Location)
            > CityMobility::RetirementDistance)
        {
            if (IsValid(Fleet[Index]))
            {
                Fleet[Index]->Destroy();
            }
            Fleet.RemoveAtSwap(Index);
        }
    }
    for (int32 Index = 0; Index < Meshes.Num() && Fleet.Num() < CityMobility::MaximumVehicles; ++Index)
    {
        const ECityTransportKind Kind = static_cast<ECityTransportKind>(Index);
        if (!Meshes[Index] || Fleet.ContainsByPredicate([Kind](const ACityRouteVehicle* Vehicle)
            { return Vehicle->GetKind() == Kind; }))
        {
            continue;
        }
        const FCityTransportRoute Route = CityMobility::MakeRoute(Kind);
        for (const int32 Stop : Route.Stops)
        {
            const float Distance = FVector::Dist2D(Route.Points[Stop], Location);
            if (Distance < 1800 || Distance > CityMobility::ActivationDistance)
            {
                continue;
            }
            auto* Vehicle = GetWorld()->SpawnActor<ACityRouteVehicle>();
            if (Vehicle && Vehicle->Configure(Kind, Route, Meshes[Index], Stop))
            {
                Fleet.Add(Vehicle);
                break;
            }
            if (Vehicle)
            {
                Vehicle->Destroy();
            }
        }
    }
}

void ACityTransportManager::EndPlay(const EEndPlayReason::Type Reason)
{
    for (ACityRouteVehicle* Vehicle : Fleet)
    {
        if (IsValid(Vehicle))
        {
            Vehicle->Destroy();
        }
    }
    Super::EndPlay(Reason);
}
