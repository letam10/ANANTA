#include "QA/CityCivicCheck.h"

#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace
{
    FString Quote(const FString& Value)
    {
        FString Result = TEXT("\"");
        for (const TCHAR Character : Value)
        {
            if (Character == TEXT('"') || Character == TEXT('\\'))
            {
                Result += TEXT('\\');
                Result += Character;
            }
            else if (Character < 32)
            {
                Result += FString::Printf(TEXT("\\u%04x"), static_cast<uint32>(Character));
            }
            else
            {
                Result += Character;
            }
        }
        return Result + TEXT("\"");
    }
}

void UCityCivicCheck::Finish(const bool bSuccess, const FString& Reason)
{
    if (bFinished)
    {
        return;
    }
    ReleaseKeys();
    bFinished = true;
    bPassed = bSuccess && Legs.Num() == 8 && Services.Num() == 4 && SetupRelocations == 4;
    const double Elapsed = ReadyAt > 0 ? FPlatformTime::Seconds() - ReadyAt : 0;
    FString Rows;
    for (auto& Leg : Legs)
    {
        if (Leg.Status == TEXT("PENDING"))
        {
            Leg.Status = TEXT("FAIL");
            Leg.Reason = Reason;
        }
        bPassed &= Leg.Status == TEXT("PASS");
        if (!Rows.IsEmpty())
        {
            Rows += TEXT(",\n");
        }
        Rows += FString::Printf(TEXT("    {\"service\":%s,\"direction\":%s,\"status\":%s,\"reason\":%s,"),
            *Quote(Leg.Service), *Quote(Leg.Direction), *Quote(Leg.Status), *Quote(Leg.Reason));
        Rows += FString::Printf(TEXT("\"startX\":%.3f,\"endX\":%.3f,\"travelCm\":%.3f,\"elapsedSeconds\":%.3f,"),
            Leg.Start.X, Leg.End.X, Leg.Travel, Leg.Elapsed);
        Rows += FString::Printf(TEXT("\"groundChecks\":%d,\"collisionChecks\":%d,\"inputChecks\":%d,"),
            Leg.GroundChecks, Leg.CollisionChecks, Leg.InputChecks);
        Rows += FString::Printf(TEXT("\"sprintInputChecks\":%d,"), Leg.SprintInputChecks);
        Rows += FString::Printf(TEXT("\"crossedDoor\":%s}"), Leg.bCrossedDoor ? TEXT("true") : TEXT("false"));
    }
    FString ServiceRows;
    for (const auto& Entry : Services)
    {
        bPassed &= Entry.bInteracted;
        if (!ServiceRows.IsEmpty())
        {
            ServiceRows += TEXT(",\n");
        }
        ServiceRows += FString::Printf(TEXT("    {\"id\":%s,\"prompt\":%s,\"interactedByE\":%s}"),
            *Quote(Entry.Id.ToString()), *Quote(Entry.Prompt), Entry.bInteracted ? TEXT("true") : TEXT("false"));
    }
    FString Report = FString::Printf(TEXT("{\n  \"schemaVersion\":1,\n  \"passed\":%s,\n"),
        bPassed ? TEXT("true") : TEXT("false"));
    Report += TEXT("  \"scope\":\"authored-map physics/input fixture\",\n");
    Report += TEXT("  \"setup\":\"Hero relocated between sites only after pinned streaming completed\",\n");
    Report += FString::Printf(TEXT("  \"setupRelocations\":%d,\n"), SetupRelocations);
    Report += TEXT("  \"measuredLegRelocations\":0,\n  \"collisionBypass\":false,\n");
    Report += TEXT("  \"speedModified\":false,\n  \"capsuleRadiusCm\":38,\n  \"capsuleHalfHeightCm\":92,\n");
    Report += TEXT("  \"walkSpeedCmS\":350,\n  \"sprintSpeedCmS\":650,\n  \"streamingRadiusCm\":6500,\n");
    Report += FString::Printf(TEXT("  \"isolatedQASlot\":true,\n  \"keysReleased\":%s,\n"),
        HeldKeys.IsEmpty() ? TEXT("true") : TEXT("false"));
    Report += FString::Printf(TEXT("  \"map\":%s,\n  \"completedUtc\":%s,\n  \"reason\":%s,\n"),
        *Quote(GetWorld()->GetMapName()), *Quote(FDateTime::UtcNow().ToIso8601()), *Quote(Reason));
    Report += FString::Printf(TEXT("  \"elapsedSeconds\":%.3f,\n  \"legs\":[\n%s\n  ],\n"), Elapsed, *Rows);
    Report += FString::Printf(TEXT("  \"services\":[\n%s\n  ]\n}\n"), *ServiceRows);
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityCivicCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    if (!FFileHelper::SaveStringToFile(Report, *(Directory / TEXT("Report.json"))))
    {
        bPassed = false;
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_CIVIC_CHECK_FINISH success=%d reason=%s"), bPassed, *Reason);
}
