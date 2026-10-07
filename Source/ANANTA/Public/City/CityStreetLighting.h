#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CityStreetLighting.generated.h"

class ADirectionalLight;
class USpotLightComponent;

UCLASS()
class ANANTA_API ACityStreetLighting : public AActor
{
    GENERATED_BODY()

public:
    ACityStreetLighting();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    TArray<FVector> LampPositions;

    UPROPERTY()
    TArray<TObjectPtr<USpotLightComponent>> Lights;

    UPROPERTY()
    TObjectPtr<ADirectionalLight> Sun;
};
