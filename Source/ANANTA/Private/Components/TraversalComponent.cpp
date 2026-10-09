#include "Components/TraversalComponent.h"

#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"

UTraversalComponent::UTraversalComponent()
    : WalkSpeed(350.0f)
    , SprintSpeed(650.0f)
    , MaxMantleHeight(180.0f)
    , MantleForwardDistance(75.0f)
    , bIsSprinting(false)
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UTraversalComponent::StartSprint()
{
    bIsSprinting = true;
    ApplyMovementSpeed(SprintSpeed);
}

void UTraversalComponent::StopSprint()
{
    bIsSprinting = false;
    ApplyMovementSpeed(WalkSpeed);
}

bool UTraversalComponent::TryMantle()
{
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    UWorld* World = GetWorld();
    if (!Character || !World)
    {
        return false;
    }
    UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
    if (!Movement || Movement->MovementMode == MOVE_None)
    {
        return false;
    }

    const FVector Forward = Character->GetActorForwardVector();
    const float HalfHeight = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    const float Radius = Character->GetCapsuleComponent()->GetScaledCapsuleRadius();
    const FVector Feet = Character->GetActorLocation() - FVector(0, 0, HalfHeight);
    const FVector ChestStart = Feet + FVector(0.0f, 0.0f, 80.0f);
    const FVector WallEnd = ChestStart + Forward * MantleForwardDistance;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(ANANTA_Mantle), false, Character);
    FHitResult WallHit;
    if (!World->LineTraceSingleByChannel(WallHit, ChestStart, WallEnd, ECC_Pawn, QueryParams))
    {
        return false;
    }

    const FVector TopStart = Feet + Forward * MantleForwardDistance + FVector(0.0f, 0.0f, MaxMantleHeight);
    const FVector TopEnd = Feet + Forward * MantleForwardDistance - FVector(0.0f, 0.0f, 20.0f);
    FHitResult TopHit;
    if (!World->LineTraceSingleByChannel(TopHit, TopStart, TopEnd, ECC_Pawn, QueryParams)
        || !Movement->IsWalkable(TopHit))
    {
        return false;
    }

    const FVector MantleLocation = TopHit.Location + FVector(0, 0, HalfHeight + 3);
    const FVector LiftLocation(Character->GetActorLocation().X, Character->GetActorLocation().Y, MantleLocation.Z);
    const FCollisionShape Capsule = FCollisionShape::MakeCapsule(Radius, HalfHeight);
    FHitResult Clearance;
    // Quet duong nang len roi tien toi, tranh xuyen tran hoac ket vao mep tuong.
    if (World->SweepSingleByChannel(Clearance, Character->GetActorLocation(), LiftLocation,
            FQuat::Identity, ECC_Pawn, Capsule, QueryParams)
        || World->SweepSingleByChannel(Clearance, LiftLocation, MantleLocation,
            FQuat::Identity, ECC_Pawn, Capsule, QueryParams)
        || World->OverlapBlockingTestByChannel(MantleLocation, FQuat::Identity, ECC_Pawn, Capsule, QueryParams))
    {
        return false;
    }
    Character->SetActorLocation(MantleLocation);

    Movement->StopMovementImmediately();
    Movement->SetMovementMode(MOVE_Walking);
    return true;
}

void UTraversalComponent::ApplyMovementSpeed(const float NewSpeed)
{
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character || !Character->GetCharacterMovement())
    {
        return;
    }

    Character->GetCharacterMovement()->MaxWalkSpeed = NewSpeed;
}
