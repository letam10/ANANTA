#include "QA/CityNavigationCheck.h"

#include "City/ANANTACityController.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"

bool UCityNavigationCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld()
        && FParse::Param(FCommandLine::Get(), TEXT("CityNavigationCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityNavigationCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityNavigationCheck, STATGROUP_Tickables);
}

void UCityNavigationCheck::Tick(const float DeltaTime)
{
    if (bFinished || !GetWorld()->HasBegunPlay())
    {
        return;
    }
    const double Now = FPlatformTime::Seconds();
    if (StartTime == 0)
    {
        StartTime = Now;
    }
    if (Now - StartTime > 40)
    {
        bFinished = true;
        UE_LOG(LogTemp, Error, TEXT("CITY_NAVIGATION_CHECK_FINISH success=0 timeout"));
        FPlatformMisc::RequestExitWithStatus(false, 1);
        return;
    }
    if (Now - StartTime < 3 || Now - LastCheck < 1)
    {
        return;
    }
    LastCheck = Now;
    auto* PC = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    auto* Nav = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
    if (!PC || !PC->CanCaptureProgress() || !PC->GetPawn() || !Nav)
    {
        return;
    }
    // Truy van navmesh that; khong dung duong di du phong truc tiep cua AI.
    const FVector Origin = PC->GetPawn()->GetActorLocation();
    FNavLocation Start;
    FNavLocation End;
    const FVector Extent(100, 100, 250);
    if (!Nav->ProjectPointToNavigation(Origin, Start, Extent)
        || !Nav->ProjectPointToNavigation(Origin + FVector(1600, 0, 0), End, Extent))
    {
        return;
    }
    const auto* Path = UNavigationSystemV1::FindPathToLocationSynchronously(
        GetWorld(), Start.Location, End.Location, PC->GetPawn());
    if (!Path || !Path->IsValid() || Path->IsPartial() || Path->PathPoints.Num() < 2)
    {
        return;
    }
    bFinished = true;
    UE_LOG(LogTemp, Display, TEXT("CITY_NAVIGATION_CHECK_FINISH success=1 points=%d length=%.1f"),
        Path->PathPoints.Num(), Path->GetPathLength());
    FPlatformMisc::RequestExitWithStatus(false, 0);
}
