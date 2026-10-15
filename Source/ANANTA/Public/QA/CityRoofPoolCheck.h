#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityRoofPoolCheck.generated.h"

class AActor;
class AANANTACityCharacter;
class AANANTACityController;
class UANANTACitySubsystem;
class UWorldPartitionStreamingSourceComponent;

enum class ECityRoofPoolPhase : uint8
{
    WaitReady,
    Settle,
    Ascent,
    Landing,
    Roof,
    ReturnLanding,
    Descent,
    Ground,
    Done
};

struct FCityRoofPoolLeg
{
    FVector Start = FVector::ZeroVector;
    FVector End = FVector::ZeroVector;
    double TravelCm = 0;
    int32 Samples = 0;
    int32 InputSamples = 0;
    TSet<int32> Steps;
};

struct FCityRoofPoolPhaseResult
{
    FString Phase;
    FString Reason;
    bool bPassed = false;
    double ElapsedSeconds = 0;
};

UCLASS()
class ANANTA_API UCityRoofPoolCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;

private:
    AANANTACityCharacter* Hero() const;
    UANANTACitySubsystem* State() const;
    bool PrepareStreaming();
    bool PrepareHero();
    bool CheckBodySettings() const;
    bool ObserveBody(float DeltaTime);
    void RunPhase();
    void MoveToward(const FVector& Target);
    void SetForward(bool bDown);
    void Advance(ECityRoofPoolPhase Next, const FString& Reason);
    void Finish(bool bSuccess, const FString& Reason);
    const TCHAR* PhaseName() const;

    TWeakObjectPtr<AANANTACityController> Controller;
    TWeakObjectPtr<AActor> Observer;
    TWeakObjectPtr<UWorldPartitionStreamingSourceComponent> StreamingSource;
    TArray<FCityRoofPoolPhaseResult> Results;
    FCityRoofPoolLeg Ascent;
    FCityRoofPoolLeg Descent;
    ECityRoofPoolPhase Phase = ECityRoofPoolPhase::WaitReady;
    FVector Previous = FVector::ZeroVector;
    FVector ProgressOrigin = FVector::ZeroVector;
    FVector StairTop = FVector::ZeroVector;
    FString FloorActor;
    FString Blocker;
    double StartedAt = 0;
    double StableAt = 0;
    double PhaseAt = 0;
    double PhaseSeconds = 0;
    double ProgressAt = 0;
    double FloorZ = 0;
    double RoofZ = 0;
    float OriginalStepHeight = 0;
    float OriginalGravityScale = 0;
    int32 FloorSamples = 0;
    int32 ClearanceSamples = 0;
    int32 LandingInputSamples = 0;
    int32 ReturnInputSamples = 0;
    int32 RoofSamples = 0;
    int32 ExitFrames = 0;
    bool bForward = false;
    bool bQASlot = false;
    bool bStreamed = false;
    bool bSettingsUnchanged = false;
    bool bRoof = false;
    bool bReturned = false;
    bool bFinished = false;
    bool bPassed = false;
};
