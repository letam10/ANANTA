#include "City/ANANTACityPedestrian.h"

#include "Animation/AnimInstance.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/ConstructorHelpers.h"

AANANTACityPedestrian::AANANTACityPedestrian()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->InitCapsuleSize(32, 92);
    GetCharacterMovement()->MaxWalkSpeed = 110;
    GetCharacterMovement()->bRunPhysicsWithNoController = true;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0, 180, 0);
    SetCanBeDamaged(false);
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple"));
    static ConstructorHelpers::FClassFinder<UAnimInstance> AnimAsset(
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"));
    if (MeshAsset.Succeeded())
    {
        GetMesh()->SetSkeletalMeshAsset(MeshAsset.Object);
        GetMesh()->SetRelativeLocation(FVector(0, 0, -92));
        GetMesh()->SetRelativeRotation(FRotator(0, -90, 0));
    }
    if (AnimAsset.Succeeded())
    {
        GetMesh()->SetAnimInstanceClass(AnimAsset.Class);
    }
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void AANANTACityPedestrian::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    FVector Direction = Destination - GetActorLocation();
    Direction.Z = 0;
    StallTime = GetVelocity().SizeSquared2D() < 25 ? StallTime + DeltaTime : 0;
    if (Direction.SizeSquared() < 10000 || StallTime > 4)
    {
        Swap(Origin, Destination);
        StallTime = 0;
    }
    AddMovementInput(Direction.GetSafeNormal());
    if (GetActorLocation().Z < -500)
    {
        Destroy();
    }
}

AANANTACityTraffic::AANANTACityTraffic()
{
    PrimaryActorTick.bCanEverTick = true;
    auto* Box = CreateDefaultSubobject<UBoxComponent>(TEXT("TrafficCollision"));
    SetRootComponent(Box);
    Box->SetBoxExtent(FVector(215, 95, 65));
    Box->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
    BodyMesh->SetupAttachment(RootComponent);
    BodyMesh->SetRelativeLocation(FVector(0, 0, -70));
    BodyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SetCanBeDamaged(false);
}

void AANANTACityTraffic::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    FVector Direction = Destination - GetActorLocation();
    Direction.Z = 0;
    if (Direction.SizeSquared() < 40000)
    {
        Destroy();
        return;
    }
    const FVector Forward = Direction.GetSafeNormal();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityTraffic), false, this);
    FHitResult Obstacle;
    if (GetWorld()->SweepSingleByChannel(Obstacle, GetActorLocation(), GetActorLocation() + Forward * 650,
        GetActorQuat(), ECC_WorldDynamic, FCollisionShape::MakeBox(FVector(210, 95, 60)), Params))
    {
        StallTime += DeltaTime;
        if (StallTime > 20)
        {
            Destroy();
        }
        return;
    }
    StallTime = 0;
    FVector Target = GetActorLocation() + Forward * 700 * FMath::Min(DeltaTime, 0.05f);
    FHitResult Floor;
    if (!GetWorld()->LineTraceSingleByChannel(Floor, Target + FVector(0, 0, 100),
        Target - FVector(0, 0, 200), ECC_WorldStatic, Params))
    {
        Destroy();
        return;
    }
    Target.Z = Floor.ImpactPoint.Z + 70;
    SetActorLocation(Target, true);
}
