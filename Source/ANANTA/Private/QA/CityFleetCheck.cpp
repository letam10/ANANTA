#include "QA/CityFleetCheck.h"

#include "City/Mobility/CityRouteVehicle.h"
#include "City/Mobility/CityTransitPassenger.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"

bool UCityFleetCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && FParse::Param(FCommandLine::Get(), TEXT("CityFleetCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityFleetCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityFleetCheck, STATGROUP_Tickables);
}

void UCityFleetCheck::Tick(const float DeltaTime)
{
    if (bFinished)
    {
        if (++ExitFrames == 3)
        {
            FPlatformMisc::RequestExitWithStatus(false, bPassed ? 0 : 1);
        }
        return;
    }
    if (!GetWorld()->HasBegunPlay())
    {
        return;
    }
    if (!bStarted)
    {
        bStarted = true;
        StartedAt = FPlatformTime::Seconds();
        if (!BuildFixtures())
        {
            return;
        }
    }
    if (FPlatformTime::Seconds() - StartedAt > 240)
    {
        Finish(false, TEXT("Physical fleet fixtures exceeded 240 seconds wall time"));
        return;
    }
    bool bAllDone = Fixtures.Num() == static_cast<int32>(ECityTransportKind::Count);
    for (FCityFleetFixture& Fixture : Fixtures)
    {
        if (!UpdateFixture(Fixture, DeltaTime))
        {
            return;
        }
        bAllDone &= Fixture.Stage == 4;
    }
    if (bAllDone)
    {
        Finish(true, TEXT("All authored controlled physical fixtures passed; no FPS or ordinary-route claim"));
    }
}

void UCityFleetCheck::Cleanup()
{
    for (FCityFleetFixture& Fixture : Fixtures)
    {
        if (Fixture.Vehicle.IsValid())
        {
            Fixture.Vehicle->Destroy();
        }
    }
    for (const TWeakObjectPtr<AActor>& Actor : Geometry)
    {
        if (Actor.IsValid())
        {
            Actor->Destroy();
        }
    }
    Geometry.Empty();
}

void UCityFleetCheck::Finish(const bool bSuccess, const FString& Detail)
{
    bFinished = true;
    bPassed = bSuccess;
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityFleetCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    FString Report = FString::Printf(TEXT("passed=%d\nfixtureCount=%d\nreason=%s\n"),
        bSuccess, Fixtures.Num(), *Detail);
    Report += TEXT("scope=controlled collision fixtures using real vehicle and passenger ticks\n");
    Report += Evidence;
    if (!FFileHelper::SaveStringToFile(Report, *(Directory / TEXT("Report.txt"))))
    {
        bPassed = false;
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_FLEET_CHECK_FINISH success=%d reason=%s"), bPassed, *Detail);
    Cleanup();
}

void UCityFleetCheck::Deinitialize()
{
    Cleanup();
    Super::Deinitialize();
}
