#include "City/ANANTACityInteractable.h"

#include "City/ANANTACitySubsystem.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Pawn.h"

AANANTACityInteractable::AANANTACityInteractable()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.25f;
    VisualMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VisualMesh"));
    SetRootComponent(VisualMesh);
    VisualMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    MarkerLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("MarkerLight"));
    MarkerLight->SetupAttachment(RootComponent);
    MarkerLight->SetLightColor(FLinearColor(0.1f, 0.65f, 1));
    MarkerLight->SetIntensity(1800);
    MarkerLight->SetAttenuationRadius(300);
    MarkerLight->SetCastShadows(false);
}

bool AANANTACityInteractable::IsAvailable() const
{
    if (!GetGameInstance())
    {
        return false;
    }
    const auto* State = GetGameInstance()->GetSubsystem<UANANTACitySubsystem>();
    FCityMissionState Preview = State->GetMission();
    return Preview.Interact(InteractionId, InteractionKind);
}

bool AANANTACityInteractable::Interact(APawn* Player)
{
    if (!Player || !Player->IsPlayerControlled() || !IsAvailable()
        || FVector::DistSquared(Player->GetActorLocation(), GetActorLocation()) > 320 * 320)
    {
        return false;
    }
    return GetGameInstance()->GetSubsystem<UANANTACitySubsystem>()->TryInteract(InteractionId, InteractionKind);
}

FString AANANTACityInteractable::GetPrompt() const
{
    switch (InteractionKind)
    {
    case ECityInteractionKind::Giver:
        return TEXT("E: speak with cafe contact");
    case ECityInteractionKind::Clue:
        return TEXT("E: investigate anomaly trace");
    case ECityInteractionKind::Fragment:
        return TEXT("E: recover fragment");
    default:
        return TEXT("");
    }
}

void AANANTACityInteractable::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    const bool bAvailable = IsAvailable();
    MarkerLight->SetVisibility(bAvailable);
    if (InteractionKind == ECityInteractionKind::Fragment)
    {
        SetActorHiddenInGame(!bAvailable);
    }
}
