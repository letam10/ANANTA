#include "QA/CityCivicCheck.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UCityCivicCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && World->GetMapName() == TEXT("ANANTA_City")
        && FParse::Param(FCommandLine::Get(), TEXT("CityCivicCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

void UCityCivicCheck::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // Moc, FLOOR_Z=15 va cua rong 480 cm tu CityCivicDistrict.py.
    Services = {
        {TEXT("Police_Read"), FVector(-60000, 6000, 15)},
        {TEXT("Fire_Read"), FVector(-48000, 6000, 15)},
        {TEXT("Bar_Read"), FVector(-36000, -6000, 15)},
        {TEXT("Arcade_Read"), FVector(-24000, -6000, 15)}
    };
    for (const auto& Entry : Services)
    {
        for (const TCHAR* Direction : {TEXT("inward"), TEXT("outward")})
        {
            auto& Leg = Legs.AddDefaulted_GetRef();
            Leg.Service = Entry.Id.ToString();
            Leg.Direction = Direction;
        }
    }
}

TStatId UCityCivicCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityCivicCheck, STATGROUP_Tickables);
}

AANANTACityCharacter* UCityCivicCheck::Hero() const
{
    return Controller.IsValid() ? Cast<AANANTACityCharacter>(Controller->GetPawn()) : nullptr;
}

UANANTACitySubsystem* UCityCivicCheck::State() const
{
    const auto* Instance = GetWorld()->GetGameInstance();
    return Instance ? Instance->GetSubsystem<UANANTACitySubsystem>() : nullptr;
}

void UCityCivicCheck::Tick(const float DeltaTime)
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
    Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    if ((ReadyAt == 0 && Now - StartedAt > 60) || (ReadyAt > 0 && Now - ReadyAt > 240))
    {
        Finish(false, TEXT("Readiness exceeded 60 seconds or civic checks exceeded 240 seconds"));
        return;
    }
    if (Phase == ECityCivicPhase::Streaming)
    {
        if (!GetWorld()->HasBegunPlay() || !Hero() || !Controller->CanCaptureProgress())
        {
            return;
        }
        if (Sources.IsEmpty() && !PrepareStreaming())
        {
            return;
        }
        if (!StreamingComplete())
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
        if (!State() || !State()->IsUsingQASlot() || !State()->GetProgress()
            || !State()->GetServices().VisitedIds.IsEmpty())
        {
            Finish(false, TEXT("Requires a fresh isolated QA service state"));
            return;
        }
        ReadyAt = Now;
        SetupSite(Now);
        return;
    }
    if (!Hero() || !Controller->CanCaptureProgress() || Controller->GetDrivenVehicle()
        || !StreamingComplete() || !State() || !State()->IsUsingQASlot())
    {
        Finish(false, TEXT("On-foot player, isolated state or pinned streaming coverage lost"));
        return;
    }
    if (Phase == ECityCivicPhase::Settle)
    {
        if (Now - PhaseAt > 8)
        {
            Finish(false, TEXT("Relocated exterior start did not settle on authored ground"));
        }
        else if (Now - PhaseAt > 1 && Hero()->GetCharacterMovement()->IsMovingOnGround())
        {
            if (ObserveBody(DeltaTime, false))
            {
                BeginLeg(true, Now);
            }
        }
        return;
    }
    if (!ObserveBody(DeltaTime, Phase != ECityCivicPhase::Interact))
    {
        return;
    }
    if (Phase == ECityCivicPhase::Interact)
    {
        Interact(Now);
    }
    else
    {
        MoveLeg(DeltaTime, Now);
    }
}

void UCityCivicCheck::Deinitialize()
{
    ReleaseKeys();
    if (!bFinished && StartedAt > 0 && GetWorld()->GetMapName() == TEXT("ANANTA_City"))
    {
        Finish(false, TEXT("City world ended before civic movement checks completed"));
    }
    for (const auto& Anchor : StreamingAnchors)
    {
        if (Anchor.IsValid())
        {
            Anchor->Destroy();
        }
    }
    // Bootstrap/teardown khong goi RequestExit; runner tu choi bao cao chua hoan thanh.
    Super::Deinitialize();
}
