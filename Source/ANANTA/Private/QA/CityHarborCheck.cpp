#include "QA/CityHarborCheck.h"

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

bool UCityHarborCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && World->GetMapName() == TEXT("ANANTA_City")
        && FParse::Param(FCommandLine::Get(), TEXT("CityHarborCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

void UCityHarborCheck::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    for (const TCHAR* Kind : {TEXT("CargoShip"), TEXT("Motorboat"), TEXT("Sailboat")})
    {
        Results.AddDefaulted_GetRef().Kind = Kind;
    }
    // Chan manager ngay khi spawn, truoc tick dau; chi subsystem QA nay dang ky callback.
    SpawnHandle = GetWorld()->AddOnActorSpawnedHandler(
        FOnActorSpawned::FDelegate::CreateUObject(this, &UCityHarborCheck::SuppressManager));
    for (TActorIterator<ACityTransportManager> It(GetWorld()); It; ++It)
    {
        SuppressManager(*It);
    }
}

void UCityHarborCheck::SuppressManager(AActor* Actor)
{
    auto* Manager = Cast<ACityTransportManager>(Actor);
    if (Manager && Manager->IsActorTickEnabled())
    {
        PausedManagers.AddUnique(Manager);
        Manager->SetActorTickEnabled(false);
    }
}

TStatId UCityHarborCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityHarborCheck, STATGROUP_Tickables);
}

void UCityHarborCheck::Tick(const float DeltaTime)
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
            Finish(TEXT("World or authored harbour streaming readiness exceeded 60 seconds"));
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
        SpawnVessels();
    }
    if (!StreamingSource.IsValid() || !StreamingSource->IsStreamingCompleted())
    {
        Finish(TEXT("Authored dock or route streaming coverage was lost"));
        return;
    }
    bool bAllDone = true;
    for (FCityHarborResult& Result : Results)
    {
        Observe(Result, Now);
        bAllDone &= Result.Status != TEXT("PENDING");
    }
    if (bAllDone || Now - ReadyAt >= 180)
    {
        Finish(bAllDone ? TEXT("All three authored route outcomes recorded")
            : TEXT("Authored harbour round trip exceeded 180 seconds after readiness"));
    }
}

void UCityHarborCheck::Deinitialize()
{
    if (!bFinished && StartedAt > 0 && GetWorld()->GetMapName() == TEXT("ANANTA_City"))
    {
        Finish(TEXT("World ended before authored harbour verification completed"));
        // Khong yeu cau EngineExit trong teardown; runner se tu choi bao cao FAIL.
    }
    Cleanup();
    Super::Deinitialize();
}
