#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CityTransitPassenger.generated.h"

class ACityRouteVehicle;

enum class ECityPassengerPhase : uint8
{
    Approaching, Seated, Alighting, Finished
};

UCLASS()
class ANANTA_API ACityTransitPassenger : public ACharacter
{
    GENERATED_BODY()

public:
    ACityTransitPassenger();
    virtual void Tick(float DeltaTime) override;
    void Approach(ACityRouteVehicle* Vehicle, const FVector& Door);
    bool Alight(const FVector& Door, const FVector& Sidewalk);
    ECityPassengerPhase GetPhase() const { return Phase; }

private:
    TWeakObjectPtr<ACityRouteVehicle> Carrier;
    FVector Target = FVector::ZeroVector;
    ECityPassengerPhase Phase = ECityPassengerPhase::Approaching;
    float Elapsed = 0;
};
