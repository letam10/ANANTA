#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CombatComponent.generated.h"

UCLASS(ClassGroup = (ANANTA), meta = (BlueprintSpawnableComponent))
class ANANTA_API UCombatComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UCombatComponent();

    UFUNCTION(BlueprintCallable, Category = "Combat")
    bool TryAttack();

    UFUNCTION(BlueprintPure, Category = "Combat")
    bool CanAttack() const;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Tuning")
    float AttackCooldown;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Tuning")
    float BaseDamage;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Tuning")
    float AttackRange;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Tuning")
    float AttackRadius;

private:
    UPROPERTY()
    TObjectPtr<class UAnimSequence> AttackAnimation;

    double LastAttackTime;
};
