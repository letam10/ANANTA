#include "QA/CityRowboatCheck.h"

#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "City/Mobility/CityRowboat.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityRowboatCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && World->GetMapName() == TEXT("ANANTA_City")
        && FParse::Param(FCommandLine::Get(), TEXT("CityRowboatCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityRowboatCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityRowboatCheck, STATGROUP_Tickables);
}

ACharacter* UCityRowboatCheck::Hero() const
{
    return Controller.IsValid() ? Cast<ACharacter>(Controller->GetPawn()) : nullptr;
}

void UCityRowboatCheck::Tick(const float DeltaTime)
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
    if (Now - StartedAt > 90 || (Phase != ECityRowboatPhase::WaitReady && Now - PhaseAt > 15))
    {
        Finish(false, TEXT("Rowboat QA readiness or input phase timed out"));
        return;
    }
    if (Phase == ECityRowboatPhase::WaitReady)
    {
        Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
        if (!GetWorld()->HasBegunPlay() || !Controller.IsValid() || !Hero())
        {
            return;
        }
        const auto* Instance = GetWorld()->GetGameInstance();
        const auto* State = Instance ? Instance->GetSubsystem<UANANTACitySubsystem>() : nullptr;
        bQASlot = State && State->IsUsingQASlot();
        if (!bQASlot)
        {
            Finish(false, TEXT("Isolated QA save slot is unavailable"));
            return;
        }
        if (!Observer.IsValid() && !PrepareStreaming())
        {
            return;
        }
        if (!StreamingSource.IsValid() || !StreamingSource->IsStreamingCompleted()
            || !Controller->CanCaptureProgress())
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
                Advance(ECityRowboatPhase::Settle, TEXT("QA save, controller restore and dock streaming ready"));
            }
        }
        return;
    }
    const auto* Instance = GetWorld()->GetGameInstance();
    const auto* State = Instance ? Instance->GetSubsystem<UANANTACitySubsystem>() : nullptr;
    if (!Hero() || !Boat.IsValid() || !State || !State->IsUsingQASlot()
        || !StreamingSource.IsValid() || !StreamingSource->IsStreamingCompleted() || !CheckCapsule())
    {
        Finish(false, TEXT("Lost player, boat, QA slot, streaming coverage or original capsule dimensions"));
        return;
    }
    // Chi cong chuyen dong trong luot W/Space; teleport setup khong duoc tinh vao ket qua.
    if (Phase == ECityRowboatPhase::Row || Phase == ECityRowboatPhase::Brake)
    {
        const FVector Position = Boat->GetActorLocation();
        if (Position.ContainsNaN() || !Boat->GetActorEnableCollision() || !IsBoarded())
        {
            Finish(false, TEXT("Invalid boat movement, collision or occupied attachment during measurement"));
            return;
        }
        MeasuredTravelCm += FVector::Dist2D(PreviousBoatPosition, Position);
        RowDisplacementCm = FVector::Dist2D(RowOrigin, Position);
        PreviousBoatPosition = Position;
        PeakSpeedKmh = FMath::Max(PeakSpeedKmh, static_cast<double>(Boat->GetSpeedKmh()));
    }
    RunPhase();
}

void UCityRowboatCheck::Advance(const ECityRowboatPhase Next, const FString& Reason)
{
    FCityRowboatPhaseResult& Result = Results.AddDefaulted_GetRef();
    Result.Phase = PhaseName();
    Result.Status = TEXT("PASS");
    Result.Reason = Reason;
    Result.ElapsedSeconds = FPlatformTime::Seconds() - PhaseAt;
    ReleaseKeys();
    Phase = Next;
    PhaseAt = FPlatformTime::Seconds();
    PhaseSeconds = 0;
}

void UCityRowboatCheck::Deinitialize()
{
    if (!bFinished && StartedAt > 0)
    {
        Finish(false, TEXT("World ended before rowboat input verification completed"));
    }
    ReleaseKeys();
    if (Observer.IsValid())
    {
        Observer->Destroy();
    }
    Super::Deinitialize();
}
