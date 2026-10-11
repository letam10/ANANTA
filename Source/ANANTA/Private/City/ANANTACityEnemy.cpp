#include "City/ANANTACityEnemy.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "AIController.h"
#include "Navigation/PathFollowingComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

AANANTACityEnemy::AANANTACityEnemy()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->InitCapsuleSize(38, 92);
    GetCharacterMovement()->MaxWalkSpeed = 250;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    AIControllerClass = AAIController::StaticClass();
    AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("EnemyLabel"));
    Label->SetupAttachment(RootComponent);
    Label->SetRelativeLocation(FVector(0, 0, 125));
    Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetWorldSize(25);
    Label->SetTextRenderColor(FColor(255, 100, 90));
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
    static ConstructorHelpers::FClassFinder<UAnimInstance> AnimAsset(
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> AttackAsset(
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_02.MM_Attack_02"));
    AttackAnimation = AttackAsset.Object;
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

void AANANTACityEnemy::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    const auto* State = GetGameInstance()->GetSubsystem<UANANTACitySubsystem>();
    const auto& Mission = State->GetMission();
    bActive = Mission.Stage == ECityMissionStage::Combat && FCityMissionState::IsEnemy(EnemyId)
        && !Mission.DefeatedEnemies.Contains(EnemyId) && Health > 0;
    SetActorHiddenInGame(!bActive);
    SetActorEnableCollision(bActive);
    auto* AI = Cast<AAIController>(GetController());
    if (!bActive)
    {
        GetCharacterMovement()->DisableMovement();
        if (AI)
        {
            AI->StopMovement();
        }
        return;
    }
    GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    auto* PC = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    auto* Player = PC ? Cast<AANANTACityCharacter>(PC->GetPawn()) : nullptr;
    if (!Player || PC->GetDrivenVehicle() || !PC->CanCaptureProgress())
    {
        if (AI)
        {
            AI->StopMovement();
        }
        return;
    }
    FVector Direction = Player->GetActorLocation() - GetActorLocation();
    const double Distance = Direction.Size2D();
    NavigationElapsed += DeltaTime;
    if (Distance > 140 && Distance < 2500)
    {
        if (AI && NavigationElapsed > 0.5f)
        {
            NavigationElapsed = 0;
            bNeedsDirectMove = AI->MoveToActor(Player, 105) == EPathFollowingRequestResult::Failed;
        }
        if (bNeedsDirectMove)
        {
            AddMovementInput(Direction.GetSafeNormal2D());
        }
    }
    else if (AI)
    {
        AI->StopMovement();
    }
    AttackElapsed += DeltaTime;
    if (Distance < 180 && FMath::Abs(Direction.Z) < 120 && AttackElapsed > 1.2f)
    {
        FHitResult Hit;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(CityEnemyMelee), false, this);
        Params.AddIgnoredActor(Player);
        if (!GetWorld()->LineTraceSingleByChannel(Hit, GetActorLocation(), Player->GetActorLocation(),
            ECC_Visibility, Params))
        {
            AttackElapsed = 0;
            SetActorRotation(Direction.Rotation());
            if (AttackAnimation && GetMesh()->GetAnimInstance())
            {
                GetMesh()->GetAnimInstance()->PlaySlotAnimationAsDynamicMontage(
                    AttackAnimation, TEXT("DefaultSlot"), 0.05f, 0.1f, 1.5f);
            }
            UGameplayStatics::ApplyDamage(Player, 12, GetController(), this, nullptr);
        }
    }
    Label->SetWorldRotation((PC->PlayerCameraManager->GetCameraLocation() - Label->GetComponentLocation()).Rotation());
    Label->SetText(FText::FromString(FString::Printf(TEXT("ANOMALY  %.0f"), Health)));
}

float AANANTACityEnemy::TakeDamage(float Damage, const FDamageEvent& Event,
    AController* DamageInstigator, AActor* Causer)
{
    const auto* Player = Cast<AANANTACityCharacter>(Causer);
    if (!bActive || !Player || !Player->IsPlayerControlled() || DamageInstigator != Player->GetController() || Damage <= 0)
    {
        return 0;
    }
    const float Applied = FMath::Min(Health, Damage);
    Health -= Applied;
    if (Health <= 0)
    {
        GetGameInstance()->GetSubsystem<UANANTACitySubsystem>()->RegisterEnemyDefeated(EnemyId);
        SetActorHiddenInGame(true);
        SetActorEnableCollision(false);
        bActive = false;
    }
    return Applied;
}
