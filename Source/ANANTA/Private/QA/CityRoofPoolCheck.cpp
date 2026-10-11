#include "QA/CityRoofPoolCheck.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityRoofPoolCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && World->GetMapName() == TEXT("ANANTA_City")
        && FParse::Param(FCommandLine::Get(), TEXT("CityRoofPoolCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityRoofPoolCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityRoofPoolCheck, STATGROUP_Tickables);
}

AANANTACityCharacter* UCityRoofPoolCheck::Hero() const
{
    return Controller.IsValid() ? Cast<AANANTACityCharacter>(Controller->GetPawn()) : nullptr;
}

UANANTACitySubsystem* UCityRoofPoolCheck::State() const
{
    const auto* Instance = GetWorld()->GetGameInstance();
    return Instance ? Instance->GetSubsystem<UANANTACitySubsystem>() : nullptr;
}

void UCityRoofPoolCheck::Tick(const float DeltaTime)
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
        PhaseAt = Now;
    }
    PhaseSeconds += DeltaTime;
    if (Now - StartedAt > 150 || (Phase != ECityRoofPoolPhase::WaitReady && Now - PhaseAt > 45))
    {
        Finish(false, TEXT("Readiness or movement phase timed out"));
        return;
    }
    if (Phase == ECityRoofPoolPhase::WaitReady)
    {
        Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
        if (!GetWorld()->HasBegunPlay() || !Hero() || !Controller->CanCaptureProgress())
        {
            return;
        }
        bQASlot = State() && State()->IsUsingQASlot();
        if (!bQASlot)
        {
            Finish(false, TEXT("Requires isolated QA save slot"));
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
        if (Now - StableAt >= 2)
        {
            bStreamed = true;
            if (PrepareHero())
            {
                Advance(ECityRoofPoolPhase::Settle, TEXT("QA slot, restore and rooftop region streaming ready"));
            }
        }
        return;
    }
    if (!Hero() || !Controller->CanCaptureProgress() || Controller->GetDrivenVehicle()
        || !State() || !State()->IsUsingQASlot() || !StreamingSource.IsValid()
        || !StreamingSource->IsStreamingCompleted())
    {
        Finish(false, TEXT("Lost on-foot character, isolated QA state or streaming coverage"));
        return;
    }
    if (Phase == ECityRoofPoolPhase::Settle)
    {
        if (PhaseSeconds > 5)
        {
            Finish(false, TEXT("Setup capsule did not settle on authored courtyard"));
        }
        else if (PhaseSeconds >= 0.5 && Hero()->GetCharacterMovement()->IsMovingOnGround())
        {
            if (ObserveBody(DeltaTime) && FMath::Abs(FloorZ - 20) <= 3)
            {
                Advance(ECityRoofPoolPhase::Ascent, TEXT("Normal capsule grounded on courtyard at Z=20"));
            }
        }
        return;
    }
    if (ObserveBody(DeltaTime))
    {
        RunPhase();
    }
}

void UCityRoofPoolCheck::Advance(const ECityRoofPoolPhase Next, const FString& Reason)
{
    auto& Result = Results.AddDefaulted_GetRef();
    Result.Phase = PhaseName();
    Result.Reason = Reason;
    Result.bPassed = true;
    Result.ElapsedSeconds = FPlatformTime::Seconds() - PhaseAt;
    SetForward(false);
    Phase = Next;
    PhaseAt = FPlatformTime::Seconds();
    PhaseSeconds = 0;
    ProgressAt = PhaseAt;
    Previous = Hero()->GetActorLocation();
    ProgressOrigin = Previous;
    if (Next == ECityRoofPoolPhase::Ascent)
    {
        Ascent.Start = Previous;
        Ascent.End = Previous;
    }
    if (Next == ECityRoofPoolPhase::Descent)
    {
        Descent.Start = Previous;
        Descent.End = Previous;
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_ROOFPOOL_PHASE %s position=%s"), PhaseName(), *Previous.ToString());
}

void UCityRoofPoolCheck::Deinitialize()
{
    if (!bFinished && StartedAt > 0)
    {
        Finish(false, TEXT("World ended before rooftop walking checks completed"));
    }
    SetForward(false);
    if (Observer.IsValid())
    {
        Observer->Destroy();
    }
    Super::Deinitialize();
}
