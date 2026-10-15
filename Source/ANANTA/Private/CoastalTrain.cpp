#include "CoastalTrain.h"

#include "CoastalCharacter.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"

ACoastalTrain::ACoastalTrain()
{
    PrimaryActorTick.bCanEverTick = true;
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Train"));
    RootComponent = Mesh;
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    TrainState = ECoastalTrainState::Running;
}

void ACoastalTrain::SetSignalState(const ECoastalTrainSignalState NewState)
{
    SignalState = NewState;
    if (NewState == ECoastalTrainSignalState::Stop)
    {
        TrainState = ECoastalTrainState::Blocked;
        BlockedReason = TEXT("Rail signal requires the train to stop.");
    }
    else if (TrainState == ECoastalTrainState::Blocked)
    {
        TrainState = ECoastalTrainState::Running;
        BlockedReason.Empty();
    }
}

bool ACoastalTrain::IsAtStation(const FVector& Location) const
{
    if (StationLocation.IsNearlyZero())
    {
        return FMath::Abs(Location.X) <= FMath::Max(20.f, StationRadius);
    }
    return FVector::Dist2D(Location, StationLocation) <= FMath::Max(20.f, StationRadius);
}

void ACoastalTrain::SetBlocked(const FString& Reason)
{
    TrainState = ECoastalTrainState::Blocked;
    BlockedReason = Reason;
    UE_LOG(LogTemp, Display, TEXT("COASTAL_TRAIN_BLOCK actor=%s reason=%s"),
        *GetName(), *Reason);
}

bool ACoastalTrain::Board(ACoastalCharacter* Character)
{
    if (Passenger)
    {
        SetBlocked(TEXT("Train already has a passenger."));
        return false;
    }
    if (!Character || !Character->GetController())
    {
        SetBlocked(TEXT("A controlled character is required for boarding."));
        return false;
    }
    if (!IsStopped() || SignalState == ECoastalTrainSignalState::Stop)
    {
        SetBlocked(TEXT("Train must be stopped at a clear signal before boarding."));
        return false;
    }
    if (FVector::Dist2D(GetActorLocation(), Character->GetActorLocation()) > 500.f)
    {
        SetBlocked(TEXT("Move to the station platform before boarding."));
        return false;
    }
    Passenger = Character;
    PassengerController = Character->GetController();
    Passenger->SetActorHiddenInGame(true);
    Passenger->SetActorEnableCollision(false);
    Passenger->GetCharacterMovement()->DisableMovement();
    ++BoardingCount;
    TrainState = ECoastalTrainState::Boarding;
    BlockedReason.Empty();
    UE_LOG(LogTemp, Display, TEXT("COASTAL_TRAIN_BOARD actor=%s count=%d"),
        *GetName(), BoardingCount);
    return true;
}

bool ACoastalTrain::Alight()
{
    if (!Passenger || !PassengerController)
    {
        SetBlocked(TEXT("No passenger is available to alight."));
        return false;
    }
    const float SideOffset = 420.f;
    for (const float Side : {-1.f, 1.f})
    {
        const FVector Candidate = GetActorLocation() + GetActorRightVector() * SideOffset * Side;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(CoastalTrainAlight), false, this);
        Query.AddIgnoredActor(Passenger);
        FHitResult Floor;
        if (!GetWorld()->LineTraceSingleByChannel(Floor, Candidate + FVector(0, 0, 240),
            Candidate - FVector(0, 0, 400), ECC_Visibility, Query) || Floor.Normal.Z < 0.7f)
        {
            continue;
        }
        const FVector Exit = Floor.ImpactPoint + FVector(0, 0, 96);
        if (GetWorld()->OverlapBlockingTestByChannel(Exit, FQuat::Identity, ECC_Pawn,
            FCollisionShape::MakeCapsule(34, 90), Query))
        {
            continue;
        }
        AController* Player = PassengerController;
        Passenger->SetActorLocation(Exit);
        Passenger->SetActorHiddenInGame(false);
        Passenger->SetActorEnableCollision(true);
        Passenger->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        Player->Possess(Passenger);
        Passenger->Notify(TEXT("Train platform reached"));
        Passenger = nullptr;
        PassengerController = nullptr;
        ++AlightingCount;
        TrainState = ECoastalTrainState::Alighting;
        Dwell = FMath::Max(Dwell, StationDwellSeconds);
        BlockedReason.Empty();
        UE_LOG(LogTemp, Display, TEXT("COASTAL_TRAIN_ALIGHT actor=%s count=%d"),
            *GetName(), AlightingCount);
        return true;
    }
    SetBlocked(TEXT("No clear platform exit was found."));
    return false;
}

void ACoastalTrain::HoldAtStationForBoarding()
{
    SetSignalState(ECoastalTrainSignalState::Clear);
    const FVector Location = GetActorLocation();
    if (!StationLocation.IsNearlyZero())
    {
        SetActorLocation(FVector(StationLocation.X, StationLocation.Y, Location.Z));
    }
    else
    {
        SetActorLocation(FVector(0, Location.Y, Location.Z));
    }
    Dwell = FMath::Max(StationDwellSeconds, 1.f);
    bStoppedAtStation = true;
    TrainState = ECoastalTrainState::Stopped;
    BlockedReason.Empty();
}

void ACoastalTrain::Tick(const float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (SignalState == ECoastalTrainSignalState::Stop)
    {
        TrainState = ECoastalTrainState::Blocked;
        BlockedReason = TEXT("Rail signal requires the train to stop.");
        return;
    }
    if (Dwell > 0.f)
    {
        Dwell = FMath::Max(0.f, Dwell - DeltaSeconds);
        TrainState = ECoastalTrainState::Stopped;
        return;
    }
    const FVector Forward = GetActorForwardVector();
    if (FMath::Abs(Forward.X) < 0.5f)
    {
        SetBlocked(TEXT("Train transform is not aligned with the authored +X rail route."));
        return;
    }
    FVector Location = GetActorLocation();
    const float PreviousX = Location.X;
    const float Speed = SignalState == ECoastalTrainSignalState::Caution ? 325.f : 650.f;
    Location += Forward * Speed * DeltaSeconds;
    if (!bStoppedAtStation && PreviousX * Location.X <= 0 && IsAtStation(Location))
    {
        Location.X = 0;
        Dwell = FMath::Max(0.f, StationDwellSeconds);
        bStoppedAtStation = true;
        TrainState = ECoastalTrainState::Stopped;
    }
    if (FMath::Abs(Location.X) > RouteHalfLength)
    {
        Location.X = Forward.X > 0 ? -RouteHalfLength : RouteHalfLength;
        bStoppedAtStation = false;
    }
    FHitResult Hit;
    SetActorLocation(Location, true, &Hit);
    if (Hit.bBlockingHit)
    {
        SetBlocked(TEXT("Train route is blocked by collision geometry."));
        return;
    }
    TrainState = ECoastalTrainState::Running;
}
