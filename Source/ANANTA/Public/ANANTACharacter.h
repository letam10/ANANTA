#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ANANTACharacter.generated.h"

class UCombatComponent;
class UTraversalComponent;

UCLASS(Blueprintable)
class ANANTA_API AANANTACharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AANANTACharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ANANTA|Components")
    TObjectPtr<UTraversalComponent> TraversalComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ANANTA|Components")
    TObjectPtr<UCombatComponent> CombatComponent;
};
