#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TraversalComponent.generated.h"

UCLASS(ClassGroup = (ANANTA), meta = (BlueprintSpawnableComponent))
class ANANTA_API UTraversalComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTraversalComponent();

    UFUNCTION(BlueprintCallable, Category = "Traversal")
    void StartSprint();

    UFUNCTION(BlueprintCallable, Category = "Traversal")
    void StopSprint();

    UFUNCTION(BlueprintPure, Category = "Traversal")
    bool IsSprinting() const { return bIsSprinting; }

    UFUNCTION(BlueprintCallable, Category = "Traversal")
    bool TryMantle();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Traversal|Tuning")
    float WalkSpeed;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Traversal|Tuning")
    float SprintSpeed;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Traversal|Tuning")
    float MaxMantleHeight;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Traversal|Tuning")
    float MantleForwardDistance;

private:
    void ApplyMovementSpeed(float NewSpeed);

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "Traversal", meta = (AllowPrivateAccess = "true"))
    bool bIsSprinting;
};
