#include "QA/CityRowboatCheck.h"

#include "City/ANANTACityController.h"
#include "City/Mobility/CityRowboat.h"
#include "Components/CapsuleComponent.h"
#include "Components/SceneComponent.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"

bool UCityRowboatCheck::PrepareStreaming()
{
    if (!GetWorld()->GetWorldPartition())
    {
        Finish(false, TEXT("Requires authored ANANTA_City World Partition map"));
        return false;
    }
    auto* Anchor = GetWorld()->SpawnActor<AActor>();
    if (!Anchor)
    {
        Finish(false, TEXT("Cannot create dock streaming observer"));
        return false;
    }
    Observer = Anchor;
    Anchor->Tags.Add(TEXT("QA_AuthoredRowboatInput"));
    auto* Root = NewObject<USceneComponent>(Anchor);
    Anchor->SetRootComponent(Root);
    Anchor->AddInstanceComponent(Root);
    Root->RegisterComponent();
    Anchor->SetActorLocation(FVector(129240, -137000, 110));
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

bool UCityRowboatCheck::PrepareHero()
{
    int32 Count = 0;
    for (TActorIterator<ACityRowboat> It(GetWorld()); It; ++It)
    {
        if (It->VehicleId == TEXT("PlayerRowboat"))
        {
            Boat = *It;
            ++Count;
        }
    }
    if (Count != 1 || !Boat->IsRestoreComplete() || Boat->bOccupied
        || !Boat->GetActorLocation().Equals(FVector(129440, -137000, -120), 2)
        || !FMath::IsNearlyEqual(Boat->GetActorRotation().Yaw, 90.0, 0.1)
        || Controller->GetDrivenVehicle())
    {
        Finish(false, TEXT("Missing, duplicate, occupied or displaced authored PlayerRowboat"));
        return false;
    }
    CapsuleRadius = Hero()->GetCapsuleComponent()->GetScaledCapsuleRadius();
    CapsuleHalfHeight = Hero()->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    bCapsule = CheckCapsule();
    if (!bCapsule || !Hero()->GetActorEnableCollision()
        || !Hero()->GetCharacterMovement()->IsActive()
        || !Hero()->GetCharacterMovement()->IsComponentTickEnabled())
    {
        Finish(false, TEXT("Requires unchanged 38/92 capsule, collision and active character movement"));
        return false;
    }
    // Chi dat vi tri ban dau; de CharacterMovement tu ha nguoi xuong san ben that.
    if (!Hero()->TeleportTo(FVector(129240, -137000, 110), FRotator(0, 90, 0)))
    {
        Finish(false, TEXT("Normal hero capsule cannot occupy authored dock setup location"));
        return false;
    }
    Hero()->GetCharacterMovement()->StopMovementImmediately();
    Controller->SetControlRotation(FRotator(-12, 90, 0));
    UE_LOG(LogTemp, Display, TEXT("CITY_ROWBOAT_SETUP hero relocation only; capsule=38/92; boat authored"));
    return true;
}

bool UCityRowboatCheck::CheckCapsule() const
{
    const auto* Character = Hero();
    if (!Character)
    {
        return false;
    }
    const auto* Capsule = Character->GetCapsuleComponent();
    return FMath::IsNearlyEqual(CapsuleRadius, 38.f, 0.1f)
        && FMath::IsNearlyEqual(CapsuleHalfHeight, 92.f, 0.1f)
        && FMath::IsNearlyEqual(Capsule->GetScaledCapsuleRadius(), CapsuleRadius, 0.01f)
        && FMath::IsNearlyEqual(Capsule->GetScaledCapsuleHalfHeight(), CapsuleHalfHeight, 0.01f);
}

bool UCityRowboatCheck::CheckDryDock(bool& bClear, bool& bDry) const
{
    bClear = false;
    bDry = false;
    const auto* Character = Hero();
    if (!Character || !CheckCapsule() || Character->IsHidden() || !Character->GetActorEnableCollision()
        || Character->GetAttachParentActor() || !Character->GetCharacterMovement()->IsActive()
        || !Character->GetCharacterMovement()->IsComponentTickEnabled()
        || Character->GetCharacterMovement()->MovementMode != MOVE_Walking)
    {
        return false;
    }
    const FVector Position = Character->GetActorLocation();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRowboatQAExit), false, Character);
    bClear = !GetWorld()->OverlapBlockingTestByChannel(Position, FQuat::Identity, ECC_Pawn,
        FCollisionShape::MakeCapsule(CapsuleRadius, CapsuleHalfHeight), Params);
    FHitResult Floor;
    if (GetWorld()->LineTraceSingleByObjectType(Floor, Position,
        Position - FVector(0, 0, CapsuleHalfHeight + 15), FCollisionObjectQueryParams(ECC_WorldStatic), Params))
    {
        const FVector Point = Floor.ImpactPoint;
        bDry = Floor.ImpactNormal.Z >= 0.8 && Point.X >= 127940 && Point.X <= 129300
            && Point.Y >= -137300 && Point.Y <= -136700 && FMath::Abs(Point.Z - 15) <= 3
            && FMath::Abs(Position.Z - CapsuleHalfHeight - Point.Z) <= 5;
    }
    return bClear && bDry && Character->GetCapsuleComponent()->GetCollisionEnabled() != ECollisionEnabled::NoCollision;
}

bool UCityRowboatCheck::IsBoarded() const
{
    return Hero() && Boat.IsValid() && Boat->bOccupied && Controller->GetDrivenVehicle() == Boat.Get()
        && Hero()->IsHidden() && Hero()->GetAttachParentActor() == Boat.Get()
        && !Hero()->GetActorEnableCollision() && Hero()->GetCharacterMovement()->MovementMode == MOVE_None;
}
