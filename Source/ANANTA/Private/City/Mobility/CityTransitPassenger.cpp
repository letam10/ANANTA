#include "City/Mobility/CityTransitPassenger.h"

#include "City/Mobility/CityRouteVehicle.h"
#include "Animation/AnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/ConstructorHelpers.h"

ACityTransitPassenger::ACityTransitPassenger()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->InitCapsuleSize(32, 92);
    GetCharacterMovement()->MaxWalkSpeed = 150;
    GetCharacterMovement()->bRunPhysicsWithNoController = true;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0, 360, 0);
    SetCanBeDamaged(false);
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple"));
    static ConstructorHelpers::FClassFinder<UAnimInstance> Animation(
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"));
    GetMesh()->SetSkeletalMeshAsset(MeshAsset.Object);
    GetMesh()->SetAnimInstanceClass(Animation.Class);
    GetMesh()->SetRelativeLocation(FVector(0, 0, -92));
    GetMesh()->SetRelativeRotation(FRotator(0, -90, 0));
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void ACityTransitPassenger::Approach(ACityRouteVehicle* Vehicle, const FVector& Door)
{
    Carrier = Vehicle;
    Target = Door;
    Elapsed = 0;
    Phase = ECityPassengerPhase::Approaching;
}

bool ACityTransitPassenger::Alight(const FVector& Door, const FVector& Sidewalk)
{
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityPassengerExit), false, this);
    if (GetWorld()->OverlapBlockingTestByChannel(Door, FQuat::Identity, ECC_Pawn,
        FCollisionShape::MakeCapsule(32, 92), Params))
    {
        return false;
    }
    DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
    SetActorLocation(Door);
    SetActorEnableCollision(true);
    SetActorHiddenInGame(false);
    GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    Target = Sidewalk;
    Phase = ECityPassengerPhase::Alighting;
    Elapsed = 0;
    return true;
}

void ACityTransitPassenger::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (Phase == ECityPassengerPhase::Seated || Phase == ECityPassengerPhase::Finished)
    {
        return;
    }
    if (!Carrier.IsValid())
    {
        Destroy();
        return;
    }
    Elapsed += DeltaTime;
    FVector Direction = Target - GetActorLocation();
    Direction.Z = 0;
    if (Direction.SizeSquared() < 55 * 55)
    {
        GetCharacterMovement()->StopMovementImmediately();
        if (Phase == ECityPassengerPhase::Approaching)
        {
            // Nhan vat vao cabin kin; chi vo hieu va cham trong luc la hanh khach.
            GetCharacterMovement()->DisableMovement();
            SetActorEnableCollision(false);
            SetActorHiddenInGame(true);
            AttachToActor(Carrier.Get(), FAttachmentTransformRules::SnapToTargetNotIncludingScale);
            Phase = ECityPassengerPhase::Seated;
            Carrier->RecordBoarding();
        }
        else
        {
            Phase = ECityPassengerPhase::Finished;
            Carrier->RecordAlighting();
            SetLifeSpan(4);
        }
        return;
    }
    AddMovementInput(Direction.GetSafeNormal());
    if (Elapsed > 18 || GetActorLocation().Z < -1000)
    {
        // Khong dich chuyen NPC xuyen vat can neu duong len/xuong bi chan.
        Destroy();
    }
}
