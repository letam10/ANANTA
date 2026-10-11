#include "City/ANANTACityVehicle.h"

#include "City/ANANTACitySubsystem.h"
#include "City/CityWorldBounds.h"
#include "Camera/CameraComponent.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"

AANANTACityVehicle::AANANTACityVehicle()
{
    PrimaryActorTick.bCanEverTick = true;
    SetCanBeDamaged(false);
    CollisionBody = CreateDefaultSubobject<UBoxComponent>(TEXT("CollisionBody"));
    SetRootComponent(CollisionBody);
    CollisionBody->SetBoxExtent(FVector(215, 95, 65));
    CollisionBody->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
    BodyMesh->SetupAttachment(RootComponent);
    BodyMesh->SetRelativeLocation(FVector(0, 0, -70));
    BodyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    CameraArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraArm"));
    CameraArm->SetupAttachment(RootComponent);
    CameraArm->TargetArmLength = 740;
    CameraArm->SocketOffset = FVector(0, 0, 170);
    CameraArm->SetRelativeRotation(FRotator(-15, 0, 0));
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(CameraArm, USpringArmComponent::SocketName);
    Camera->FieldOfView = 85;
}

void AANANTACityVehicle::BeginPlay()
{
    Super::BeginPlay();
    InitialTransform = GetActorTransform();
    const auto* Save = GetGameInstance()->GetSubsystem<UANANTACitySubsystem>()->GetProgress();
    if (Save->bHasCarTransform && VehicleId == TEXT("PlayerCar"))
    {
        SetActorTransform(Save->CarTransform);
    }
}

void AANANTACityVehicle::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (bRestoreComplete)
    {
        if (!bOccupied)
        {
            Drive(0, 0, true, DeltaTime);
        }
        return;
    }
    const APlayerController* PC = GetWorld()->GetFirstPlayerController();
    const APawn* Hero = PC ? PC->GetPawn() : nullptr;
    if (!Hero || FVector::DistSquared2D(Hero->GetActorLocation(), GetActorLocation()) > 12000 * 12000)
    {
        RestoreElapsed = 0;
        return;
    }
    RestoreElapsed += DeltaTime;
    if (RestoreElapsed < 1)
    {
        return;
    }
    FVector Position = GetActorLocation();
    FHitResult Floor;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityCarRestore), false, this);
    if (GetWorld()->LineTraceSingleByChannel(Floor, Position + FVector(0, 0, 150),
        Position - FVector(0, 0, 500), ECC_WorldStatic, Params) && Floor.ImpactNormal.Z > 0.8f)
    {
        Position.Z = Floor.ImpactPoint.Z + 70;
        if (!GetWorld()->OverlapBlockingTestByChannel(Position, GetActorQuat(), ECC_WorldDynamic,
            FCollisionShape::MakeBox(CollisionBody->GetScaledBoxExtent()), Params))
        {
            SetActorLocation(Position);
            bRestoreComplete = true;
        }
    }
    if (RestoreElapsed > 12 && !bRestoreComplete)
    {
        SetActorTransform(InitialTransform);
    }
}

void AANANTACityVehicle::Drive(float Throttle, float Steering, bool bBrake, const float DeltaTime)
{
    if (!bRestoreComplete)
    {
        return;
    }
    const float Step = FMath::Min(DeltaTime, 0.05f);
    Speed = FMath::Clamp(Speed + Throttle * 850 * Step, -850.f, 3300.f);
    if (bBrake || FMath::IsNearlyZero(Throttle))
    {
        Speed = FMath::FInterpConstantTo(Speed, 0.f, Step, bBrake ? 2500.f : 260.f);
    }
    const float Turn = Steering * FMath::Clamp(Speed / 800.f, -1.f, 1.f) * 65 * Step;
    const FQuat Rotation = FRotator(0, GetActorRotation().Yaw + Turn, 0).Quaternion();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityCarDrive), false, this);
    // Kiem tra goc quay vi sweep Unreal khong quet the tich xoay.
    if (!GetWorld()->OverlapBlockingTestByChannel(GetActorLocation(), Rotation, ECC_WorldDynamic,
        FCollisionShape::MakeBox(CollisionBody->GetScaledBoxExtent()), Params))
    {
        SetActorRotation(Rotation);
    }
    const FVector Next = GetActorLocation() + GetActorForwardVector() * Speed * Step;
    FHitResult Floor;
    if (FMath::Abs(Next.X) > CityWorldBounds::RoadExtent
        || FMath::Abs(Next.Y) > CityWorldBounds::RoadExtent
        || !GetWorld()->LineTraceSingleByChannel(Floor, Next + FVector(0, 0, 120),
            Next - FVector(0, 0, 220), ECC_WorldStatic, Params) || Floor.ImpactNormal.Z < 0.8f)
    {
        Speed = 0;
        return;
    }
    FVector Target = Next;
    Target.Z = Floor.ImpactPoint.Z + 70;
    FHitResult Hit;
    SetActorLocation(Target, true, &Hit);
    if (Hit.bBlockingHit)
    {
        Speed = 0;
    }
}

bool AANANTACityVehicle::FindSafeExit(const APawn* Player, FVector& OutLocation) const
{
    const auto* Character = Cast<ACharacter>(Player);
    if (!Character)
    {
        return false;
    }
    const auto* PlayerCapsule = Character->GetCapsuleComponent();
    const float Radius = PlayerCapsule->GetScaledCapsuleRadius();
    const float HalfHeight = PlayerCapsule->GetScaledCapsuleHalfHeight();
    const FCollisionShape Capsule = FCollisionShape::MakeCapsule(Radius, HalfHeight);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityCarExit), false, this);
    Params.AddIgnoredActor(Player);
    const FVector Offsets[] = {
        FVector(0, -210, 0), FVector(0, 210, 0), FVector(-340, 0, 0), FVector(340, 0, 0)
    };
    for (const FVector& Offset : Offsets)
    {
        FVector Candidate = GetActorTransform().TransformPosition(Offset);
        FHitResult Floor;
        if (!GetWorld()->LineTraceSingleByChannel(Floor, Candidate + FVector(0, 0, 200),
            Candidate - FVector(0, 0, 300), ECC_WorldStatic, Params) || Floor.ImpactNormal.Z < 0.7f)
        {
            continue;
        }
        const float DoorFloor = GetActorLocation().Z - CollisionBody->GetScaledBoxExtent().Z;
        // Khong chon mai nha/dam tren dau lam san roi dich chuyen nguoi len do.
        if (Floor.ImpactPoint.Z > DoorFloor + Character->GetCharacterMovement()->MaxStepHeight)
        {
            continue;
        }
        Candidate.Z = Floor.ImpactPoint.Z + HalfHeight + 3;
        FHitResult Wall;
        // Quet ca than nguoi: hinh cau cu bo sot dam thap va vat can ngang dau.
        const FVector Start(GetActorLocation().X, GetActorLocation().Y, Candidate.Z);
        if (GetWorld()->SweepSingleByChannel(Wall, Start, Candidate, FQuat::Identity, ECC_Pawn,
            Capsule, Params))
        {
            continue;
        }
        // Khong bo qua xe khi kiem tra capsule o diem ra cuoi cung.
        FCollisionQueryParams ExitParams(SCENE_QUERY_STAT(CityExitCapsule), false, Player);
        if (!GetWorld()->OverlapBlockingTestByChannel(Candidate, FQuat::Identity, ECC_Pawn,
            Capsule, ExitParams))
        {
            OutLocation = Candidate;
            return true;
        }
    }
    return false;
}
