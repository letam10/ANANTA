#pragma once

#include "CoreMinimal.h"

enum class ECityTransportKind : uint8
{
    Coach, CityBus, Taxi, BoxTruck, CargoTruck, TankerTruck,
    PoliceCar, Ambulance, CargoShip, Motorboat, Sailboat, Count
};

struct FCityTransportRoute
{
    FName Id;
    TArray<FVector> Points;
    TArray<int32> Stops;
    TArray<int32> ReverseTargets;
    bool bWater = false;
};

namespace CityMobility
{
    constexpr int32 MaximumVehicles = 8;
    constexpr float ActivationDistance = 7000.f;
    constexpr float RetirementDistance = 11000.f;
    constexpr float WaterLevel = -120.f;
    const TCHAR* MeshName(ECityTransportKind Kind);
    FCityTransportRoute MakeRoute(ECityTransportKind Kind);
    float CruiseSpeed(ECityTransportKind Kind);
}
