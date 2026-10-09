#include "QA/CityRailCheck.h"

#include "City/ANANTACitySubsystem.h"
#include "City/Mobility/CityRailShuttle.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

bool UCityRailCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && World->GetMapName() == TEXT("ANANTA_City")
        && FParse::Param(FCommandLine::Get(), TEXT("CityRailCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityRailCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityRailCheck, STATGROUP_Tickables);
}

void UCityRailCheck::Tick(const float DeltaTime)
{
    if (bFinished || !GetWorld()->HasBegunPlay())
    {
        return;
    }
    const double Now = FPlatformTime::Seconds();
    if (StartedAt == 0)
    {
        StartedAt = Now;
        const auto* Instance = GetWorld()->GetGameInstance();
        const auto* State = Instance ? Instance->GetSubsystem<UANANTACitySubsystem>() : nullptr;
        if (!State || !State->IsUsingQASlot())
        {
            Finish(false, TEXT("Isolated QA save unavailable"));
            return;
        }
        // Camera nap vung ga that; khong doi geometry, toc do hay vi tri cua tau.
        AActor* Actor = GetWorld()->SpawnActor<AActor>();
        auto* Root = NewObject<USceneComponent>(Actor);
        Actor->SetRootComponent(Root);
        Root->RegisterComponent();
        Actor->SetActorLocation(FVector(-66000, 198000, 500));
        auto* Streaming = NewObject<UWorldPartitionStreamingSourceComponent>(Actor);
        Streaming->RegisterComponent();
        Observer = Actor;
        Source = Streaming;
    }
    if (ReadyAt == 0)
    {
        if (Now - StartedAt > 60)
        {
            Finish(false, TEXT("Authored station readiness exceeded 60 seconds"));
            return;
        }
        if (!Source.IsValid() || !Source->IsStreamingCompleted())
        {
            StableAt = 0;
            return;
        }
        if (StableAt == 0)
        {
            StableAt = Now;
        }
        if (Now - StableAt < 2)
        {
            return;
        }
        for (TActorIterator<ACityRailShuttle> It(GetWorld()); It; ++It)
        {
            auto& Result = Results.AddDefaulted_GetRef();
            Result.Train = *It;
            Result.Start = It->GetActorLocation();
            Result.Previous = Result.Start;
        }
        if (Results.Num() != 2)
        {
            Finish(false, TEXT("Station must contain two authored shuttle actors"));
            return;
        }
        const double TrackDistance = FMath::Abs(Results[0].Start.Y - Results[1].Start.Y);
        if (!FMath::IsNearlyEqual(TrackDistance, 1000.0, 1.0))
        {
            Finish(false, TEXT("Shuttles must occupy distinct parallel tracks"));
            return;
        }
        ReadyAt = Now;
    }
    if (!Source.IsValid() || !Source->IsStreamingCompleted())
    {
        Finish(false, TEXT("Station streaming coverage lost"));
        return;
    }
    bool bAllPassed = true;
    for (auto& Result : Results)
    {
        auto* Train = Result.Train.Get();
        if (!Train)
        {
            Finish(false, TEXT("Authored train disappeared"));
            return;
        }
        const FVector Location = Train->GetActorLocation();
        Result.Travel += FVector::Dist(Location, Result.Previous);
        Result.Previous = Location;
        Result.MaximumDistance = FMath::Max(Result.MaximumDistance, FVector::Dist(Location, Result.Start));
        if (FMath::Abs(Location.Y - Result.Start.Y) > 1)
        {
            Finish(false, TEXT("Train left authored straight track"));
            return;
        }
        Result.bPassed |= Train->IsStopped() && Train->GetBoardingCount() >= 2
            && Train->GetAlightingCount() >= 1 && Result.MaximumDistance >= 1900
            && Result.Travel >= 3800 && FVector::Dist(Location, Result.Start) < 100;
        bAllPassed &= Result.bPassed;
    }
    if (bAllPassed || Now - ReadyAt > 180)
    {
        Finish(bAllPassed, bAllPassed ? TEXT("Both shuttles boarded, alighted and returned")
            : TEXT("Authored rail round trip exceeded 180 seconds"));
    }
}

void UCityRailCheck::Finish(const bool bPassed, const FString& Reason)
{
    bFinished = true;
    auto Report = MakeShared<FJsonObject>();
    Report->SetBoolField(TEXT("passed"), bPassed);
    Report->SetStringField(TEXT("scope"), TEXT("authored-map rail physics fixture"));
    Report->SetStringField(TEXT("reason"), Reason);
    Report->SetStringField(TEXT("completedUtc"), FDateTime::UtcNow().ToIso8601());
    Report->SetNumberField(TEXT("elapsedSeconds"), ReadyAt > 0 ? FPlatformTime::Seconds() - ReadyAt : 0);
    TArray<TSharedPtr<FJsonValue>> Rows;
    for (const auto& Result : Results)
    {
        const auto* Train = Result.Train.Get();
        auto Row = MakeShared<FJsonObject>();
        Row->SetBoolField(TEXT("passed"), Result.bPassed);
        Row->SetStringField(TEXT("actor"), GetNameSafe(Train));
        Row->SetNumberField(TEXT("boarded"), Train ? Train->GetBoardingCount() : 0);
        Row->SetNumberField(TEXT("alighted"), Train ? Train->GetAlightingCount() : 0);
        Row->SetNumberField(TEXT("travelCm"), Result.Travel);
        Row->SetNumberField(TEXT("maxDistanceCm"), Result.MaximumDistance);
        Row->SetStringField(TEXT("blocker"), Train ? Train->GetBlockedReason() : TEXT("Missing actor"));
        Rows.Add(MakeShared<FJsonValueObject>(Row));
    }
    Report->SetArrayField(TEXT("results"), Rows);
    FString Contents;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Contents));
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityRailCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    const bool bSaved = FFileHelper::SaveStringToFile(Contents, *(Directory / TEXT("Report.json")));
    UE_LOG(LogTemp, Display, TEXT("CITY_RAIL_CHECK_FINISH success=%d reason=%s"), bPassed && bSaved, *Reason);
    FPlatformMisc::RequestExitWithStatus(false, bPassed && bSaved ? 0 : 1);
}
