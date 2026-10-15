#include "CoastalVehicle.h"

#include "Camera/CameraComponent.h"
#include "CoastalCharacter.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"

ACoastalVehicle::ACoastalVehicle()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = false;
    Collision = CreateDefaultSubobject<UBoxComponent>(TEXT("Collision"));
    RootComponent = Collision;
    Collision->SetBoxExtent(FVector(220, 90, 65));
    Collision->SetCollisionProfileName(TEXT("Pawn"));
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VehicleMesh"));
    Mesh->SetupAttachment(RootComponent);
    Mesh->SetRelativeLocation(FVector(0, 0, -65));
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Arm = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraArm"));
    Arm->SetupAttachment(RootComponent);
    Arm->TargetArmLength = 650;
    Arm->SetRelativeRotation(FRotator(-18, 0, 0));
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(Arm);
}

ECoastalVehicleType ACoastalVehicle::GetEffectiveVehicleType() const
{
    if (bBoat)
    {
        return ECoastalVehicleType::Rowboat;
    }
    return VehicleType;
}

float ACoastalVehicle::GetMaximumSpeed() const
{
    switch (GetEffectiveVehicleType())
    {
    case ECoastalVehicleType::Rowboat: return 300.f;
    case ECoastalVehicleType::Aircraft: return 2200.f;
    case ECoastalVehicleType::Helicopter: return 1400.f;
    case ECoastalVehicleType::Emergency: return 1800.f;
    default: return 1800.f;
    }
}

void ACoastalVehicle::SetFailure(const ECoastalTransitFailureReason Reason, const FString& Text)
{
    FailureReason = Reason;
    FailureReasonText = Text;
    VehicleState = ECoastalVehicleState::Blocked;
    UE_LOG(LogTemp, Display, TEXT("COASTAL_TRANSIT_FAILURE vehicle=%s reason=%d detail=%s"),
        *VehicleName, static_cast<int32>(Reason), *Text);
}

void ACoastalVehicle::ClearFailure()
{
    FailureReason = ECoastalTransitFailureReason::None;
    FailureReasonText.Empty();
    if (VehicleState == ECoastalVehicleState::Blocked)
    {
        VehicleState = Driver ? ECoastalVehicleState::Occupied : ECoastalVehicleState::Idle;
    }
}

void ACoastalVehicle::SetVehicleType(const ECoastalVehicleType NewType)
{
    VehicleType = NewType;
    bBoat = NewType == ECoastalVehicleType::Rowboat;
}

void ACoastalVehicle::SetRouteBounds(const FVector Minimum, const FVector Maximum)
{
    RouteMinBounds = FVector(FMath::Min(Minimum.X, Maximum.X), FMath::Min(Minimum.Y, Maximum.Y),
        FMath::Min(Minimum.Z, Maximum.Z));
    RouteMaxBounds = FVector(FMath::Max(Minimum.X, Maximum.X), FMath::Max(Minimum.Y, Maximum.Y),
        FMath::Max(Minimum.Z, Maximum.Z));
    bRouteBounded = true;
}

void ACoastalVehicle::ClearRouteBounds()
{
    bRouteBounded = false;
}

void ACoastalVehicle::SetStop(const FVector Location, const float Radius, const float DwellSeconds)
{
    StopLocation = Location;
    StopRadius = FMath::Max(1.f, Radius);
    StopDwellSeconds = FMath::Max(0.f, DwellSeconds);
    StopDwellRemaining = 0.f;
    bStopEnabled = true;
}

void ACoastalVehicle::ClearStop()
{
    bStopEnabled = false;
    StopDwellRemaining = 0.f;
}

bool ACoastalVehicle::IsAtStop() const
{
    return bStopEnabled && FVector::Dist2D(GetActorLocation(), StopLocation) <= StopRadius;
}

bool ACoastalVehicle::Board(ACoastalCharacter* Character)
{
    ClearFailure();
    if (Driver)
    {
        SetFailure(ECoastalTransitFailureReason::AlreadyOccupied, TEXT("Vehicle already has a driver."));
        return false;
    }
    if (!Character)
    {
        SetFailure(ECoastalTransitFailureReason::InvalidCharacter, TEXT("No character is available to board."));
        return false;
    }
    if (!Character->GetController())
    {
        SetFailure(ECoastalTransitFailureReason::CharacterHasNoController,
            TEXT("Character has no controller for boarding."));
        return false;
    }
    if (FVector::Dist2D(GetActorLocation(), Character->GetActorLocation()) > 340)
    {
        SetFailure(ECoastalTransitFailureReason::CharacterTooFar,
            TEXT("Move closer to the vehicle before boarding."));
        return false;
    }
    if (FMath::Abs(Speed) > 80.f)
    {
        SetFailure(ECoastalTransitFailureReason::VehicleMoving,
            TEXT("Vehicle must be stopped before boarding."));
        return false;
    }
    Driver = Character;
    AController* Player = Character->GetController();
    Driver->SetActorHiddenInGame(true);
    Driver->SetActorEnableCollision(false);
    Driver->GetCharacterMovement()->DisableMovement();
    Player->Possess(this);
    VehicleState = ECoastalVehicleState::Occupied;
    SetActorTickEnabled(true);
    UE_LOG(LogTemp, Display, TEXT("COASTAL_TRANSIT_BOARD vehicle=%s type=%d"),
        *VehicleName, static_cast<int32>(GetEffectiveVehicleType()));
    return true;
}

bool ACoastalVehicle::TryFindExit(FVector& Exit) const
{
    if (!GetWorld() || !Driver)
    {
        return false;
    }
    const float Offset = Collision->GetScaledBoxExtent().Y + 110;
    for (const float Side : {-1.f, 1.f})
    {
        const FVector Candidate = GetActorLocation() + GetActorRightVector() * Offset * Side;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(CoastalExit), false, this);
        Query.AddIgnoredActor(Driver);
        FHitResult Floor;
        if (!GetWorld()->LineTraceSingleByChannel(Floor, Candidate + FVector(0, 0, 220),
            Candidate - FVector(0, 0, 400), ECC_Visibility, Query) || Floor.Normal.Z < 0.7f)
        {
            continue;
        }
        const FVector CandidateExit = Floor.ImpactPoint + FVector(0, 0, 96);
        if (GetWorld()->OverlapBlockingTestByChannel(CandidateExit, FQuat::Identity, ECC_Pawn,
            FCollisionShape::MakeCapsule(34, 90), Query))
        {
            continue;
        }
        Exit = CandidateExit;
        return true;
    }
    return false;
}

bool ACoastalVehicle::Leave()
{
    ClearFailure();
    if (!Driver || !Controller)
    {
        SetFailure(ECoastalTransitFailureReason::NoPassenger,
            TEXT("Vehicle has no passenger to exit."));
        return false;
    }
    if (FMath::Abs(Speed) > 80.f)
    {
        SetFailure(ECoastalTransitFailureReason::VehicleMoving,
            TEXT("Vehicle must stop before exiting."));
        return false;
    }
    FVector Exit;
    if (!TryFindExit(Exit))
    {
        SetFailure(ECoastalTransitFailureReason::NoSafeExit,
            TEXT("No walkable and clear exit point is available."));
        return false;
    }
    AController* Player = Controller;
    Driver->SetActorLocation(Exit);
    Driver->SetActorHiddenInGame(false);
    Driver->SetActorEnableCollision(true);
    Driver->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    Player->Possess(Driver);
    Driver->Notify(TEXT("Vehicle parked"));
    Driver = nullptr;
    Speed = 0;
    Drive(0, 0);
    VehicleState = ECoastalVehicleState::Idle;
    SetActorTickEnabled(false);
    UE_LOG(LogTemp, Display, TEXT("COASTAL_TRANSIT_EXIT vehicle=%s"), *VehicleName);
    return true;
}

void ACoastalVehicle::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("CoastForward"), this, &ACoastalVehicle::Forward);
    Input->BindAxis(TEXT("CoastRight"), this, &ACoastalVehicle::Right);
    Input->BindKey(EKeys::E, IE_Pressed, this, &ACoastalVehicle::ExitInput);
}

void ACoastalVehicle::Forward(const float Value)
{
    Drive(Value, SteeringInput);
}

void ACoastalVehicle::Right(const float Value)
{
    Drive(ThrottleInput, Value);
}

void ACoastalVehicle::ExitInput()
{
    Leave();
}

void ACoastalVehicle::Drive(const float Throttle, const float Steering)
{
    if (!Driver)
    {
        SetFailure(ECoastalTransitFailureReason::ControlUnavailable,
            TEXT("Vehicle controls require a boarded driver."));
        return;
    }
    ClearFailure();
    ThrottleInput = FMath::Clamp(Throttle, -1.f, 1.f);
    SteeringInput = FMath::Clamp(Steering, -1.f, 1.f);
}

void ACoastalVehicle::Tick(const float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!Driver)
    {
        SetActorTickEnabled(false);
        return;
    }
    const ECoastalVehicleType Type = GetEffectiveVehicleType();
    const float Maximum = GetMaximumSpeed();
    Speed = FMath::FInterpTo(Speed, ThrottleInput * Maximum, DeltaSeconds,
        Type == ECoastalVehicleType::Rowboat ? 1.2f : 1.8f);
    if (bStopEnabled && IsAtStop())
    {
        if (StopDwellRemaining <= 0.f)
        {
            StopDwellRemaining = StopDwellSeconds;
            Speed = 0.f;
            VehicleState = ECoastalVehicleState::Stopped;
        }
        else
        {
            StopDwellRemaining = FMath::Max(0.f, StopDwellRemaining - DeltaSeconds);
            if (StopDwellRemaining <= 0.f)
            {
                bStopEnabled = false;
            }
        }
        return;
    }
    const float TurnScale = Type == ECoastalVehicleType::Aircraft ? 25.f : 65.f;
    const float Turn = SteeringInput * FMath::Clamp(Speed / Maximum, -1.f, 1.f)
        * TurnScale * DeltaSeconds;
    AddActorWorldRotation(FRotator(0, Turn, 0));
    FVector Next = GetActorLocation() + GetActorForwardVector() * Speed * DeltaSeconds;
    if (Type == ECoastalVehicleType::Rowboat)
    {
        Next.X = FMath::Clamp(Next.X, 20600.f, 72000.f);
        Next.Y = FMath::Clamp(Next.Y, -26500.f, 26500.f);
    }
    if (bRouteBounded && (Next.X < RouteMinBounds.X || Next.X > RouteMaxBounds.X
        || Next.Y < RouteMinBounds.Y || Next.Y > RouteMaxBounds.Y
        || Next.Z < RouteMinBounds.Z || Next.Z > RouteMaxBounds.Z))
    {
        Next.X = FMath::Clamp(Next.X, RouteMinBounds.X, RouteMaxBounds.X);
        Next.Y = FMath::Clamp(Next.Y, RouteMinBounds.Y, RouteMaxBounds.Y);
        Next.Z = FMath::Clamp(Next.Z, RouteMinBounds.Z, RouteMaxBounds.Z);
        SetFailure(ECoastalTransitFailureReason::RouteLimit,
            TEXT("Vehicle reached the authored route boundary."));
        Speed = 0.f;
    }
    FHitResult Hit;
    SetActorLocation(Next, true, &Hit);
    if (Hit.bBlockingHit)
    {
        if (!bReportedBlock)
        {
            UE_LOG(LogTemp, Display, TEXT("COASTAL_VEHICLE_BLOCK name=%s actor=%s normal=%s penetrating=%d"),
                *VehicleName, *GetNameSafe(Hit.GetActor()), *Hit.Normal.ToString(),
                Hit.bStartPenetrating ? 1 : 0);
            bReportedBlock = true;
        }
        SetFailure(ECoastalTransitFailureReason::RouteBlocked,
            TEXT("Vehicle route is blocked by collision geometry."));
        Speed = 0;
    }
    else
    {
        bReportedBlock = false;
        if (FailureReason == ECoastalTransitFailureReason::RouteBlocked)
        {
            ClearFailure();
        }
    }
    if (Type == ECoastalVehicleType::Rowboat)
    {
        RowingFeedback += DeltaSeconds * FMath::Max(0.5f, FMath::Abs(Speed) / Maximum * 7.f);
        VehicleState = ECoastalVehicleState::Rowing;
        if (Mesh)
        {
            Mesh->SetRelativeRotation(FRotator(0, FMath::Sin(RowingFeedback) * 4.f, 0));
        }
    }
    else
    {
        VehicleState = FMath::Abs(Speed) > 1.f ? ECoastalVehicleState::Moving
            : ECoastalVehicleState::Occupied;
    }
}
