#include "QA/CityInputSmokeSubsystem.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACityInteractable.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/PlatformTime.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityInputSmokeSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && FParse::Param(FCommandLine::Get(), TEXT("CityInputSmoke"));
#endif
}

TStatId UCityInputSmokeSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityInputSmokeSubsystem, STATGROUP_Tickables);
}

AANANTACityCharacter* UCityInputSmokeSubsystem::GetHero() const
{
    return Controller.IsValid() ? Cast<AANANTACityCharacter>(Controller->GetPawn()) : nullptr;
}

UANANTACitySubsystem* UCityInputSmokeSubsystem::GetState() const
{
    return GetWorld() && GetWorld()->GetGameInstance()
        ? GetWorld()->GetGameInstance()->GetSubsystem<UANANTACitySubsystem>() : nullptr;
}

void UCityInputSmokeSubsystem::Tick(float DeltaTime)
{
    if (bFinished)
    {
        if (++ExitFrames == 3)
        {
            FPlatformMisc::RequestExitWithStatus(false, bPassed ? 0 : 1);
        }
        return;
    }
    if (!GetWorld() || !GetWorld()->HasBegunPlay())
    {
        return;
    }
    Now = FPlatformTime::Seconds();
    if (StartTime == 0)
    {
        StartTime = Now;
        PhaseStartTime = Now;
        if (!GetWorld()->GetMapName().Contains(TEXT("ANANTA_City"))
            || !FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityCapture")))
        {
            Finish(false, TEXT("Require city map and -CityQASlot; do not combine with -CityCapture"));
            return;
        }
    }
    PhaseElapsed = static_cast<float>(Now - PhaseStartTime);
    if (Now - StartTime > 120 || PhaseElapsed > PhaseTimeout())
    {
        Finish(false, TEXT("Bounded input sequence timed out; no recovery teleport or mission bypass used"));
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
    if (Phase == ECityInputSmokePhase::WaitReady)
    {
        Prepare();
        return;
    }
    if (!Controller.IsValid() || !GetHero() || !Giver.IsValid() || !Car.IsValid() || !GetState())
    {
        Finish(false, TEXT("Required controller, pawn, giver, vehicle or city state disappeared"));
        return;
    }
    RunPhase();
}

bool UCityInputSmokeSubsystem::Prepare()
{
    if (!Controller.IsValid() || !GetHero() || !Controller->CanCaptureProgress() || PhaseElapsed < 2)
    {
        return false;
    }
    auto* State = GetState();
    if (!State || !State->IsUsingQASlot() || State->GetMissionStage() != ECityMissionStage::NotStarted)
    {
        Finish(false, TEXT("Smoke requires isolated fresh QA mission state"));
        return false;
    }
    int32 GiverCount = 0;
    int32 CarCount = 0;
    for (TActorIterator<AANANTACityInteractable> It(GetWorld()); It; ++It)
    {
        if (It->InteractionId == TEXT("Giver_Cafe"))
        {
            Giver = *It;
            ++GiverCount;
        }
    }
    for (TActorIterator<AANANTACityVehicle> It(GetWorld()); It; ++It)
    {
        if (It->VehicleId == TEXT("PlayerCar"))
        {
            Car = *It;
            ++CarCount;
        }
    }
    if (GiverCount != 1 || CarCount != 1)
    {
        Finish(false, TEXT("Missing or duplicate Giver_Cafe / PlayerCar actors"));
        return false;
    }
    if (!Car->IsRestoreComplete())
    {
        return false;
    }
    if (!CheckCamera(false))
    {
        Finish(false, TEXT("Player camera attachment or observed camera separation is invalid"));
        return false;
    }
    InitialLocation = GetHero()->GetActorLocation();
    NextPhase(ECityInputSmokePhase::WalkToGiver, TEXT("Ready with unique actors and valid third person camera"));
    return true;
}

void UCityInputSmokeSubsystem::SetKey(const FKey& Key, const bool bDown)
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

void UCityInputSmokeSubsystem::TapKey(const FKey& Key)
{
    SetKey(Key, true);
    PulseReleaseTimes.Add(Key, Now + 0.15);
}

void UCityInputSmokeSubsystem::ReleaseKeys()
{
    const TArray<FKey> Keys = HeldKeys.Array();
    for (const FKey& Key : Keys)
    {
        SetKey(Key, false);
    }
    HeldKeys.Empty();
    PulseReleaseTimes.Empty();
}

void UCityInputSmokeSubsystem::Deinitialize()
{
    ReleaseKeys();
    if (!bFinished && StartTime > 0)
    {
        Observe(false, TEXT("World ended before the input sequence completed"));
        WriteReport(true, false);
    }
    Super::Deinitialize();
}
