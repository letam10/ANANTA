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

bool ACoastalVehicle::Board(ACoastalCharacter* Character)
{
    if (Driver || !Character || !Character->GetController())
    {
        return false;
    }
    if (FVector::Dist2D(GetActorLocation(), Character->GetActorLocation()) > 340)
    {
        return false;
    }
    Driver = Character;
    AController* Player = Character->GetController();
    Driver->SetActorHiddenInGame(true);
    Driver->SetActorEnableCollision(false);
    Driver->GetCharacterMovement()->DisableMovement();
    Player->Possess(this);
    SetActorTickEnabled(true);
    return true;
}

bool ACoastalVehicle::Leave()
{
    if (!Driver || !Controller || FMath::Abs(Speed) > 80)
    {
        return false;
    }
    // Chỉ xuống thuyền ở điểm có nền: tránh đặt người vào mặt nước.
    for (float Side : {-1.f, 1.f})
    {
        const float Offset = Collision->GetScaledBoxExtent().Y + 110;
        const FVector Candidate = GetActorLocation() + GetActorRightVector() * Offset * Side;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(CoastalExit), false, this);
        Query.AddIgnoredActor(Driver);
        FHitResult Floor;
        if (!GetWorld()->LineTraceSingleByChannel(Floor, Candidate + FVector(0, 0, 220),
            Candidate - FVector(0, 0, 400), ECC_Visibility, Query) || Floor.Normal.Z < 0.7)
        {
            continue;
        }
        const FVector Exit = Floor.ImpactPoint + FVector(0, 0, 96);
        if (GetWorld()->OverlapBlockingTestByChannel(Exit, FQuat::Identity, ECC_Pawn,
            FCollisionShape::MakeCapsule(34, 90), Query))
        {
            continue;
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
        SetActorTickEnabled(false);
        return true;
    }
    return false;
}

void ACoastalVehicle::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("CoastForward"), this, &ACoastalVehicle::Forward);
    Input->BindAxis(TEXT("CoastRight"), this, &ACoastalVehicle::Right);
    Input->BindKey(EKeys::E, IE_Pressed, this, &ACoastalVehicle::ExitInput);
}

void ACoastalVehicle::Forward(float Value)
{
    Drive(Value, SteeringInput);
}

void ACoastalVehicle::Right(float Value)
{
    Drive(ThrottleInput, Value);
}

void ACoastalVehicle::ExitInput() { Leave(); }

void ACoastalVehicle::Drive(float Throttle, float Steering)
{
    ThrottleInput = FMath::Clamp(Throttle, -1.f, 1.f);
    SteeringInput = FMath::Clamp(Steering, -1.f, 1.f);
}

void ACoastalVehicle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    const float Maximum = bBoat ? 300.f : 1800.f;
    Speed = FMath::FInterpTo(Speed, ThrottleInput * Maximum, DeltaSeconds, bBoat ? 1.2f : 1.8f);
    const float Turn = SteeringInput * FMath::Clamp(Speed / Maximum, -1.f, 1.f) * 65 * DeltaSeconds;
    AddActorWorldRotation(FRotator(0, Turn, 0));
    FVector Next = GetActorLocation() + GetActorForwardVector() * Speed * DeltaSeconds;
    if (bBoat)
    {
        Next.X = FMath::Clamp(Next.X, 20600.f, 72000.f);
        Next.Y = FMath::Clamp(Next.Y, -26500.f, 26500.f);
    }
    FHitResult Hit;
    SetActorLocation(Next, true, &Hit);
    if (Hit.bBlockingHit)
    {
        if (!bReportedBlock)
        {
            UE_LOG(LogTemp, Display, TEXT("COASTAL_VEHICLE_BLOCK name=%s actor=%s normal=%s penetrating=%d"),
                *VehicleName, *GetNameSafe(Hit.GetActor()), *Hit.Normal.ToString(), Hit.bStartPenetrating ? 1 : 0);
            bReportedBlock = true;
        }
        Speed = 0;
    }
    else
    {
        bReportedBlock = false;
    }
}
