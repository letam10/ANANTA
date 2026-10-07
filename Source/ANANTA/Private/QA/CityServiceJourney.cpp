#include "QA/CityServiceJourney.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityServiceJourney::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"))
        && (FParse::Param(FCommandLine::Get(), TEXT("CityServiceCheck"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityServiceReload")));
#endif
}

TStatId UCityServiceJourney::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityServiceJourney, STATGROUP_Tickables);
}

AANANTACityCharacter* UCityServiceJourney::GetHero() const
{
    return Controller.IsValid() ? Cast<AANANTACityCharacter>(Controller->GetPawn()) : nullptr;
}

UANANTACitySubsystem* UCityServiceJourney::GetState() const
{
    return GetWorld() && GetWorld()->GetGameInstance()
        ? GetWorld()->GetGameInstance()->GetSubsystem<UANANTACitySubsystem>() : nullptr;
}

void UCityServiceJourney::Tick(float DeltaTime)
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
    if (StartTime == 0)
    {
        StartTime = Now;
        PhaseStartTime = Now;
        bReload = FParse::Param(FCommandLine::Get(), TEXT("CityServiceReload"));
        const bool bCheck = FParse::Param(FCommandLine::Get(), TEXT("CityServiceCheck"));
        if (bCheck == bReload || !GetWorld()->GetMapName().Contains(TEXT("ANANTA_City"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityCapture"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityInputSmoke"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityMissionCheck"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityMissionReload"))
            || FParse::Param(FCommandLine::Get(), TEXT("benchmark")))
        {
            Finish(false, TEXT("Require one service mode, city map, and no concurrent QA or benchmark mode"));
            return;
        }
        IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
        if (bReload ? !ReadCheckpoint()
            : !IFileManager::Get().Delete(*(EvidenceDirectory() / TEXT("Checkpoint.txt")), false))
        {
            Finish(false, TEXT("Could not validate reload checkpoint or invalidate previous check checkpoint"));
            return;
        }
        Observe(true, TEXT("Bounded ordinary service journey started"));
        if (!WriteReport(false, false))
        {
            Finish(false, TEXT("Cannot write initial evidence"));
            return;
        }
    }
    PhaseElapsed = Now - PhaseStartTime;
    const double Limit = Phase == ECityServiceJourneyPhase::Route ? 110
        : Phase == ECityServiceJourneyPhase::WaitReady ? 60 : 15;
    if (Now - StartTime > 360 || PhaseElapsed > Limit)
    {
        Finish(false, TEXT("Wall clock or phase timeout; no venue skipped or traversal bypass used"));
        return;
    }
    Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    for (auto It = PulseReleaseTimes.CreateIterator(); It; ++It)
    {
        if (Now >= It.Value())
        {
            SetKey(It.Key(), false);
            It.RemoveCurrent();
        }
    }
    if (Phase == ECityServiceJourneyPhase::WaitReady)
    {
        Prepare();
        return;
    }
    if (LastFrameTime > 0)
    {
        FrameMilliseconds.Add((Now - LastFrameTime) * 1000);
    }
    LastFrameTime = Now;
    if (!GetHero() || !GetState() || !Controller->CanCaptureProgress() || Controller->GetDrivenVehicle()
        || !GetHero()->GetActorEnableCollision() || GetHero()->Health <= 0
        || GetState()->GetMissionStage() != ECityMissionStage::NotStarted)
    {
        Finish(false, TEXT("Required runtime state, collision, on-foot control or untouched mission was lost"));
        return;
    }
    const FVector Location = GetHero()->GetActorLocation();
    if (Location.Z < -200 || FVector::Dist2D(Location, LastLocation) > FMath::Max(250.f, DeltaTime * 1000))
    {
        Finish(false, TEXT("Unexpected displacement or fall; recovery is not accepted"));
        return;
    }
    LastLocation = Location;
    RunPhase();
}

void UCityServiceJourney::Prepare()
{
    if (!GetWorld()->HasBegunPlay() || !GetHero() || !Controller->CanCaptureProgress() || PhaseElapsed < 2
        || !GetHero()->GetCharacterMovement()->IsMovingOnGround())
    {
        return;
    }
    const auto* State = GetState();
    if (!State || !State->IsUsingQASlot() || State->GetSaveSlotName() != TEXT("ANANTA_City_QA")
        || !MatchesProgress(State->GetProgress(), bReload ? 8 : 0))
    {
        Finish(false, TEXT("QA slot isolation or initial service/mission state is incorrect"));
        return;
    }
    LastLocation = GetHero()->GetActorLocation();
    LastFrameTime = Now;
    if (bReload)
    {
        NextPhase(ECityServiceJourneyPhase::Reload, TEXT("Restored pawn ready; observing settled reload"));
    }
    else
    {
        BeginRoute();
    }
}

void UCityServiceJourney::SetKey(const FKey& Key, const bool bDown)
{
    if (!Controller.IsValid() || HeldKeys.Contains(Key) == bDown)
    {
        return;
    }
    const FInputKeyEventArgs Event(nullptr, INPUTDEVICEID_NONE, Key,
        bDown ? IE_Pressed : IE_Released, bDown ? 1.f : 0.f, false, FPlatformTime::Cycles64());
    Controller->InputKey(Event);
    if (bDown)
    {
        HeldKeys.Add(Key);
    }
    else
    {
        HeldKeys.Remove(Key);
    }
}

void UCityServiceJourney::TapKey(const FKey& Key)
{
    SetKey(Key, true);
    PulseReleaseTimes.Add(Key, Now + 0.15);
}

void UCityServiceJourney::ReleaseKeys()
{
    for (const FKey& Key : HeldKeys.Array())
    {
        SetKey(Key, false);
    }
    HeldKeys.Empty();
    PulseReleaseTimes.Empty();
}

void UCityServiceJourney::Deinitialize()
{
    ReleaseKeys();
    if (!bFinished && StartTime > 0)
    {
        Now = FPlatformTime::Seconds();
        Finish(false, TEXT("World ended before the service journey completed"));
        FPlatformMisc::RequestExitWithStatus(false, 1);
    }
    Super::Deinitialize();
}
