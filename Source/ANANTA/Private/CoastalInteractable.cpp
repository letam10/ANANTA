#include "CoastalInteractable.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"

ACoastalInteractable::ACoastalInteractable()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = false;
    PrimaryActorTick.TickInterval = 0.1f;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Pivot"));
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(RootComponent);
    Mesh->SetMobility(EComponentMobility::Movable);
}

void ACoastalInteractable::BeginPlay()
{
    Super::BeginPlay();
    ClosedRotation = GetActorRotation();
    if (Kind == 2 && bScheduleEnabled)
    {
        ScheduleOrigin = GetActorLocation();
        SchedulePhase = FMath::Fmod(FMath::Abs(ScheduleOrigin.X + ScheduleOrigin.Y), 628.0f) / 100.0f;
        SetActorTickEnabled(true);
    }
}

void ACoastalInteractable::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (Kind != 2 || !bScheduleEnabled)
    {
        return;
    }
    SchedulePhase += DeltaSeconds * FMath::Max(0.05f, ScheduleSpeed);
    const float Horizontal = FMath::Sin(SchedulePhase) * ScheduleRadius;
    const float Depth = FMath::Sin(SchedulePhase * 0.73f) * ScheduleRadius * 0.35f;
    SetActorLocation(ScheduleOrigin + FVector(Horizontal, Depth, 0));
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
