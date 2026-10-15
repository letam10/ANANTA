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
    if (Kind == 6)
    {
        SignalPhase = FMath::Fmod(FMath::Abs(GetActorLocation().X + GetActorLocation().Y), 1200.0f) / 100.0f;
        SetActorTickEnabled(true);
    }
}

void ACoastalInteractable::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (Kind != 2 || !bScheduleEnabled)
    {
        if (Kind != 6)
        {
            return;
        }
        const float Period = FMath::Max(3.0f, SignalPeriod);
        SignalPhase += DeltaSeconds;
        const float Phase = FMath::Fmod(SignalPhase, Period);
        const float GreenEnd = Period * 0.55f;
        const float YellowEnd = Period * 0.65f;
        SignalState = Phase < GreenEnd ? 0 : Phase < YellowEnd ? 1 : 2;
        const TCHAR* State = SignalState == 0 ? TEXT("Green")
            : SignalState == 1 ? TEXT("Yellow") : TEXT("Red");
        ActionName = FString::Printf(TEXT("Signal: %s"), State);
        Message = FString::Printf(TEXT("Traffic signal is %s."), State);
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
