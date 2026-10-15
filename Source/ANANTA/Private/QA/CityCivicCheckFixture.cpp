#include "QA/CityCivicCheck.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "City/CityServiceInteractable.h"
#include "Components/SceneComponent.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformTime.h"
#include "InputKeyEventArgs.h"

bool UCityCivicCheck::PrepareStreaming()
{
    if (!GetWorld()->GetWorldPartition())
    {
        Finish(false, TEXT("Requires the authored World Partition city"));
        return false;
    }
    for (const auto& Entry : Services)
    {
        auto* Anchor = GetWorld()->SpawnActor<AActor>();
        if (!Anchor)
        {
            Finish(false, TEXT("Cannot create a civic streaming anchor"));
            return false;
        }
        StreamingAnchors.Add(Anchor);
        auto* Root = NewObject<USceneComponent>(Anchor);
        Anchor->SetRootComponent(Root);
        Anchor->AddInstanceComponent(Root);
        Root->RegisterComponent();
        Anchor->SetActorLocation(Entry.Anchor + FVector(3300, 0, 150));
        auto* Source = NewObject<UWorldPartitionStreamingSourceComponent>(Anchor);
        Anchor->AddInstanceComponent(Source);
        FStreamingSourceShape Shape;
        Shape.bUseGridLoadingRange = false;
        Shape.Radius = 6500;
        Source->Shapes.Add(Shape);
        Source->TargetState = EStreamingSourceTargetState::Activated;
        Source->EnableStreamingSource();
        Source->RegisterComponent();
        Sources.Add(Source);
    }
    return true;
}

bool UCityCivicCheck::StreamingComplete() const
{
    if (Sources.Num() != 4)
    {
        return false;
    }
    for (const auto& Source : Sources)
    {
        if (!Source.IsValid() || !Source->IsStreamingCompleted())
        {
            return false;
        }
    }
    return true;
}

ACityServiceInteractable* UCityCivicCheck::Service() const
{
    ACityServiceInteractable* Found = nullptr;
    for (TActorIterator<ACityServiceInteractable> It(GetWorld()); It; ++It)
    {
        if (It->InteractionId == Services[SiteIndex].Id)
        {
            if (Found)
            {
                return nullptr;
            }
            Found = *It;
        }
    }
    return Found;
}

void UCityCivicCheck::SetupSite(const double Now)
{
    ReleaseKeys();
    const auto& Entry = Services[SiteIndex];
    const auto* Target = Service();
    if (!Target || Target->ServiceKind != ECityServiceKind::Read
        || !Target->GetActorLocation().Equals(Entry.Anchor + FVector(4730, 0, 100), 2))
    {
        Finish(false, TEXT("Missing, duplicate or displaced authored civic service"));
        return;
    }
    // Chi di chuyen setup sau khi streaming san sang; moi leg do deu dung W/Shift.
    const FVector Exterior = Entry.Anchor + FVector(1450, 0, 95);
    if (!Hero()->TeleportTo(Exterior, FRotator::ZeroRotator))
    {
        Finish(false, TEXT("Normal capsule cannot occupy the authored exterior fixture start"));
        return;
    }
    Hero()->GetCharacterMovement()->StopMovementImmediately();
    ++SetupRelocations;
    Phase = ECityCivicPhase::Settle;
    PhaseAt = Now;
    Previous = Hero()->GetActorLocation();
    UE_LOG(LogTemp, Display, TEXT("CITY_CIVIC_SETUP service=%s relocation=%d streamed=1"),
        *Entry.Id.ToString(), SetupRelocations);
}

void UCityCivicCheck::SetKey(const FKey& Key, const bool bDown)
{
    if (!Controller.IsValid() || HeldKeys.Contains(Key) == bDown)
    {
        return;
    }
    Controller->InputKey(FInputKeyEventArgs(nullptr, INPUTDEVICEID_NONE, Key,
        bDown ? IE_Pressed : IE_Released, bDown ? 1.f : 0.f, false, FPlatformTime::Cycles64()));
    if (bDown)
    {
        HeldKeys.Add(Key);
    }
    else
    {
        HeldKeys.Remove(Key);
    }
}

void UCityCivicCheck::ReleaseKeys()
{
    for (const FKey& Key : HeldKeys.Array())
    {
        SetKey(Key, false);
    }
    HeldKeys.Empty();
}

void UCityCivicCheck::Interact(const double Now)
{
    Previous = Hero()->GetActorLocation();
    if (!bESent && Now - PhaseAt >= 0.5)
    {
        auto* Target = Service();
        Services[SiteIndex].Prompt = Controller->GetInteractionPrompt();
        if (!Target || Controller->FindInteractionTarget() != Target
            || Services[SiteIndex].Prompt.IsEmpty()
            || State()->GetServices().VisitedIds.Contains(Services[SiteIndex].Id))
        {
            Finish(false, TEXT("Fresh service is not the ordinary E interaction target with a prompt"));
            return;
        }
        SetKey(EKeys::E, true);
        bESent = true;
        PhaseAt = Now;
        return;
    }
    if (!bESent)
    {
        return;
    }
    if (Now - PhaseAt >= 0.15)
    {
        SetKey(EKeys::E, false);
    }
    if (Now - PhaseAt >= 0.5)
    {
        if (!State()->GetServices().VisitedIds.Contains(Services[SiteIndex].Id)
            || State()->GetServices().VisitedIds.Num() != SiteIndex + 1)
        {
            Finish(false, TEXT("Actual E input did not discover exactly this civic service"));
            return;
        }
        Services[SiteIndex].bInteracted = true;
        BeginLeg(false, Now);
    }
}
