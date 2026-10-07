#include "ANANTACharacter.h"

#include "Components/CombatComponent.h"
#include "Components/TraversalComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

AANANTACharacter::AANANTACharacter()
{
    TraversalComponent = CreateDefaultSubobject<UTraversalComponent>(TEXT("TraversalComponent"));
    CombatComponent = CreateDefaultSubobject<UCombatComponent>(TEXT("CombatComponent"));

    GetCharacterMovement()->MaxWalkSpeed = TraversalComponent->WalkSpeed;
    GetCharacterMovement()->AirControl = 0.65f;
}
