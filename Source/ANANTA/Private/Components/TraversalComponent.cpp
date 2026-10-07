#include "Components/TraversalComponent.h"

#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"

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

    const FVector Forward = Character->GetActorForwardVector();
    const FVector Feet = Character->GetActorLocation();
    const FVector ChestStart = Feet + FVector(0.0f, 0.0f, 80.0f);
    const FVector WallEnd = ChestStart + Forward * MantleForwardDistance;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(ANANTA_Mantle), false, Character);
    FHitResult WallHit;
    if (!World->LineTraceSingleByChannel(WallHit, ChestStart, WallEnd, ECC_Visibility, QueryParams))
    {
        return false;
    }

    const FVector TopStart = Feet + Forward * MantleForwardDistance + FVector(0.0f, 0.0f, MaxMantleHeight);
    const FVector TopEnd = Feet + Forward * MantleForwardDistance - FVector(0.0f, 0.0f, 20.0f);
    FHitResult TopHit;
    if (!World->LineTraceSingleByChannel(TopHit, TopStart, TopEnd, ECC_Visibility, QueryParams)
        || TopHit.Normal.Z < 0.65f)
    {
        return false;
    }

    const FVector MantleLocation = TopHit.Location + FVector(0.0f, 0.0f, 96.0f);
    if (!Character->SetActorLocation(MantleLocation, true))
    {
        return false;
    }

    if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
    {
        Movement->SetMovementMode(MOVE_Walking);
    }
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
