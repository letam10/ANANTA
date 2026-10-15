#include "QA/CityStreamingJourney.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "Components/TraversalComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityStreamingJourney::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && FParse::Param(FCommandLine::Get(), TEXT("CityStreamingCheck"));
#endif
}

TStatId UCityStreamingJourney::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityStreamingJourney, STATGROUP_Tickables);
}

AANANTACityCharacter* UCityStreamingJourney::GetHero() const
{
    return Controller.IsValid() ? Cast<AANANTACityCharacter>(Controller->GetPawn()) : nullptr;
}

UANANTACitySubsystem* UCityStreamingJourney::GetState() const
{
    return GetWorld() && GetWorld()->GetGameInstance()
        ? GetWorld()->GetGameInstance()->GetSubsystem<UANANTACitySubsystem>() : nullptr;
}

bool UCityStreamingJourney::Begin()
{
    StartTime = Now;
    PhaseStart = Now;
    if (!GetWorld()->GetMapName().Contains(TEXT("ANANTA_City"))
        || !FParse::Param(FCommandLine::Get(), TEXT("CityQASlot")))
    {
        Finish(false, TEXT("Require ANANTA_City game world and explicit -CityQASlot"));
        return false;
    }
    static const TCHAR* Conflicts[] = {
        TEXT("CityCapture"), TEXT("CityInputSmoke"), TEXT("CityMissionCheck"), TEXT("CityMissionReload"),
        TEXT("CityServiceCheck"), TEXT("CityServiceReload"), TEXT("benchmark"), TEXT("NullRHI")
    };
    for (const TCHAR* Flag : Conflicts)
    {
        if (FParse::Param(FCommandLine::Get(), Flag))
        {
            Finish(false, FString::Printf(TEXT("Incompatible concurrent mode: %s"), Flag));
            return false;
        }
    }
    IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
    for (int32 Index = 0; Index < 4; ++Index)
    {
        if (!IFileManager::Get().Delete(*ScreenshotPath(Index), false))
        {
            Finish(false, TEXT("Cannot invalidate an old screenshot"));
            return false;
        }
    }
    Observe(TEXT("Waiting for fresh isolated ordinary on-foot play"));
    if (!WriteReport(false, false))
    {
        Finish(false, TEXT("Cannot write initial evidence"));
        return false;
    }
    return true;
}

void UCityStreamingJourney::Tick(const float DeltaTime)
{
    if (bFinished)
    {
        if (++ExitFrames == 3)
        {
            FPlatformMisc::RequestExitWithStatus(false, bPassed ? 0 : 1);
        }
        return;
    }
    if (!GetWorld())
    {
        return;
    }
    Now = FPlatformTime::Seconds();
    if (StartTime == 0 && !Begin())
    {
        return;
    }
    if (LastFrameTime > 0)
    {
        FrameMilliseconds.Add((Now - LastFrameTime) * 1000);
    }
    if (Now - StartTime >= 300 || (Phase == ECityStreamingPhase::WaitReady && Now - PhaseStart > 30)
        || (Phase == ECityStreamingPhase::Settle && Now - PhaseStart > 12)
        || (Phase == ECityStreamingPhase::Capture && Now - PhaseStart > 8))
    {
        Finish(false, TEXT("Wall clock, readiness, endpoint streaming or screenshot timeout"));
        return;
    }
    if (Phase == ECityStreamingPhase::WaitReady)
    {
        Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
        Prepare();
        return;
    }
    LastFrameTime = Now;
    const auto* State = GetState();
    if (!Controller.IsValid() || Controller.Get() != GetWorld()->GetFirstPlayerController()
        || !GetHero() || !State || !State->GetProgress() || !State->IsUsingQASlot()
        || !Controller->CanCaptureProgress() || Controller->GetDrivenVehicle()
        || !GetHero()->GetActorEnableCollision() || GetHero()->Health <= 0
        || State->GetMissionStage() != ECityMissionStage::NotStarted)
    {
        Finish(false, TEXT("On-foot control, isolated state, collision or untouched mission was lost"));
        return;
    }
    if (!CheckMovement(DeltaTime))
    {
        return;
    }
    if (Phase == ECityStreamingPhase::Route)
    {
        RunRoute();
    }
    else
    {
        RunCapture();
    }
}

void UCityStreamingJourney::Prepare()
{
    auto* Hero = GetHero();
    if (!GetWorld()->HasBegunPlay() || !Hero || !Controller->CanCaptureProgress()
        || Now - PhaseStart < 2 || !Hero->GetCharacterMovement()->IsMovingOnGround())
    {
        return;
    }
    const auto* State = GetState();
    const auto* Save = State ? State->GetProgress() : nullptr;
    if (!Save || !State->IsUsingQASlot() || State->GetSaveSlotName() != TEXT("ANANTA_City_QA")
        || Save->bHasPlayerTransform || Save->Mission.Stage != ECityMissionStage::NotStarted
        || !Save->Mission.Clues.IsEmpty() || !Save->Mission.DefeatedEnemies.IsEmpty()
        || Save->Mission.bFragmentCollected || Save->Mission.RewardCount != 0
        || !Save->Services.VisitedIds.IsEmpty() || !Save->Services.ClaimedSupplyIds.IsEmpty()
        || Save->Services.SuppliesCount != 0 || !Save->LegacyFragments.IsEmpty()
        || FVector::Dist2D(Hero->GetActorLocation(), FVector(-25000, 1500, 120)) > 60)
    {
        Finish(false, TEXT("Requires a fresh isolated QA slot at the authored cafe spawn"));
        return;
    }
    if (!GetWorld()->GetWorldPartition() || !Hero->TraversalComponent)
    {
        Finish(false, TEXT("Missing World Partition or ordinary traversal component"));
        return;
    }
    InitialLocation = Hero->GetActorLocation();
    LastLocation = InitialLocation;
    LastFrameTime = Now;
    SprintSpeed = Hero->TraversalComponent->SprintSpeed;
    WalkSpeed = Hero->TraversalComponent->WalkSpeed;
    // Theo via he quan cafe, truc x=-24000 va duong y=72000 trong CityExpansionLayout.py.
    Waypoints = {
        FVector(-25100, 1500, 0), FVector(-25100, 1100, 0), FVector(-22900, 1100, 0),
        FVector(-22900, 73100, 0), FVector(73100, 73100, 0)
    };
    FVector Previous = InitialLocation;
    for (const FVector& Point : Waypoints)
    {
        PlannedDistance += FVector::Dist2D(Previous, Point);
        Previous = Point;
    }
    if (SprintSpeed <= 0 || WalkSpeed <= 0 || PlannedDistance / SprintSpeed > 300 - (Now - StartTime))
    {
        Finish(false, TEXT("Ordinary configured speed cannot complete the route within the remaining budget"));
        return;
    }
    NextPhase(ECityStreamingPhase::Route, TEXT("Fresh start verified; beginning ordinary held-key route"));
}

void UCityStreamingJourney::SetKey(const FKey& Key, const bool bDown)
{
    if (!Controller.IsValid() || HeldKeys.Contains(Key) == bDown)
    {
        return;
    }
    const FInputKeyEventArgs Event(nullptr, INPUTDEVICEID_NONE, Key,
        bDown ? IE_Pressed : IE_Released, bDown ? 1.f : 0.f, false, FPlatformTime::Cycles64());
    Controller->InputKey(Event);
    InputEvents.Add(FString::Printf(TEXT("time=%.3f key=%s event=%s"), Now - StartTime,
        *Key.ToString(), bDown ? TEXT("Pressed") : TEXT("Released")));
    if (bDown)
    {
        HeldKeys.Add(Key);
    }
    else
    {
        HeldKeys.Remove(Key);
    }
}

void UCityStreamingJourney::ReleaseKeys()
{
    for (const FKey& Key : HeldKeys.Array())
    {
        SetKey(Key, false);
    }
    HeldKeys.Empty();
}

void UCityStreamingJourney::Deinitialize()
{
    Now = FPlatformTime::Seconds();
    ReleaseKeys();
    if (!bFinished && StartTime > 0)
    {
        Finish(false, TEXT("World ended before journey completion"));
        FPlatformMisc::RequestExitWithStatus(false, 1);
    }
    Super::Deinitialize();
}
