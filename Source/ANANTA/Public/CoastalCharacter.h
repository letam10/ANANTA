#pragma once

#include "CoreMinimal.h"
#include "ANANTACharacter.h"
#include "CoastalCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;

UCLASS()
class ANANTA_API ACoastalCharacter : public AANANTACharacter
{
    GENERATED_BODY()

public:
    ACoastalCharacter();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USpringArmComponent> CameraArm;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UCameraComponent> Camera;

    UFUNCTION(BlueprintCallable)
    void Interact();

    FString StatusMessage;
    double StatusUntil = 0;
    AActor* FindAction() const;
    void Notify(const FString& Message);

protected:
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual void Tick(float DeltaSeconds) override;

private:
    void Forward(float Value);
    void Right(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    void Sprint();
    void Walk();
    void Move(float ForwardValue, float RightValue);
};
