#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ANANTACityEnemy.generated.h"

class UTextRenderComponent;

UCLASS()
class ANANTA_API AANANTACityEnemy : public ACharacter
{
    GENERATED_BODY()

public:
    AANANTACityEnemy();
    virtual void Tick(float DeltaTime) override;
    virtual float TakeDamage(float Damage, const FDamageEvent& Event, AController* DamageInstigator,
        AActor* Causer) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FName EnemyId;

    UPROPERTY(BlueprintReadOnly)
    float Health = 60;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UTextRenderComponent> Label;

private:
    UPROPERTY()
    TObjectPtr<class UAnimSequence> AttackAnimation;

    float AttackElapsed = 0;
    float NavigationElapsed = 0;
    bool bActive = false;
    bool bNeedsDirectMove = false;
};
