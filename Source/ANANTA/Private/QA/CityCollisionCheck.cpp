#include "QA/CityCollisionCheck.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace
{
    // Toa do cua CityRooms: di qua cua theo ca hai huong, bang CharacterMovement that.
    const FVector Starts[] = {
        FVector(-25080, 2400, 110), FVector(-25600, 2400, 110),
        FVector(1000, 2500, 110), FVector(1600, 2500, 110)
    };
    const FVector Ends[] = {
        FVector(-25600, 2400, 110), FVector(-25080, 2400, 110),
        FVector(1600, 2500, 110), FVector(1000, 2500, 110)
    };
}

bool UCityCollisionCheck::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld()
        && FParse::Param(FCommandLine::Get(), TEXT("CityCollisionCheck"))
        && FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
#endif
}

TStatId UCityCollisionCheck::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityCollisionCheck, STATGROUP_Tickables);
}

void UCityCollisionCheck::Finish(const bool bSuccess, const TCHAR* Reason)
{
    bFinished = true;
    UE_LOG(LogTemp, Display, TEXT("CITY_COLLISION_CHECK_FINISH success=%d legs=%d reason=%s"),
        bSuccess, Leg, Reason);
    FPlatformMisc::RequestExitWithStatus(false, bSuccess ? 0 : 1);
}

void UCityCollisionCheck::Tick(const float DeltaTime)
{
    if (bFinished || !GetWorld()->HasBegunPlay())
    {
        return;
    }
    const double Now = FPlatformTime::Seconds();
    if (StartedAt == 0)
    {
        StartedAt = Now;
    }
    if (Now - StartedAt > 90)
    {
        Finish(false, TEXT("Timeout waiting for player or streamed doorway"));
        return;
    }
    auto* PC = Cast<AANANTACityController>(GetWorld()->GetFirstPlayerController());
    auto* Hero = PC ? Cast<AANANTACityCharacter>(PC->GetPawn()) : nullptr;
    if (!Hero || !PC->CanCaptureProgress())
    {
        return;
    }
    auto* Movement = Hero->GetCharacterMovement();
    if (!bPlaced)
    {
        Movement->StopMovementImmediately();
        Movement->DisableMovement();
        Hero->SetActorLocation(Starts[Leg]);
        LegStartedAt = Now;
        bPlaced = true;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityCollisionCheck), false, Hero);
    const auto* Capsule = Hero->GetCapsuleComponent();
    const float HalfHeight = Capsule->GetScaledCapsuleHalfHeight();
    const FCollisionShape Shape = FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(), HalfHeight);
    if (!bWalking)
    {
        FHitResult Floor;
        FVector Start = Starts[Leg];
        if (Now - LegStartedAt < 2 || !GetWorld()->LineTraceSingleByChannel(Floor,
            Start + FVector(0, 0, 150), Start - FVector(0, 0, 300), ECC_Pawn, Params)
            || !Movement->IsWalkable(Floor))
        {
            return;
        }
        Start.Z = Floor.ImpactPoint.Z + HalfHeight + 3;
        if (GetWorld()->OverlapBlockingTestByChannel(Start, FQuat::Identity, ECC_Pawn, Shape, Params))
        {
            Finish(false, TEXT("Doorway approach capsule overlaps blocking geometry"));
            return;
        }
        Hero->SetActorLocation(Start);
        Movement->SetMovementMode(MOVE_Walking);
        LegStartedAt = Now;
        bWalking = true;
    }
    const FVector Location = Hero->GetActorLocation();
    if (Now - LegStartedAt > 15 || Location.Z < 70 || Location.Z > 180)
    {
        UE_LOG(LogTemp, Error, TEXT("CITY_COLLISION_BLOCKED leg=%d position=%s velocity=%s"),
            Leg, *Location.ToString(), *Movement->Velocity.ToString());
        Finish(false, TEXT("Doorway walk stuck or lost ground"));
        return;
    }
    if (FVector::DistSquared2D(Location, Ends[Leg]) < FMath::Square(35.f)
        && Movement->IsMovingOnGround())
    {
        UE_LOG(LogTemp, Display, TEXT("CITY_COLLISION_LEG_PASS leg=%d position=%s"), Leg, *Location.ToString());
        Movement->StopMovementImmediately();
        ++Leg;
        bPlaced = false;
        bWalking = false;
        if (Leg == UE_ARRAY_COUNT(Starts))
        {
            Finish(true, TEXT("Cafe and apartment doorways traversed both directions"));
        }
        return;
    }
    Hero->AddMovementInput((Ends[Leg] - Location).GetSafeNormal2D(), 1);
}
