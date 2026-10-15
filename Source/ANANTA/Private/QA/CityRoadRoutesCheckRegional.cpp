#include "QA/CityRoadRoutesCheck.h"

#include "City/Mobility/CityRouteVehicle.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

void UCityRoadRoutesCheck::SelectRegion()
{
    FParse::Value(FCommandLine::Get(), TEXT("CityRoadRoutesRegion="), Region);
    if (Region == TEXT("Core"))
    {
        return;
    }
    if (Region == TEXT("East"))
    {
        SourcePlayerLocation = FVector(200000, 0, 100);
    }
    else if (Region == TEXT("West"))
    {
        SourcePlayerLocation = FVector(-244000, 420, 100);
    }
    else if (Region == TEXT("South"))
    {
        SourcePlayerLocation = FVector(-28000, -215580, 100);
    }
    else if (Region == TEXT("NorthEast"))
    {
        SourcePlayerLocation = FVector(188000, 288420, 100);
    }
    else
    {
        bValidRegion = false;
    }
}

bool UCityRoadRoutesCheck::HasUnexpectedFleet() const
{
    for (TActorIterator<ACityRouteVehicle> It(GetWorld()); It; ++It)
    {
        // Tau author san tiep tuc chay; chi cac xe cua fixture duoc phep tren duong bo.
        if (It->GetKind() == ECityTransportKind::PassengerTrain)
        {
            continue;
        }
        const ACityRouteVehicle* Vehicle = *It;
        const bool bFixture = Results.ContainsByPredicate([Vehicle](const FCityRoadResult& Result)
        {
            return Result.Probes.ContainsByPredicate([Vehicle](const FCityRoadProbe& Probe)
            {
                return Probe.Vehicle.Get() == Vehicle;
            });
        });
        if (!bFixture)
        {
            return true;
        }
    }
    return false;
}
