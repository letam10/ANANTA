#pragma once

#include "CoreMinimal.h"
#include "InputCoreTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityRowboatCheck.generated.h"

class AActor;
class ACharacter;
class AANANTACityController;
class ACityRowboat;
class UWorldPartitionStreamingSourceComponent;

enum class ECityRowboatPhase : uint8
{
    WaitReady,
    Settle,
    Board,
    Row,
    Brake,
    Alight,
    OpenSea,
    Done
};

struct FCityRowboatPhaseResult
{
    FString Phase;
    FString Status;
    FString Reason;
    double ElapsedSeconds = 0;
};

UCLASS()
class ANANTA_API UCityRowboatCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;

private:
    ACharacter* Hero() const;
    bool PrepareStreaming();
    bool PrepareHero();
    bool CheckCapsule() const;
    bool CheckDryDock(bool& bClear, bool& bDry) const;
    bool IsBoarded() const;
    void RunPhase();
    void SetKey(const FKey& Key, bool bDown);
    void ReleaseKeys();
    void Advance(ECityRowboatPhase Next, const FString& Reason);
    void Finish(bool bSuccess, const FString& Reason);
    const TCHAR* PhaseName() const;

    TWeakObjectPtr<AANANTACityController> Controller;
    TWeakObjectPtr<ACityRowboat> Boat;
    TWeakObjectPtr<AActor> Observer;
    TWeakObjectPtr<UWorldPartitionStreamingSourceComponent> StreamingSource;
    TSet<FKey> HeldKeys;
    TArray<FCityRowboatPhaseResult> Results;
    ECityRowboatPhase Phase = ECityRowboatPhase::WaitReady;
    FVector PreviousBoatPosition = FVector::ZeroVector;
    FVector RowOrigin = FVector::ZeroVector;
    FString BoardPrompt;
    FString AlightPrompt;
    double StartedAt = 0;
    double StableAt = 0;
    double PhaseAt = 0;
    double PhaseSeconds = 0;
    double MeasuredTravelCm = 0;
    double RowDisplacementCm = 0;
    double RowSeconds = 0;
    double PeakSpeedKmh = 0;
    double BrakeStartSpeedKmh = 0;
    double StoppedSpeedKmh = 0;
    float CapsuleRadius = 0;
    float CapsuleHalfHeight = 0;
    bool bQASlot = false;
    bool bStreamed = false;
    bool bCapsule = false;
    bool bBoard = false;
    bool bRowInput = false;
    bool bBrakeInput = false;
    bool bBrake = false;
    bool bAlight = false;
    bool bCapsuleClear = false;
    bool bDryFloor = false;
    bool bOpenSeaSetup = false;
    bool bOpenSeaExitRejected = false;
    bool bFinished = false;
    bool bPassed = false;
    int32 ExitFrames = 0;
};
