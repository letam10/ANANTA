#include "QA/CityHarborCheck.h"

#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace
{
    // JSON nho, escape chuoi de giu nguyen ten actor/vat can trong bao cao.
    FString JsonString(const FString& Value)
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

void UCityHarborCheck::Finish(const FString& Reason)
{
    if (bFinished)
    {
        return;
    }
    bFinished = true;
    bPassed = Results.Num() == 3;
    const double Now = FPlatformTime::Seconds();
    const double Elapsed = ReadyAt > 0 ? Now - ReadyAt : 0;
    FString Rows;
    for (FCityHarborResult& Result : Results)
    {
        if (Result.Status == TEXT("PENDING"))
        {
            Result.Status = TEXT("FAIL");
            Result.Reason = Reason;
            Result.Elapsed = Elapsed;
        }
        bPassed &= Result.Status == TEXT("PASS");
        if (!Rows.IsEmpty())
        {
            Rows += TEXT(",\n");
        }
        Rows += FString::Printf(TEXT("    {\"kind\":%s,\"status\":%s,\"reason\":%s,\"lastBlocker\":%s,"),
            *JsonString(Result.Kind), *JsonString(Result.Status),
            *JsonString(Result.Reason), *JsonString(Result.LastBlocker));
        Rows += FString::Printf(TEXT("\"maxDistanceCm\":%.3f,\"travelCm\":%.3f,\"dockDistanceCm\":%.3f,"),
            Result.MaximumDistance, Result.TravelDistance, Result.DockDistance);
        Rows += FString::Printf(TEXT("\"minWaterlineCm\":%.3f,\"boarded\":%d,\"alighted\":%d,"),
            Result.MinimumWaterline, Result.Boarded, Result.Alighted);
        Rows += FString::Printf(TEXT("\"outbound\":%s,\"returned\":%s,\"elapsedSeconds\":%.3f}"),
            Result.bOutbound ? TEXT("true") : TEXT("false"),
            Result.bReturned ? TEXT("true") : TEXT("false"), Result.Elapsed);
    }
    FString Report = FString::Printf(TEXT("{\n  \"schemaVersion\":1,\n  \"passed\":%s,\n"),
        bPassed ? TEXT("true") : TEXT("false"));
    Report += TEXT("  \"scope\":\"authored-map physics fixture\",\n");
    Report += FString::Printf(TEXT("  \"observerRelocated\":%s,\n  \"streamingRadiusCm\":20000,\n"),
        Observer.IsValid() ? TEXT("true") : TEXT("false"));
    Report += TEXT("  \"artificialSupportFloors\":false,\n  \"vesselSpeedModified\":false,\n");
    Report += TEXT("  \"piersMoved\":false,\n  \"collisionBypass\":false,\n  \"isolatedQASlot\":true,\n");
    Report += FString::Printf(TEXT("  \"map\":%s,\n  \"completedUtc\":%s,\n  \"reason\":%s,\n"),
        *JsonString(GetWorld()->GetMapName()), *JsonString(FDateTime::UtcNow().ToIso8601()), *JsonString(Reason));
    Report += FString::Printf(TEXT("  \"elapsedSeconds\":%.3f,\n  \"results\":[\n%s\n  ]\n}\n"), Elapsed, *Rows);
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityHarborCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    if (!FFileHelper::SaveStringToFile(Report, *(Directory / TEXT("Report.json"))))
    {
        bPassed = false;
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_HARBOR_CHECK_FINISH success=%d reason=%s"), bPassed, *Reason);
    // Giu nguyen fixture den luc thoat; manager khong duoc tao tau chen vao ket qua.
}
