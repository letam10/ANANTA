#pragma once

#include "CoreMinimal.h"
#include "ANANTACharacter.h"
#include "ANANTACityCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UNavigationInvokerComponent;

UCLASS()
class ANANTA_API AANANTACityCharacter : public AANANTACharacter
{
    GENERATED_BODY()

public:
    AANANTACityCharacter();
    virtual float TakeDamage(float Damage, const FDamageEvent& Event, AController* DamageInstigator,
        AActor* Causer) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<USpringArmComponent> CameraArm;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UCameraComponent> Camera;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UNavigationInvokerComponent> NavigationInvoker;

    UPROPERTY(BlueprintReadOnly)
    float Health = 100;

    float LastDamageTime = -100;
};
