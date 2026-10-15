#include "QA/CityCivicCheck.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "Components/CapsuleComponent.h"
#include "Components/TraversalComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"

bool UCityCivicCheck::ObserveBody(const float DeltaTime, const bool bMeasured)
{
    const auto* Pawn = Hero();
    const auto* Capsule = Pawn->GetCapsuleComponent();
    const auto* Movement = Pawn->GetCharacterMovement();
    const auto* Traversal = Pawn->TraversalComponent.Get();
    const FVector Position = Pawn->GetActorLocation();
    const FVector Anchor = Services[SiteIndex].Anchor;
    const double FeetZ = Position.Z - Capsule->GetScaledCapsuleHalfHeight();
    const bool bNormalSpeed = FMath::IsNearlyEqual(Movement->MaxWalkSpeed, 350.f)
        || FMath::IsNearlyEqual(Movement->MaxWalkSpeed, 650.f);
    if (Position.ContainsNaN() || !Pawn->GetActorEnableCollision()
        || Capsule->GetCollisionEnabled() != ECollisionEnabled::QueryAndPhysics
        || Capsule->GetCollisionResponseToChannel(ECC_WorldStatic) != ECR_Block
        || !FMath::IsNearlyEqual(Capsule->GetScaledCapsuleRadius(), 38.f)
        || !FMath::IsNearlyEqual(Capsule->GetScaledCapsuleHalfHeight(), 92.f)
        || !Traversal || !FMath::IsNearlyEqual(Traversal->WalkSpeed, 350.f)
        || !FMath::IsNearlyEqual(Traversal->SprintSpeed, 650.f) || !bNormalSpeed
        || !FMath::IsNearlyEqual(Pawn->CustomTimeDilation, 1.f))
    {
        Finish(false, TEXT("Normal capsule, collision or ordinary 350/650 cm/s speeds changed"));
        return false;
    }
    if (!Movement->IsMovingOnGround() || !Movement->CurrentFloor.IsWalkableFloor()
        || Movement->CurrentFloor.HitResult.bStartPenetrating
        || FeetZ < Anchor.Z - 5 || FeetZ > Anchor.Z + 10
        || FMath::Abs(Position.Y - Anchor.Y) > 190)
    {
        Finish(false, TEXT("Unsupported, penetrating floor or movement outside the clear entry corridor"));
        return false;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityCivicBody), false, Pawn);
    const auto Shape = FCollisionShape::MakeCapsule(37.f, 89.f);
    const FCollisionResponseParams Responses(Capsule->GetCollisionResponseToChannels());
    // Tru 1/3 cm chi cho phep do overlap, capsule vat ly van giu nguyen 38/92.
    if (GetWorld()->OverlapBlockingTestByChannel(Position, FQuat::Identity, ECC_Pawn,
        Shape, Params, Responses))
    {
        Finish(false, TEXT("Character body penetrated blocking authored geometry"));
        return false;
    }
    if (Phase != ECityCivicPhase::Settle
        && FVector::Dist(Position, Previous) > FMath::Max(40.f, DeltaTime * 650.f + 20.f))
    {
        Finish(false, TEXT("Discontinuous displacement; teleport/recovery is invalid during measured legs"));
        return false;
    }
    if (bMeasured)
    {
        auto& Leg = Legs[LegIndex];
        ++Leg.GroundChecks;
        ++Leg.CollisionChecks;
        if (Controller->IsInputKeyDown(EKeys::W))
        {
            ++Leg.InputChecks;
            if (Controller->IsInputKeyDown(EKeys::LeftShift))
            {
                ++Leg.SprintInputChecks;
            }
        }
        Leg.Travel += FVector::Dist2D(Position, Previous);
        Leg.End = Position;
    }
    Previous = Position;
    return true;
}

void UCityCivicCheck::BeginLeg(const bool bInward, const double Now)
{
    ReleaseKeys();
    Phase = bInward ? ECityCivicPhase::Inward : ECityCivicPhase::Outward;
    LegIndex = SiteIndex * 2 + (bInward ? 0 : 1);
    PhaseAt = Now;
    ProgressAt = Now;
    Previous = Hero()->GetActorLocation();
    ProgressOrigin = Previous;
    Legs[LegIndex].Start = Previous;
    Legs[LegIndex].End = Previous;
}

void UCityCivicCheck::MoveLeg(const float DeltaTime, const double Now)
{
    const bool bInward = Phase == ECityCivicPhase::Inward;
    auto& Leg = Legs[LegIndex];
    Leg.Elapsed = Now - PhaseAt;
    const FVector Position = Hero()->GetActorLocation();
    const FVector Anchor = Services[SiteIndex].Anchor;
    const FVector Target = Anchor + FVector(bInward ? 4480 : 1450, 0, 92);
    const FVector Direction(Target.X - Position.X, Target.Y - Position.Y, 0);
    const double Distance = Direction.Size();
    Leg.bCrossedDoor |= bInward ? Position.X > Anchor.X + 1900 : Position.X < Anchor.X + 1700;
    if (Distance <= 24)
    {
        ReleaseKeys();
        if (!Leg.bCrossedDoor || Leg.Travel < 2900 || Leg.GroundChecks < 10
            || Leg.InputChecks < 10 || Leg.SprintInputChecks < 10)
        {
            Finish(false, TEXT("Incomplete real input doorway traversal evidence"));
            return;
        }
        Leg.Status = TEXT("PASS");
        Leg.Reason = TEXT("W/Shift crossed authored doorway on ground with normal capsule and no penetration");
        if (bInward)
        {
            Phase = ECityCivicPhase::Interact;
            PhaseAt = Now;
            bESent = false;
        }
        else if (++SiteIndex == Services.Num())
        {
            Finish(true, TEXT("Four E interactions and eight actual inward/outward doorway legs completed"));
        }
        else
        {
            SetupSite(Now);
        }
        return;
    }
    Controller->SetControlRotation(FRotator(-12, Direction.Rotation().Yaw, 0));
    SetKey(EKeys::W, true);
    SetKey(EKeys::LeftShift, Distance > 500);
    if (FVector::Dist2D(Position, ProgressOrigin) > 30)
    {
        ProgressOrigin = Position;
        ProgressAt = Now;
    }
    if (Now - ProgressAt > 4 || Leg.Elapsed > 30)
    {
        Finish(false, TEXT("Doorway movement stuck for 4 seconds or leg exceeded 30 seconds"));
    }
}
