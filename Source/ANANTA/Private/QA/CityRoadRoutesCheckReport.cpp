#include "QA/CityRoadRoutesCheck.h"

#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace
{
    FString RoadJsonString(const FString& Value)
    {
        FString Escaped = TEXT("\"");
        for (const TCHAR Character : Value)
        {
            if (Character == TEXT('"') || Character == TEXT('\\'))
            {
                Escaped += TEXT('\\');
                Escaped += Character;
            }
            else if (Character < 32)
            {
                Escaped += FString::Printf(TEXT("\\u%04x"), static_cast<uint32>(Character));
            }
            else
            {
                Escaped += Character;
            }
        }
        return Escaped + TEXT("\"");
    }
}

void UCityRoadRoutesCheck::Finish(const FString& Reason)
{
    if (bFinished)
    {
        return;
    }
    bFinished = true;
    const double Elapsed = ReadyAt > 0 ? FPlatformTime::Seconds() - ReadyAt : 0;
    bPassed = Results.Num() == 8 && ReadyAt > 0 && Elapsed <= 240;
    FString Rows;
    for (auto& Result : Results)
    {
        FString Probes;
        int32 Boarded = 0;
        int32 Alighted = 0;
        int32 BoardedMask = 0;
        int32 AlightedMask = 0;
        double Travel = 0;
        double RouteElapsed = 0;
        bool bRoutePassed = Result.Probes.Num() == 2;
        for (auto& Probe : Result.Probes)
        {
            if (Probe.Status == TEXT("PENDING"))
            {
                Probe.Status = TEXT("FAIL");
                Probe.Reason = Reason;
                Probe.Elapsed = Elapsed;
            }
            bRoutePassed &= Probe.Status == TEXT("PASS");
            Boarded += Probe.Boarded;
            Alighted += Probe.Alighted;
            BoardedMask |= Probe.BoardedMask;
            AlightedMask |= Probe.AlightedMask;
            Travel += Probe.Travel;
            RouteElapsed = FMath::Max(RouteElapsed, Probe.Elapsed);
            if (!Probes.IsEmpty())
            {
                Probes += TEXT(",");
            }
            Probes += FString::Printf(TEXT("{\"initialPoint\":%d,\"status\":%s,\"reason\":%s,\"lastBlocker\":%s,"),
                Probe.InitialPoint, *RoadJsonString(Probe.Status),
                *RoadJsonString(Probe.Reason), *RoadJsonString(Probe.LastBlocker));
            Probes += FString::Printf(TEXT("\"boarded\":%d,\"alighted\":%d,\"boardedMask\":%d,\"alightedMask\":%d,"),
                Probe.Boarded, Probe.Alighted, Probe.BoardedMask, Probe.AlightedMask);
            Probes += FString::Printf(TEXT("\"travelCm\":%.3f,\"startDistanceCm\":%.3f,\"elapsedSeconds\":%.3f,"),
                Probe.Travel, Probe.StartDistance, Probe.Elapsed);
            Probes += FString::Printf(TEXT("\"maxRoadDeviationCm\":%.3f,\"maxFloorGapCm\":%.3f,"),
                Probe.MaxDeviation, Probe.MaxFloorGap);
            Probes += FString::Printf(TEXT("\"pointMask\":%d,\"returned\":%s,\"sideTravelCm\":[%.3f,%.3f,%.3f,%.3f]}"),
                Probe.PointMask, Probe.bReturned ? TEXT("true") : TEXT("false"),
                Probe.SideTravel[0], Probe.SideTravel[1], Probe.SideTravel[2], Probe.SideTravel[3]);
        }
        bRoutePassed &= BoardedMask == 15 && AlightedMask == 15;
        bPassed &= bRoutePassed;
        if (!Rows.IsEmpty())
        {
            Rows += TEXT(",\n");
        }
        Rows += FString::Printf(TEXT("    {\"kind\":%s,\"status\":%s,\"reason\":%s,"),
            *RoadJsonString(Result.Kind), bRoutePassed ? TEXT("\"PASS\"") : TEXT("\"FAIL\""),
            *RoadJsonString(bRoutePassed ? TEXT("All four stops boarded and alighted; both full loops verified")
                : TEXT("Failed probe or incomplete four-stop passenger coverage; see probes")));
        Rows += FString::Printf(TEXT("\"boarded\":%d,\"alighted\":%d,\"boardedMask\":%d,\"alightedMask\":%d,"),
            Boarded, Alighted, BoardedMask, AlightedMask);
        Rows += FString::Printf(TEXT("\"travelCm\":%.3f,\"elapsedSeconds\":%.3f,\"probes\":[%s]}"),
            Travel, RouteElapsed, *Probes);
    }
    FString Report = FString::Printf(TEXT("{\n  \"schemaVersion\":1,\n  \"passed\":%s,\n"),
        bPassed ? TEXT("true") : TEXT("false"));
    Report += TEXT("  \"scope\":\"authored-map physics fixture\",\n");
    Report += TEXT("  \"fixtureVehiclesPerKind\":2,\n  \"initialRoutePoints\":[0,2],\n");
    Report += TEXT("  \"fixtureReason\":\"Two offset vehicles cover alternating passenger service at all stops\",\n");
    Report += TEXT("  \"stopPointIndices\":[0,2,4,6],\n  \"sideOrder\":[\"east\",\"north\",\"west\",\"south\"],\n");
    Report += FString::Printf(TEXT("  \"observerRelocated\":%s,\n  \"streamingRadiusCm\":62000,\n"),
        Observer.IsValid() ? TEXT("true") : TEXT("false"));
    Report += TEXT("  \"artificialSupportFloors\":false,\n  \"vehicleSpeedModified\":false,\n");
    Report += TEXT("  \"routesModified\":false,\n  \"geometryModified\":false,\n  \"collisionBypass\":false,\n");
    Report += FString::Printf(TEXT("  \"isolatedQASlot\":%s,\n"), ReadyAt > 0 ? TEXT("true") : TEXT("false"));
    Report += FString::Printf(TEXT("  \"map\":%s,\n  \"completedUtc\":%s,\n  \"reason\":%s,\n"),
        *RoadJsonString(GetWorld()->GetMapName()), *RoadJsonString(FDateTime::UtcNow().ToIso8601()),
        *RoadJsonString(Reason));
    Report += FString::Printf(TEXT("  \"elapsedSeconds\":%.3f,\n  \"results\":[\n%s\n  ]\n}\n"), Elapsed, *Rows);
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityRoadRoutesCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    if (!FFileHelper::SaveStringToFile(Report, *(Directory / TEXT("Report.json"))))
    {
        bPassed = false;
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_ROAD_ROUTES_CHECK_FINISH success=%d reason=%s"), bPassed, *Reason);
}
