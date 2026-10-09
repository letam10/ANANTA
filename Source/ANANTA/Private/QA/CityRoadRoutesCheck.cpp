#include "QA/CityRoadRoutesCheck.h"

#include "City/ANANTACitySubsystem.h"
#include "City/Mobility/CityRouteVehicle.h"
#include "City/Mobility/CityTransportManager.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityRoadRoutesCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && World->GetMapName() == TEXT("ANANTA_City")
        && FParse::Param(FCommandLine::Get(), TEXT("CityRoadRoutesCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

void UCityRoadRoutesCheck::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    for (int32 Index = 0; Index < 8; ++Index)
    {
        auto& Result = Results.AddDefaulted_GetRef();
        const auto Kind = static_cast<ECityTransportKind>(Index);
        Result.Kind = CityMobility::MeshName(Kind);
        Result.Route = CityMobility::MakeRoute(Kind);
        // Hai xe lech mot tram: runtime luan phien don/tra khach, can ca hai de phu bon tram.
        Result.Probes.SetNum(2);
        Result.Probes[1].InitialPoint = 2;
    }
    // Chan manager ngay khi spawn, truoc tick dau; chi subsystem QA nay dang ky callback.
    SpawnHandle = GetWorld()->AddOnActorSpawnedHandler(
        FOnActorSpawned::FDelegate::CreateUObject(this, &UCityRoadRoutesCheck::SuppressManager));
    for (TActorIterator<ACityTransportManager> It(GetWorld()); It; ++It)
    {
        SuppressManager(*It);
    }
}

void UCityRoadRoutesCheck::SuppressManager(AActor* Actor)
{
    auto* Manager = Cast<ACityTransportManager>(Actor);
    if (Manager && Manager->IsActorTickEnabled())
    {
        PausedManagers.AddUnique(Manager);
        Manager->SetActorTickEnabled(false);
    }
}

TStatId UCityRoadRoutesCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityRoadRoutesCheck, STATGROUP_Tickables);
}

void UCityRoadRoutesCheck::Tick(const float DeltaTime)
{
    if (bFinished)
    {
        if (++ExitFrames == 3)
        {
            FPlatformMisc::RequestExitWithStatus(false, bPassed ? 0 : 1);
        }
        return;
    }
    const double Now = FPlatformTime::Seconds();
    if (StartedAt == 0)
    {
        StartedAt = Now;
    }
    if (ReadyAt == 0)
    {
        if (Now - StartedAt > 60)
        {
            Finish(TEXT("World or authored road route streaming readiness exceeded 60 seconds"));
            return;
        }
        if (!GetWorld()->HasBegunPlay() || !GetWorld()->GetFirstPlayerController())
        {
            return;
        }
        if (!Observer.IsValid() && !PrepareStreaming())
        {
            return;
        }
        if (!StreamingSource.IsValid() || !StreamingSource->IsStreamingCompleted())
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
        const auto* Instance = GetWorld()->GetGameInstance();
        const auto* State = Instance ? Instance->GetSubsystem<UANANTACitySubsystem>() : nullptr;
        if (!State || !State->IsUsingQASlot())
        {
            Finish(TEXT("Isolated QA save state unavailable"));
            return;
        }
        ReadyAt = Now;
        SpawnVehicles();
    }
    if (!StreamingSource.IsValid() || !StreamingSource->IsStreamingCompleted())
    {
        Finish(TEXT("Authored road route streaming coverage was lost"));
        return;
    }
    bool bAllDone = true;
    for (FCityRoadResult& Result : Results)
    {
        for (FCityRoadProbe& Probe : Result.Probes)
        {
            Observe(Result, Probe, Now);
            bAllDone &= Probe.Status != TEXT("PENDING");
        }
    }
    if (bAllDone || Now - ReadyAt >= 240)
    {
        Finish(bAllDone ? TEXT("All eight authored road route outcomes recorded")
            : TEXT("Authored road route round trip exceeded 240 seconds after readiness"));
    }
}

void UCityRoadRoutesCheck::Deinitialize()
{
    if (!bFinished && StartedAt > 0 && GetWorld()->GetMapName() == TEXT("ANANTA_City"))
    {
        Finish(TEXT("World ended before authored road route verification completed"));
        // Khong yeu cau EngineExit trong teardown; runner se tu choi bao cao FAIL.
    }
    Cleanup();
    Super::Deinitialize();
}
