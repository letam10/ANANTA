#pragma once

#include "City/ANANTACityVehicle.h"
#include "CityRowboat.generated.h"

UCLASS()
class ANANTA_API ACityRowboat : public AANANTACityVehicle
{
    GENERATED_BODY()

public:
    ACityRowboat();
    virtual void BeginPlay() override;
    virtual void Drive(float Throttle, float Steering, bool bBrake, float DeltaTime) override;
    virtual bool FindSafeExit(const APawn* Player, FVector& OutLocation) const override;
};
