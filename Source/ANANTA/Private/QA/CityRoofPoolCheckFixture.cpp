#include "QA/CityRoofPoolCheck.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "Components/CapsuleComponent.h"
#include "Components/SceneComponent.h"
#include "Components/TraversalComponent.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputCoreTypes.h"

bool UCityRoofPoolCheck::PrepareStreaming()
{
    if (!GetWorld()->GetWorldPartition())
    {
        Finish(false, TEXT("Requires authored ANANTA_City World Partition map"));
        return false;
    }
    auto* Anchor = GetWorld()->SpawnActor<AActor>();
    if (!Anchor)
    {
        Finish(false, TEXT("Cannot create rooftop streaming observer"));
        return false;
    }
    Observer = Anchor;
    Anchor->Tags.Add(TEXT("QA_AuthoredRoofPoolInput"));
    auto* Root = NewObject<USceneComponent>(Anchor);
    Anchor->SetRootComponent(Root);
    Anchor->AddInstanceComponent(Root);
    Root->RegisterComponent();
    Anchor->SetActorLocation(FVector(102000, 198000, 840));
    auto* Source = NewObject<UWorldPartitionStreamingSourceComponent>(Anchor);
    Anchor->AddInstanceComponent(Source);
    FStreamingSourceShape Shape;
    Shape.bUseGridLoadingRange = false;
    Shape.Radius = 30000;
    Source->Shapes.Add(Shape);
    Source->TargetState = EStreamingSourceTargetState::Activated;
    Source->EnableStreamingSource();
    Source->RegisterComponent();
    StreamingSource = Source;
    return true;
}

bool UCityRoofPoolCheck::PrepareHero()
{
    const auto* Movement = Hero()->GetCharacterMovement();
    OriginalStepHeight = Movement->MaxStepHeight;
    OriginalGravityScale = Movement->GravityScale;
    bSettingsUnchanged = CheckBodySettings();
    if (!bSettingsUnchanged || Controller->GetDrivenVehicle())
    {
        Finish(false, TEXT("Requires normal on-foot character with unchanged 38/92 capsule and walk speed"));
        return false;
    }
    // Chi teleport luc setup; moi doan len/xuong sau do deu dung W qua controller.
    if (!Hero()->TeleportTo(FVector(98350, 195600, 115), FRotator(0, 90, 0)))
    {
        Finish(false, TEXT("Normal capsule cannot occupy courtyard setup location"));
        return false;
    }
    Hero()->GetCharacterMovement()->StopMovementImmediately();
    Controller->SetControlRotation(FRotator(-12, 90, 0));
    Previous = Hero()->GetActorLocation();
    return true;
}

bool UCityRoofPoolCheck::CheckBodySettings() const
{
    const auto* Pawn = Hero();
    if (!Pawn)
    {
        return false;
    }
    const auto* Capsule = Pawn->GetCapsuleComponent();
    const auto* Movement = Pawn->GetCharacterMovement();
    const auto* Traversal = Pawn->TraversalComponent.Get();
    return Pawn->GetActorEnableCollision() && !Pawn->IsHidden() && !Pawn->GetAttachParentActor()
        && Capsule->GetCollisionEnabled() == ECollisionEnabled::QueryAndPhysics
        && Capsule->GetCollisionResponseToChannel(ECC_WorldStatic) == ECR_Block
        && FMath::IsNearlyEqual(Capsule->GetScaledCapsuleRadius(), 38.f, 0.01f)
        && FMath::IsNearlyEqual(Capsule->GetScaledCapsuleHalfHeight(), 92.f, 0.01f)
        && FMath::IsNearlyEqual(Pawn->CustomTimeDilation, 1.f)
        && Movement->IsActive() && Movement->IsComponentTickEnabled()
        && FMath::IsNearlyEqual(Movement->MaxWalkSpeed, 350.f, 0.01f)
        && FMath::IsNearlyEqual(Movement->MaxStepHeight, OriginalStepHeight, 0.01f)
        && FMath::IsNearlyEqual(Movement->GravityScale, OriginalGravityScale, 0.01f)
        && Traversal && FMath::IsNearlyEqual(Traversal->WalkSpeed, 350.f)
        && FMath::IsNearlyEqual(Traversal->SprintSpeed, 650.f);
}

bool UCityRoofPoolCheck::ObserveBody(const float DeltaTime)
{
    bSettingsUnchanged &= CheckBodySettings();
    const auto* Pawn = Hero();
    const auto* Movement = Pawn->GetCharacterMovement();
    const FVector Position = Pawn->GetActorLocation();
    if (!bSettingsUnchanged || Position.ContainsNaN() || !Movement->IsMovingOnGround()
        || !Movement->CurrentFloor.IsWalkableFloor() || Movement->CurrentFloor.HitResult.bStartPenetrating)
    {
        Finish(false, TEXT("Changed body settings, unsupported character or penetrating movement floor"));
        return false;
    }
    if (Phase != ECityRoofPoolPhase::Settle
        && FVector::Dist(Position, Previous) > FMath::Max(50.f, DeltaTime * 400.f + 30.f))
    {
        Finish(false, TEXT("Discontinuous measured movement suggests teleport or recovery"));
        return false;
    }
    const auto* Capsule = Pawn->GetCapsuleComponent();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRoofPoolBody), false, Pawn);
    const FCollisionResponseParams Responses(Capsule->GetCollisionResponseToChannels());
    if (GetWorld()->OverlapBlockingTestByChannel(Position, FQuat::Identity, ECC_Pawn,
        FCollisionShape::MakeCapsule(38.f, 92.f), Params, Responses))
    {
        Finish(false, TEXT("Full normal capsule overlaps blocking geometry"));
        return false;
    }
    ++ClearanceSamples;
    FHitResult Floor;
    const bool bFloorHit = GetWorld()->LineTraceSingleByObjectType(Floor, Position,
        Position - FVector(0, 0, 150), FCollisionObjectQueryParams(ECC_WorldStatic), Params);
    if (!bFloorHit || Floor.bStartPenetrating || Floor.ImpactNormal.Z < 0.8)
    {
        Finish(false, TEXT("No authored static walkable surface beneath normal capsule"));
        return false;
    }
    FloorZ = Floor.ImpactPoint.Z;
    FloorActor = GetNameSafe(Floor.GetActor());
    const double FeetZ = Position.Z - 92;
    if (FloorZ < 17 || FloorZ > 843 || FeetZ < FloorZ - 3 || FeetZ > FloorZ + OriginalStepHeight + 5)
    {
        Finish(false, TEXT("Feet or supporting floor left the courtyard/stair/roof height envelope"));
        return false;
    }
    ++FloorSamples;
    const bool bW = Controller->IsInputKeyDown(EKeys::W);
    if (Phase == ECityRoofPoolPhase::Ascent || Phase == ECityRoofPoolPhase::Descent)
    {
        if (FMath::Abs(Position.X - 98350) > 180)
        {
            Finish(false, TEXT("Measured stair leg left the 500 cm stair corridor"));
            return false;
        }
        auto& Leg = Phase == ECityRoofPoolPhase::Ascent ? Ascent : Descent;
        Leg.TravelCm += FVector::Dist2D(Previous, Position);
        Leg.End = Position;
        ++Leg.Samples;
        Leg.InputSamples += bW ? 1 : 0;
        const int32 Step = FMath::RoundToInt((FloorZ - 40) / 20);
        if (Step >= 0 && Step < 41 && FMath::Abs(FloorZ - (40 + Step * 20)) <= 2
            && FMath::Abs(Position.Y - (195800 + Step * 100)) <= 52)
        {
            Leg.Steps.Add(Step);
        }
    }
    LandingInputSamples += Phase == ECityRoofPoolPhase::Landing && bW ? 1 : 0;
    ReturnInputSamples += Phase == ECityRoofPoolPhase::ReturnLanding && bW ? 1 : 0;
    Previous = Position;
    return true;
}
