#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ANANTACityVehicle.generated.h"

class UBoxComponent;
class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;

UCLASS()
class ANANTA_API AANANTACityVehicle : public AActor
{
    GENERATED_BODY()

public:
    AANANTACityVehicle();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void Drive(float Throttle, float Steering, bool bBrake, float DeltaTime);
    virtual bool FindSafeExit(const APawn* Player, FVector& OutLocation) const;
    bool IsRestoreComplete() const { return bRestoreComplete; }
    float GetSpeedKmh() const { return FMath::Abs(Speed) * 0.036f; }

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FName VehicleId = TEXT("PlayerCar");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> BodyMesh;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UBoxComponent> CollisionBody;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USpringArmComponent> CameraArm;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UCameraComponent> Camera;

    bool bOccupied = false;

protected:
    bool bRestoreComplete = false;
    FTransform InitialTransform;
    float RestoreElapsed = 0;
    float Speed = 0;
};
