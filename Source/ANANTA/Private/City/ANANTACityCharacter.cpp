#include "City/ANANTACityCharacter.h"

#include "City/ANANTACityController.h"
#include "City/ANANTACityEnemy.h"
#include "Components/CombatComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "NavigationInvokerComponent.h"
#include "Animation/AnimInstance.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "UObject/ConstructorHelpers.h"

AANANTACityCharacter::AANANTACityCharacter()
{
    GetCapsuleComponent()->InitCapsuleSize(38, 92);
    CombatComponent->AttackCooldown = 0.65f;
    bUseControllerRotationYaw = false;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0, 540, 0);
    GetCharacterMovement()->JumpZVelocity = 650;
    CameraArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("CityCameraArm"));
    CameraArm->SetupAttachment(RootComponent);
    CameraArm->TargetArmLength = 420;
    CameraArm->SocketOffset = FVector(0, 55, 75);
    CameraArm->bUsePawnControlRotation = true;
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("CityCamera"));
    Camera->SetupAttachment(CameraArm, USpringArmComponent::SocketName);
    Camera->FieldOfView = 80;
    NavigationInvoker = CreateDefaultSubobject<UNavigationInvokerComponent>(TEXT("NavigationInvoker"));
    NavigationInvoker->SetGenerationRadii(7000, 9000);

    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
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

float AANANTACityCharacter::TakeDamage(float Damage, const FDamageEvent& Event,
    AController* DamageInstigator, AActor* Causer)
{
    if (!IsPlayerControlled() || !Cast<AANANTACityEnemy>(Causer) || Damage <= 0)
    {
        return 0;
    }
    const float Applied = FMath::Min(Health, Damage);
    Health -= Applied;
    LastDamageTime = GetWorld()->GetTimeSeconds();
    if (Health <= 0)
    {
        if (auto* PC = Cast<AANANTACityController>(GetController()))
        {
            PC->RecoverPlayer();
        }
        Health = 100;
    }
    return Applied;
}
