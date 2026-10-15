#include "CoastalInteractable.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"

ACoastalInteractable::ACoastalInteractable()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = false;
    PrimaryActorTick.TickInterval = 0.1f;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Pivot"));
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(RootComponent);
    Mesh->SetMobility(EComponentMobility::Movable);
}

ECoastalInteractionKind ACoastalInteractable::KindFromLegacyValue(const int32 LegacyKind)
{
    switch (LegacyKind)
    {
    case 0: return ECoastalInteractionKind::Service;
    case 1: return ECoastalInteractionKind::Door;
    case 2: return ECoastalInteractionKind::NPC;
    case 3: return ECoastalInteractionKind::Item;
    case 4: return ECoastalInteractionKind::Elevator;
    case 5: return ECoastalInteractionKind::Prop;
    case 6: return ECoastalInteractionKind::Signal;
    default: return ECoastalInteractionKind::Unknown;
    }
}

FName ACoastalInteractable::NormalizeIdentifier(const FName Value, const FName Fallback)
{
    if (Value.IsNone())
    {
        return Fallback;
    }
    FString Text = Value.ToString();
    Text.TrimStartAndEndInline();
    Text.ReplaceInline(TEXT(" "), TEXT("_"));
    return Text.IsEmpty() ? Fallback : FName(*Text.ToLower());
}

void ACoastalInteractable::NormalizeInteractionMetadata()
{
    const ECoastalInteractionKind LegacyKind = KindFromLegacyValue(Kind);
    if (InteractionKind == ECoastalInteractionKind::Service && Kind != 0)
    {
        InteractionKind = LegacyKind;
    }
    else if (InteractionKind != ECoastalInteractionKind::Unknown)
    {
        Kind = static_cast<int32>(InteractionKind);
    }
    if (InteractionKind == ECoastalInteractionKind::Unknown)
    {
        InteractionKind = LegacyKind;
    }
    const FName ActorId = NormalizeIdentifier(GetFName(), TEXT("coastal_interaction"));
    VenueId = NormalizeIdentifier(VenueId, TEXT("coastal"));
    PropId = NormalizeIdentifier(PropId, ActorId);
    if (SaveKey.IsNone())
    {
        SaveKey = FName(*FString::Printf(TEXT("%s_%s"), *VenueId.ToString(), *PropId.ToString()));
    }
    if (Prompt.IsEmpty())
    {
        Prompt = ActionName.IsEmpty() ? TEXT("Inspect") : ActionName;
    }
    if (Response.IsEmpty())
    {
        Response = Message;
    }
    if (FailureMessage.IsEmpty())
    {
        FailureMessage = TEXT("Interaction is unavailable.");
    }
    if (InteractionKind == ECoastalInteractionKind::Item
        && CollisionPolicy == ECoastalCollisionPolicy::Preserve)
    {
        CollisionPolicy = ECoastalCollisionPolicy::DisableWhenHidden;
    }
    LastInteractionMarker = FString::Printf(TEXT("P4A_READY venue=%s prop=%s kind=%d"),
        *VenueId.ToString(), *PropId.ToString(), Kind);
}

void ACoastalInteractable::BeginPlay()
{
    Super::BeginPlay();
    NormalizeInteractionMetadata();
    ClosedRotation = GetActorRotation();
    if (Mesh)
    {
        OriginalCollisionEnabled = Mesh->GetCollisionEnabled();
        bCollisionStateCaptured = true;
    }
    const ECoastalInteractionKind CurrentKind = GetInteractionKind();
    if (CurrentKind == ECoastalInteractionKind::NPC && bScheduleEnabled)
    {
        ScheduleOrigin = GetActorLocation();
        SchedulePhase = FMath::Fmod(FMath::Abs(ScheduleOrigin.X + ScheduleOrigin.Y), 628.0f) / 100.0f;
        bScheduleActive = true;
        SetActorTickEnabled(true);
    }
    if (CurrentKind == ECoastalInteractionKind::Signal)
    {
        SignalPhase = FMath::Fmod(FMath::Abs(GetActorLocation().X + GetActorLocation().Y), 1200.0f) / 100.0f;
        SetActorTickEnabled(true);
    }
    if (CurrentKind == ECoastalInteractionKind::NPC && bScheduleDistanceGating)
    {
        SetActorTickEnabled(true);
    }
}

bool ACoastalInteractable::IsSchedulePlayerInRange() const
{
    const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!Player)
    {
        return true;
    }
    return FVector::Dist2D(Player->GetActorLocation(), ScheduleOrigin)
        <= FMath::Max(100.f, ScheduleActivationDistance);
}

void ACoastalInteractable::SetScheduleActive(const bool bActive)
{
    if (bScheduleActive == bActive)
    {
        return;
    }
    bScheduleActive = bActive;
    if (bHideWhenScheduleInactive)
    {
        SetActorHiddenInGame(!bActive);
    }
    if (Mesh && bCollisionStateCaptured)
    {
        if (!bActive && bDisableCollisionWhenScheduleInactive)
        {
            Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        }
        else if (bActive)
        {
            Mesh->SetCollisionEnabled(OriginalCollisionEnabled);
        }
    }
    LastInteractionMarker = FString::Printf(TEXT("P4A_SCHEDULE_%s venue=%s prop=%s"),
        bActive ? TEXT("SPAWN") : TEXT("DESPAWN"), *VenueId.ToString(), *PropId.ToString());
}

void ACoastalInteractable::UpdateScheduleActivation()
{
    if (GetInteractionKind() == ECoastalInteractionKind::NPC && bScheduleDistanceGating)
    {
        SetScheduleActive(IsSchedulePlayerInRange());
    }
}

void ACoastalInteractable::Tick(const float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    const ECoastalInteractionKind CurrentKind = GetInteractionKind();
    if (CurrentKind == ECoastalInteractionKind::Signal)
    {
        const float Period = FMath::Max(3.0f, SignalPeriod);
        SignalPhase += DeltaSeconds;
        const float Phase = FMath::Fmod(SignalPhase, Period);
        const float GreenEnd = Period * 0.55f;
        const float YellowEnd = Period * 0.65f;
        SignalState = Phase < GreenEnd ? 0 : Phase < YellowEnd ? 1 : 2;
        const TCHAR* State = SignalState == 0 ? TEXT("Green")
            : SignalState == 1 ? TEXT("Yellow") : TEXT("Red");
        ActionName = FString::Printf(TEXT("Signal: %s"), State);
        Message = FString::Printf(TEXT("Traffic signal is %s."), State);
        Prompt = ActionName;
        Response = Message;
        return;
    }
    if (CurrentKind != ECoastalInteractionKind::NPC || !bScheduleEnabled)
    {
        return;
    }
    UpdateScheduleActivation();
    if (!bScheduleActive)
    {
        return;
    }
    SchedulePhase += DeltaSeconds * FMath::Max(0.05f, ScheduleSpeed);
    const float Horizontal = FMath::Sin(SchedulePhase) * ScheduleRadius;
    const float Depth = FMath::Sin(SchedulePhase * 0.73f) * ScheduleRadius * 0.35f;
    SetActorLocation(ScheduleOrigin + FVector(Horizontal, Depth, 0));
}

void ACoastalInteractable::RecordInteraction(const bool bSuccess, const FString& Detail)
{
    LastInteractionMarker = FString::Printf(TEXT("P4A_INTERACTION_%s venue=%s prop=%s kind=%d detail=%s"),
        bSuccess ? TEXT("PASS") : TEXT("FAIL"), *VenueId.ToString(), *PropId.ToString(), Kind, *Detail);
    UE_LOG(LogTemp, Display, TEXT("%s"), *LastInteractionMarker);
}

FString ACoastalInteractable::ReportInteractionFailure(const FString& FailureReason)
{
    const FString Detail = FailureReason.IsEmpty() ? FailureMessage : FailureReason;
    RecordInteraction(false, Detail);
    return Detail;
}

FString ACoastalInteractable::FailInteraction(const FString& Reason)
{
    return ReportInteractionFailure(Reason);
}

FString ACoastalInteractable::Use()
{
    NormalizeInteractionMetadata();
    if (!bInteractionEnabled || !IsValid(Mesh))
    {
        return FailInteraction(FailureMessage);
    }
    const ECoastalInteractionKind CurrentKind = GetInteractionKind();
    if (CurrentKind == ECoastalInteractionKind::Item && bUsed)
    {
        return ReportInteractionFailure(TEXT("Already collected"));
    }
    if (CurrentKind == ECoastalInteractionKind::Door)
    {
        bUsed = !bUsed;
        SetActorRotation(ClosedRotation + FRotator(0, bUsed ? 95 : 0, 0));
        const FString DoorResponse = bUsed ? TEXT("Door opened") : TEXT("Door closed");
        RecordInteraction(true, DoorResponse);
        return DoorResponse;
    }
    if (CurrentKind == ECoastalInteractionKind::Item)
    {
        Mesh->SetVisibility(false);
        Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
    bUsed = true;
    const FString Result = GetInteractionResponse();
    RecordInteraction(true, Result);
    return Result;
}

FName ACoastalInteractable::GetVenueId() const
{
    return VenueId;
}

FName ACoastalInteractable::GetPropId() const
{
    return PropId;
}

ECoastalInteractionKind ACoastalInteractable::GetInteractionKind() const
{
    if (InteractionKind == ECoastalInteractionKind::Service && Kind != 0)
    {
        return KindFromLegacyValue(Kind);
    }
    return InteractionKind == ECoastalInteractionKind::Unknown
        ? KindFromLegacyValue(Kind) : InteractionKind;
}

FString ACoastalInteractable::GetInteractionPrompt() const
{
    return Prompt.IsEmpty() ? ActionName : Prompt;
}

FString ACoastalInteractable::GetInteractionResponse() const
{
    return Response.IsEmpty() ? Message : Response;
}

ECoastalCollisionPolicy ACoastalInteractable::GetCollisionPolicy() const
{
    return CollisionPolicy;
}

FName ACoastalInteractable::GetInteractionSaveKey() const
{
    return SaveKey;
}

bool ACoastalInteractable::IsInteractionAvailable() const
{
    return bInteractionEnabled && IsValid(Mesh)
        && !(GetInteractionKind() == ECoastalInteractionKind::Item && bUsed)
        && bScheduleActive;
}

FString ACoastalInteractable::GetLastInteractionMarker() const
{
    return LastInteractionMarker;
}
