#include "City/Mobility/CityRowboat.h"

#include "City/CityWorldBounds.h"
#include "City/Mobility/CityMobilityData.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"

ACityRowboat::ACityRowboat()
{
    VehicleId = TEXT("PlayerRowboat");
    CollisionBody->SetBoxExtent(FVector(190, 70, 100));
    BodyMesh->SetRelativeLocation(FVector(0, 0, -25));
}

void ACityRowboat::BeginPlay()
{
    Super::BeginPlay();
    // Thuyen noi tren mat nuoc; khong cho Tick cua xe tim day bien lam mat duong.
    bRestoreComplete = true;
}

void ACityRowboat::Drive(float Throttle, float Steering, bool bBrake, float DeltaTime)
{
    const float Step = FMath::Min(DeltaTime, .05f);
    Speed = FMath::Clamp(Speed + Throttle * 120 * Step, -100.f, 250.f);
    if (bBrake || FMath::IsNearlyZero(Throttle))
    {
        Speed = FMath::FInterpConstantTo(Speed, 0.f, Step, bBrake ? 400.f : 60.f);
    }
    const FQuat Rotation = FRotator(0, GetActorRotation().Yaw + Steering * 40 * Step, 0).Quaternion();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRowboat), false, this);
    const FCollisionShape Shape = FCollisionShape::MakeBox(CollisionBody->GetScaledBoxExtent());
    if (!GetWorld()->OverlapBlockingTestByChannel(GetActorLocation(), Rotation, ECC_WorldDynamic, Shape, Params))
    {
        SetActorRotation(Rotation);
    }
    FVector Target = GetActorLocation() + GetActorForwardVector() * Speed * Step;
    Target.Z = CityMobility::WaterLevel;
    // Giu thuyen trong vung bien va cach bien ban do bang kich thuoc than thuyen.
    constexpr float Edge = CityWorldBounds::RoadExtent - 500.f;
    if (Target.X < 128500 || Target.Y > -120500 || FMath::Abs(Target.X) > Edge || FMath::Abs(Target.Y) > Edge)
    {
        Speed = 0;
        return;
    }
    FHitResult Hit;
    SetActorLocation(Target, true, &Hit);
    if (Hit.bBlockingHit)
    {
        Speed = 0;
    }
}

bool ACityRowboat::FindSafeExit(const APawn* Player, FVector& OutLocation) const
{
    const auto* Character = Cast<ACharacter>(Player);
    if (!Character)
    {
        return false;
    }
    const auto* Capsule = Character->GetCapsuleComponent();
    const float HalfHeight = Capsule->GetScaledCapsuleHalfHeight();
    const FCollisionShape Shape = FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(), HalfHeight);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRowboatExit), false, this);
    Params.AddIgnoredActor(Player);
    for (const FVector Offset : {FVector(0, -220, 0), FVector(0, 220, 0), FVector(-300, 0, 0)})
    {
        FVector Candidate = GetActorTransform().TransformPosition(Offset);
        FHitResult Floor;
        if (!GetWorld()->LineTraceSingleByObjectType(Floor, Candidate + FVector(0, 0, 500),
            Candidate - FVector(0, 0, 100), FCollisionObjectQueryParams(ECC_WorldStatic), Params)
            || Floor.ImpactNormal.Z < .8f || Floor.ImpactPoint.Z < -30 || Floor.ImpactPoint.Z > 80)
        {
            continue;
        }
        Candidate.Z = Floor.ImpactPoint.Z + HalfHeight + 3;
        FHitResult Wall;
        const FVector Start(GetActorLocation().X, GetActorLocation().Y, Candidate.Z);
        if (GetWorld()->SweepSingleByChannel(Wall, Start, Candidate, FQuat::Identity, ECC_Pawn, Shape, Params))
        {
            continue;
        }
        FCollisionQueryParams FinalParams(SCENE_QUERY_STAT(CityRowboatExitCapsule), false, Player);
        if (!GetWorld()->OverlapBlockingTestByChannel(Candidate, FQuat::Identity, ECC_Pawn, Shape, FinalParams))
        {
            OutLocation = Candidate;
            return true;
        }
    }
    return false;
}
