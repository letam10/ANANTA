#pragma once

#include "City/Mobility/CityRouteVehicle.h"
#include "CityRailShuttle.generated.h"

UCLASS()
class ANANTA_API ACityRailShuttle : public ACityRouteVehicle
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere)
    FVector StationCentre = FVector(-66000, 198000, 51);

    UPROPERTY(EditAnywhere)
    int32 DirectionSign = 1;
};
