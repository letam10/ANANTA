#include "City/CityServiceInteractable.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACitySubsystem.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

bool ACityServiceInteractable::CanUseService(const APawn* Player) const
{
    if (!Player || !Player->IsPlayerControlled() || Player->GetWorld() != GetWorld() || !GetWorld()
        || FVector::DistSquared(Player->GetActorLocation(), GetActorLocation()) > 320.0 * 320.0
        || !FCityServiceState::IsServiceId(InteractionId, ServiceKind))
    {
        return false;
    }
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityService), false, Player);
    Params.AddIgnoredActor(this);
    const FVector Start = Player->GetActorLocation() + FVector(0, 0, 40);
    const FVector End = GetActorLocation() + FVector(0, 0, 40);
    return !GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params);
}

bool ACityServiceInteractable::IsAvailable() const
{
    const auto* State = GetGameInstance() ? GetGameInstance()->GetSubsystem<UANANTACitySubsystem>() : nullptr;
    return State && State->GetProgress() && State->GetServices().IsValid()
        && CanUseService(UGameplayStatics::GetPlayerPawn(this, 0));
}

bool ACityServiceInteractable::Interact(APawn* Player)
{
    if (!CanUseService(Player) || !GetGameInstance())
    {
        return false;
    }
    auto* Hero = Cast<AANANTACityCharacter>(Player);
    const bool bRestoreHealth = ServiceKind == ECityServiceKind::Rest || ServiceKind == ECityServiceKind::Heal;
    if (bRestoreHealth && !Hero)
    {
        return false;
    }
    auto* State = GetGameInstance()->GetSubsystem<UANANTACitySubsystem>();
    if (!State || !State->TryUseService(InteractionId, ServiceKind, Description))
    {
        return false;
    }
    if (bRestoreHealth)
    {
        Hero->Health = 100;
    }
    return true;
}

FString ACityServiceInteractable::GetPrompt() const
{
    const FString Name = DisplayName.IsEmpty() ? InteractionId.ToString() : DisplayName;
    const auto* State = GetGameInstance() ? GetGameInstance()->GetSubsystem<UANANTACitySubsystem>() : nullptr;
    FString Action;
    switch (ServiceKind)
    {
    case ECityServiceKind::Rest:
        Action = TEXT("rest and save");
        break;
    case ECityServiceKind::Heal:
        Action = TEXT("restore health");
        break;
    case ECityServiceKind::Supplies:
        Action = State && State->GetProgress() && State->GetServices().ClaimedSupplyIds.Contains(InteractionId)
            ? TEXT("supplies already collected") : TEXT("collect supplies");
        break;
    case ECityServiceKind::Read:
        Action = State && State->GetProgress() && State->GetServices().VisitedIds.Contains(InteractionId)
            ? TEXT("read again (discovered)") : TEXT("discover this location");
        break;
    default:
        return FString();
    }
    return FString::Printf(TEXT("E: %s - %s"), *Name, *Action);
}
