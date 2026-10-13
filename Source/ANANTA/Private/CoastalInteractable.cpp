#include "CoastalInteractable.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"

ACoastalInteractable::ACoastalInteractable()
{
    PrimaryActorTick.bCanEverTick = false;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Pivot"));
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(RootComponent);
    Mesh->SetMobility(EComponentMobility::Movable);
}

void ACoastalInteractable::BeginPlay()
{
    Super::BeginPlay();
    ClosedRotation = GetActorRotation();
}

FString ACoastalInteractable::Use()
{
    if (Kind == 1)
    {
        bUsed = !bUsed;
        SetActorRotation(ClosedRotation + FRotator(0, bUsed ? 95 : 0, 0));
        return bUsed ? TEXT("Door opened") : TEXT("Door closed");
    }
    if (Kind == 3)
    {
        if (bUsed)
        {
            return TEXT("Already collected");
        }
        Mesh->SetVisibility(false);
        Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
    bUsed = true;
    return Message;
}
