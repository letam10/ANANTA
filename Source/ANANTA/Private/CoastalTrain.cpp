#include "CoastalTrain.h"

#include "Components/StaticMeshComponent.h"

ACoastalTrain::ACoastalTrain()
{
    PrimaryActorTick.bCanEverTick = true;
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Train"));
    RootComponent = Mesh;
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
}

void ACoastalTrain::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (Dwell > 0)
    {
        Dwell -= DeltaSeconds;
        return;
    }
    FVector Location = GetActorLocation();
    const float Previous = Location.X;
    Location.X += Direction * 650 * DeltaSeconds;
    if (!bStoppedAtStation && Previous * Location.X <= 0)
    {
        Location.X = 0;
        Dwell = 6;
        bStoppedAtStation = true;
    }
    if (FMath::Abs(Location.X) > RouteHalfLength)
    {
        Location.X = -Direction * RouteHalfLength;
        bStoppedAtStation = false;
    }
    SetActorLocation(Location);
}
