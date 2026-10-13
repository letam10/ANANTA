#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "CoastalVehicle.generated.h"

class ACoastalCharacter;
class UBoxComponent;
class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;

UCLASS()
class ANANTA_API ACoastalVehicle : public APawn
{
    GENERATED_BODY()

public:
    ACoastalVehicle();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UBoxComponent> Collision;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bBoat = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString VehicleName = TEXT("Vehicle");

    UFUNCTION(BlueprintCallable)
    bool Board(ACoastalCharacter* Character);

    UFUNCTION(BlueprintCallable)
    bool Leave();

    UFUNCTION(BlueprintCallable)
    void Drive(float Throttle, float Steering);

    bool IsOccupied() const { return Driver != nullptr; }
    float GetSpeed() const { return Speed; }

protected:
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;

private:
    UPROPERTY()
    TObjectPtr<ACoastalCharacter> Driver;

    UPROPERTY()
    TObjectPtr<USpringArmComponent> Arm;

    UPROPERTY()
    TObjectPtr<UCameraComponent> Camera;

    float Speed = 0;
    float ThrottleInput = 0;
    float SteeringInput = 0;
    bool bReportedBlock = false;
    void Forward(float Value);
    void Right(float Value);
    void ExitInput();
};
