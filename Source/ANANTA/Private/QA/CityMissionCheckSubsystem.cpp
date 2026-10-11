#include "QA/CityMissionCheckSubsystem.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityMissionCheckSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld()
        && (FParse::Param(FCommandLine::Get(), TEXT("CityMissionCheck"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityMissionReload")));
#endif
}

TStatId UCityMissionCheckSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityMissionCheckSubsystem, STATGROUP_Tickables);
}

AANANTACityCharacter* UCityMissionCheckSubsystem::GetHero() const
{
    return Controller.IsValid() ? Cast<AANANTACityCharacter>(Controller->GetPawn()) : nullptr;
}

UANANTACitySubsystem* UCityMissionCheckSubsystem::GetState() const
{
    return GetWorld() && GetWorld()->GetGameInstance()
        ? GetWorld()->GetGameInstance()->GetSubsystem<UANANTACitySubsystem>() : nullptr;
}

void UCityMissionCheckSubsystem::Tick(float DeltaTime)
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
        bReload = FParse::Param(FCommandLine::Get(), TEXT("CityMissionReload"));
        const bool bCheck = FParse::Param(FCommandLine::Get(), TEXT("CityMissionCheck"));
        if (bReload == bCheck || !FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"))
            || !GetWorld()->GetMapName().Contains(TEXT("ANANTA_City"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityCapture"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityInputSmoke")))
        {
            Finish(false, TEXT("Require city map, QA slot, one mission mode and no other input/capture harness"));
            return;
        }
        if (bReload && !ReadCheckpoint())
        {
            Finish(false, TEXT("Reload requires a completed checkpoint from a different process"));
            return;
        }
        if (!bReload)
        {
            IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
            if (!IFileManager::Get().Delete(*(EvidenceDirectory() / TEXT("Checkpoint.txt")), false))
            {
                Finish(false, TEXT("Could not invalidate the previous QA completion checkpoint"));
                return;
            }
        }
        Observe(true, TEXT("Started bounded engine input mission acceptance"));
        if (!WriteReport(false, false))
        {
            Finish(false, TEXT("Cannot write initial phase evidence"));
            return;
        }
    }
    PhaseElapsed = static_cast<float>(Now - PhaseStartTime);
    if (Now - StartTime > 900 || PhaseElapsed > PhaseTimeout())
    {
        Finish(false, TEXT("Bounded phase/run timeout; no traversal or gameplay bypass attempted"));
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
    if (Phase == ECityMissionCheckPhase::WaitReady)
    {
        Prepare();
        return;
    }
    if (!GetHero() || !GetState() || !Car.IsValid() || !Controller->CanCaptureProgress()
        || Controller->GetDrivenVehicle() || GetHero()->Health <= 0)
    {
        Finish(false, TEXT("Required runtime state lost, recovery occurred, or unexpected vehicle entered"));
        return;
    }
    const FVector Location = GetHero()->GetActorLocation();
    if (Location.Z < -200 || FVector::Dist2D(Location, LastLocation) > FMath::Max(250.f, DeltaTime * 1000))
    {
        Finish(false, TEXT("Unexpected displacement or fall; traversal is not accepted"));
        return;
    }
    LastLocation = Location;
    RunPhase();
}

void UCityMissionCheckSubsystem::Prepare()
{
    if (!GetWorld()->HasBegunPlay() || !GetHero() || !Controller->CanCaptureProgress() || PhaseElapsed < 2)
    {
        return;
    }
    const auto* State = GetState();
    if (!State || !State->IsUsingQASlot() || State->GetSaveSlotName() != TEXT("ANANTA_City_QA"))
    {
        Finish(false, TEXT("Save isolation was not established"));
        return;
    }
    int32 Cars = 0;
    for (TActorIterator<AANANTACityVehicle> It(GetWorld()); It; ++It)
    {
        if (It->VehicleId == TEXT("PlayerCar"))
        {
            Car = *It;
            ++Cars;
        }
    }
    if (Cars != 1 || !Car->IsRestoreComplete() || !IsSafelyGrounded())
    {
        return;
    }
    LastLocation = GetHero()->GetActorLocation();
    if (bReload)
    {
        if (!VerifyRestoredProgress())
        {
            Finish(false, TEXT("Completed state, IDs or restored transforms differ from completion checkpoint"));
            return;
        }
        Objective = 5;
        NextPhase(ECityMissionCheckPhase::Repeat, TEXT("New process restored complete QA state and both transforms"));
    }
    else if (State->GetMissionStage() == ECityMissionStage::NotStarted && State->GetMission().IsValid())
    {
        BeginRoute();
    }
    else
    {
        Finish(false, TEXT("Mission check did not start with fresh QA progress"));
    }
}

void UCityMissionCheckSubsystem::SetKey(const FKey& Key, const bool bDown)
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

void UCityMissionCheckSubsystem::TapKey(const FKey& Key)
{
    SetKey(Key, true);
    PulseReleaseTimes.Add(Key, Now + 0.15);
}

void UCityMissionCheckSubsystem::ReleaseKeys()
{
    for (const FKey& Key : HeldKeys.Array())
    {
        SetKey(Key, false);
    }
    HeldKeys.Empty();
    PulseReleaseTimes.Empty();
}

void UCityMissionCheckSubsystem::Deinitialize()
{
    ReleaseKeys();
    if (!bFinished && StartTime > 0)
    {
        Observe(false, TEXT("World ended before acceptance completed"));
        WriteReport(true, false);
        FPlatformMisc::RequestExitWithStatus(false, 1);
    }
    Super::Deinitialize();
}
