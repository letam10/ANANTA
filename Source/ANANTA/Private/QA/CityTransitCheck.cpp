#include "QA/CityTransitCheck.h"

#include "City/ANANTACityController.h"
#include "City/ANANTACityCharacter.h"
#include "City/ANANTACitySubsystem.h"
#include "City/Mobility/CityRouteVehicle.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/FileManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"

bool UCityTransitCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const auto* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld() && FParse::Param(FCommandLine::Get(), TEXT("CityTransitCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityTransitCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityTransitCheck, STATGROUP_Tickables);
}

void UCityTransitCheck::SetWalking(const bool bWalk)
{
    if (!Controller.IsValid() || bWalking == bWalk)
    {
        return;
    }
    bWalking = bWalk;
    for (const FKey& Key : {EKeys::W, EKeys::LeftShift})
    {
        Controller->InputKey(FInputKeyEventArgs(nullptr, FInputDeviceId::CreateFromInternalId(0),
            Key, bWalk ? IE_Pressed : IE_Released, bWalk ? 1.f : 0.f, false, FPlatformTime::Cycles64()));
    }
}

void UCityTransitCheck::Tick(const float DeltaTime)
{
    if (bDone)
    {
        if (++ExitFrames == 3)
        {
            FPlatformMisc::RequestExitWithStatus(false, bPass ? 0 : 1);
        }
        return;
    }
    const double Now = FPlatformTime::Seconds();
    if (Start == 0)
    {
        Start = Now;
    }
    if (Now - Start > 180)
    {
        Finish(false, TEXT("Ordinary transit observation timed out"));
        return;
    }
    Controller = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    auto* Hero = Controller.IsValid() ? Cast<AANANTACityCharacter>(Controller->GetPawn()) : nullptr;
    if (!Hero || !Controller->CanCaptureProgress())
    {
        return;
    }
    if (Hero->GetActorLocation().Z < -100 || !Hero->GetActorEnableCollision())
    {
        Finish(false, TEXT("Player lost supported collision during observation"));
        return;
    }
    if (Hero->GetCharacterMovement()->IsMovingOnGround())
    {
        ++GroundChecks;
    }
    if (!Vehicle.IsValid())
    {
        for (TActorIterator<ACityRouteVehicle> It(GetWorld()); It; ++It)
        {
            if (It->GetKind() == ECityTransportKind::Coach)
            {
                Vehicle = *It;
                FirstVehiclePosition = It->GetActorLocation();
                break;
            }
        }
        return;
    }
    // Theo tuyen bang input W/Shift that, khong teleport hay tang toc nhan vat/xe.
    FVector Target = Vehicle->GetActorLocation() + Vehicle->GetActorRightVector() * 800
        - Vehicle->GetActorForwardVector() * 1400;
    Target.Z = Hero->GetActorLocation().Z;
    const FVector Direction = Target - Hero->GetActorLocation();
    Controller->SetControlRotation(Direction.Rotation());
    SetWalking(Direction.SizeSquared2D() > 1800 * 1800);
    if (Vehicle->GetBoardingCount() > 0 && Vehicle->GetAlightingCount() > 0
        && FVector::Dist2D(FirstVehiclePosition, Vehicle->GetActorLocation()) > 3000 && GroundChecks > 100)
    {
        Finish(true, TEXT("Authored coach route travelled with visible NPC boarding and alighting phases"));
    }
}

void UCityTransitCheck::Finish(const bool bSuccess, const FString& Detail)
{
    SetWalking(false);
    bDone = true;
    bPass = bSuccess;
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityTransitCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    FString Report = FString::Printf(TEXT("passed=%d\nreason=%s\ngroundChecks=%d\nboarded=%d\nalighted=%d\n"),
        bSuccess, *Detail, GroundChecks, Vehicle.IsValid() ? Vehicle->GetBoardingCount() : 0,
        Vehicle.IsValid() ? Vehicle->GetAlightingCount() : 0);
    if (Vehicle.IsValid())
    {
        Report += FString::Printf(TEXT("vehicle=%s\nstopped=%d\nblocked=%s\n"),
            *Vehicle->GetActorLocation().ToString(), Vehicle->IsStopped(), *Vehicle->GetBlockedReason());
    }
    FFileHelper::SaveStringToFile(Report, *(Directory / TEXT("Report.txt")));
    UE_LOG(LogTemp, Display, TEXT("CITY_TRANSIT_CHECK_FINISH success=%d reason=%s"), bSuccess, *Detail);
}

void UCityTransitCheck::Deinitialize()
{
    SetWalking(false);
    Super::Deinitialize();
}
