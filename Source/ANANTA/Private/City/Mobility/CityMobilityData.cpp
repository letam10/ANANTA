#include "City/Mobility/CityMobilityData.h"

const TCHAR* CityMobility::MeshName(const ECityTransportKind Kind)
{
    static const TCHAR* Names[] = {
        TEXT("Coach"), TEXT("CityBus"), TEXT("Taxi"), TEXT("BoxTruck"), TEXT("CargoTruck"),
        TEXT("TankerTruck"), TEXT("PoliceCar"), TEXT("Ambulance"), TEXT("CargoShip"),
        TEXT("Motorboat"), TEXT("Sailboat"), TEXT("FireEngine"), TEXT("PassengerTrain")
    };
    const int32 Index = static_cast<int32>(Kind);
    return Index >= 0 && Index < UE_ARRAY_COUNT(Names) ? Names[Index] : TEXT("");
}

float CityMobility::CruiseSpeed(const ECityTransportKind Kind)
{
    if (Kind == ECityTransportKind::CargoShip || Kind == ECityTransportKind::Sailboat)
    {
        return 450.f;
    }
    return Kind == ECityTransportKind::Motorboat ? 1000.f : 750.f;
}

FCityTransportRoute CityMobility::MakeRoute(const ECityTransportKind Kind)
{
    FCityTransportRoute Result;
    Result.Id = FName(MeshName(Kind));
    Result.bWater = Kind == ECityTransportKind::CargoShip || Kind == ECityTransportKind::Motorboat
        || Kind == ECityTransportKind::Sailboat;
    Result.bRail = Kind == ECityTransportKind::PassengerTrain;
    if (Result.bRail)
    {
        Result.Points = {
            FVector(-68000, 198500, 51), FVector(-64000, 198500, 51),
            FVector(-65333.333, 198500, 51), FVector(-66666.667, 198500, 51)
        };
        Result.Stops = {0, 1};
        Result.ReverseTargets = {2, 3, 0};
        return Result;
    }
    if (Result.bWater)
    {
        const float Offset = (static_cast<int32>(Kind) - 8) * 4200.f;
        const float X = 131000.f + Offset;
        // Ben tau duoc author o bo dong, dong bo CityCoastalDistrict.py.
        Result.Points = {
            FVector(X, -141000, WaterLevel), FVector(X, -136000, WaterLevel),
            FVector(X, -130000, WaterLevel), FVector(X, -135000, WaterLevel)
        };
        Result.Stops = {0};
        Result.ReverseTargets = {3, 0};
        return Result;
    }
    const int32 Index = static_cast<int32>(Kind);
    const float X0 = -36000.f + (Index % 4) * 24000.f;
    const float X1 = X0 + 24000.f;
    const float Y0 = Index < 4 ? 0.f : -24000.f;
    const float Y1 = Y0 + 24000.f;
    // Chieu di co via he ben phai (+Y local); diem dung nam giua doan thang.
    Result.Points = {
        FVector(X0 + 6000, Y0 + 420, 0), FVector(X1 - 420, Y0 + 420, 0),
        FVector(X1 - 420, Y0 + 6000, 0), FVector(X1 - 420, Y1 - 420, 0),
        FVector(X1 - 6000, Y1 - 420, 0), FVector(X0 + 420, Y1 - 420, 0),
        FVector(X0 + 420, Y1 - 6000, 0), FVector(X0 + 420, Y0 + 420, 0)
    };
    Result.Stops = {0, 2, 4, 6};
    return Result;
}
