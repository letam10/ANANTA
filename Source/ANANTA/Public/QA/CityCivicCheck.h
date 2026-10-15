#pragma once

#include "CoreMinimal.h"
#include "InputCoreTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityCivicCheck.generated.h"

class AANANTACityCharacter;
class AActor;
class AANANTACityController;
class ACityServiceInteractable;
class UANANTACitySubsystem;
class UWorldPartitionStreamingSourceComponent;

struct FCityCivicLeg
{
    FString Service;
    FString Direction;
    FString Status = TEXT("PENDING");
    FString Reason;
    FVector Start = FVector::ZeroVector;
    FVector End = FVector::ZeroVector;
    double Travel = 0;
    double Elapsed = 0;
    int32 GroundChecks = 0;
    int32 CollisionChecks = 0;
    int32 InputChecks = 0;
    int32 SprintInputChecks = 0;
    bool bCrossedDoor = false;
};

struct FCityCivicService
{
    FName Id;
    FVector Anchor = FVector::ZeroVector;
    FString Prompt;
    bool bInteracted = false;
};

enum class ECityCivicPhase : uint8
{
    Streaming, Settle, Inward, Interact, Outward
};

UCLASS()
class ANANTA_API UCityCivicCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    AANANTACityCharacter* Hero() const;
    UANANTACitySubsystem* State() const;
    ACityServiceInteractable* Service() const;
    bool PrepareStreaming();
    bool StreamingComplete() const;
    void SetupSite(double Now);
    void BeginLeg(bool bInward, double Now);
    bool ObserveBody(float DeltaTime, bool bMeasured);
    void MoveLeg(float DeltaTime, double Now);
    void Interact(double Now);
    void SetKey(const FKey& Key, bool bDown);
    void ReleaseKeys();
    void Finish(bool bSuccess, const FString& Reason);
    TArray<FCityCivicService> Services;
    TArray<FCityCivicLeg> Legs;
    TArray<TWeakObjectPtr<AActor>> StreamingAnchors;
    TArray<TWeakObjectPtr<UWorldPartitionStreamingSourceComponent>> Sources;
    TWeakObjectPtr<AANANTACityController> Controller;
    TSet<FKey> HeldKeys;
    FVector Previous = FVector::ZeroVector;
    FVector ProgressOrigin = FVector::ZeroVector;
    ECityCivicPhase Phase = ECityCivicPhase::Streaming;
    int32 SiteIndex = 0;
    int32 LegIndex = 0;
    int32 SetupRelocations = 0;
    int32 ExitFrames = 0;
    double StartedAt = 0;
    double ReadyAt = 0;
    double StableAt = 0;
    double PhaseAt = 0;
    double ProgressAt = 0;
    bool bESent = false;
    bool bFinished = false;
    bool bPassed = false;
};
