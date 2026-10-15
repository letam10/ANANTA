#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoastalInteractable.generated.h"

class UStaticMeshComponent;
struct FTimerHandle;

UENUM(BlueprintType)
enum class ECoastalInteractionKind : uint8
{
    Service = 0,
    Door = 1,
    NPC = 2,
    Item = 3,
    Elevator = 4,
    Prop = 5,
    Signal = 6,
    Unknown = 255
};

UENUM(BlueprintType)
enum class ECoastalCollisionPolicy : uint8
{
    Preserve,
    DisableWhenHidden,
    QueryOnlyWhenHidden
};

UCLASS()
class ANANTA_API ACoastalInteractable : public AActor
{
    GENERATED_BODY()

public:
    ACoastalInteractable();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString ActionName = TEXT("Inspect");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString Message = TEXT("Welcome to the coastal district.");

    // 0: dịch vụ, 1: cửa, 2: NPC, 3: vật phẩm, 4: thang máy, 5: prop nhỏ, 6: đèn giao thông.
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Kind = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction")
    FName VenueId = TEXT("coastal");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction")
    FName PropId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction")
    ECoastalInteractionKind InteractionKind = ECoastalInteractionKind::Service;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction")
    FString Prompt;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction", meta = (MultiLine = true))
    FString Response;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction", meta = (MultiLine = true))
    FString FailureMessage = TEXT("Interaction is unavailable.");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction")
    ECoastalCollisionPolicy CollisionPolicy = ECoastalCollisionPolicy::Preserve;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction")
    FName SaveKey = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Interaction")
    bool bInteractionEnabled = true;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "P4A|Interaction")
    FString LastInteractionMarker;

    // Lịch nhẹ cho cư dân (Kind = 2), di chuyển quanh điểm neo.
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bScheduleEnabled = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float ScheduleRadius = 120.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float ScheduleSpeed = 0.65f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FVector Destination = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float SignalPeriod = 12.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Schedule")
    bool bScheduleDistanceGating = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Schedule")
    float ScheduleActivationDistance = 3200.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Schedule")
    bool bHideWhenScheduleInactive = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "P4A|Schedule")
    bool bDisableCollisionWhenScheduleInactive = false;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly)
    int32 SignalState = 0;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly)
    bool bUsed = false;

    UFUNCTION(BlueprintCallable)
    FString Use();

    UFUNCTION(BlueprintCallable, Category = "P4A|Interaction")
    FString ReportInteractionFailure(const FString& FailureReason);

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    FName GetVenueId() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    FName GetPropId() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    ECoastalInteractionKind GetInteractionKind() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    FString GetInteractionPrompt() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    FString GetInteractionResponse() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    ECoastalCollisionPolicy GetCollisionPolicy() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    FName GetInteractionSaveKey() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    bool IsInteractionAvailable() const;

    UFUNCTION(BlueprintPure, Category = "P4A|Interaction")
    FString GetLastInteractionMarker() const;

private:
    FRotator ClosedRotation;
    FVector ScheduleOrigin;
    float SchedulePhase = 0.f;
    float SignalPhase = 0.f;
    bool bScheduleActive = true;
    bool bCollisionStateCaptured = false;
    ECollisionEnabled::Type OriginalCollisionEnabled = ECollisionEnabled::QueryAndPhysics;
    FTimerHandle ScheduleGateTimer;

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    static ECoastalInteractionKind KindFromLegacyValue(int32 LegacyKind);
    static FName NormalizeIdentifier(FName Value, FName Fallback);
    void NormalizeInteractionMetadata();
    void RecordInteraction(bool bSuccess, const FString& Detail);
    FString FailInteraction(const FString& Reason);
    bool IsSchedulePlayerInRange() const;
    void UpdateScheduleActivation();
    void SetScheduleActive(bool bActive);
};
