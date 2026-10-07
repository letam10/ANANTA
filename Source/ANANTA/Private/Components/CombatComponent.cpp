#include "Components/CombatComponent.h"

#include "GameFramework/Character.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

UCombatComponent::UCombatComponent()
    : AttackCooldown(0.35f)
    , BaseDamage(25.0f)
    , AttackRange(220.0f)
    , AttackRadius(55.0f)
    , LastAttackTime(-TNumericLimits<double>::Max())
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UCombatComponent::TryAttack()
{
    if (!CanAttack())
    {
        return false;
    }

    LastAttackTime = GetWorld()->GetTimeSeconds();

    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (Character)
    {
        const FVector Start = Character->GetActorLocation() + FVector(0.0f, 0.0f, 80.0f);
        const FVector End = Start + Character->GetActorForwardVector() * AttackRange;
        FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(ANANTA_Attack), false, Character);
        FHitResult Hit;
        const bool bHit = GetWorld()->SweepSingleByChannel(
            Hit,
            Start,
            End,
            FQuat::Identity,
            ECC_Pawn,
            FCollisionShape::MakeSphere(AttackRadius),
            QueryParams);

        if (bHit && Hit.GetActor())
        {
            UGameplayStatics::ApplyDamage(Hit.GetActor(), BaseDamage, Character->GetController(), Character, nullptr);
        }
    }

    return true;
}

bool UCombatComponent::CanAttack() const
{
    const UWorld* World = GetWorld();
    return World && (World->GetTimeSeconds() - LastAttackTime) >= AttackCooldown;
}
