#pragma once

#include "CoreMinimal.h"
#include "InputCoreTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityMissionCheckSubsystem.generated.h"

class AANANTACityCharacter;
class AANANTACityController;
class AANANTACityInteractable;
class AANANTACityVehicle;
class UANANTACitySubsystem;
class UANANTACitySave;

enum class ECityMissionCheckPhase : uint8
{
    WaitReady,
    Route,
    Interact,
    Fight,
    Repeat,
    Save
};

UCLASS()
class ANANTA_API UCityMissionCheckSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;

private:
    void Prepare();
    void RunPhase();
    void RunInteraction();
    void RunCombat();
    void RunSave();
    void BeginRoute();
    bool WalkToward(const FVector& Destination, float Tolerance);
    AANANTACityInteractable* FindItem(FName Id) const;
    FName ObjectiveId() const;
    AANANTACityCharacter* GetHero() const;
    UANANTACitySubsystem* GetState() const;
    bool IsComplete(const UANANTACitySave* Save) const;
    bool IsSafelyGrounded() const;
    bool VerifySavedProgress() const;
    bool WriteCheckpoint() const;
    bool ReadCheckpoint();
    bool VerifyRestoredProgress() const;
    void SetKey(const FKey& Key, bool bDown);
    void TapKey(const FKey& Key);
    void ReleaseKeys();
    void NextPhase(ECityMissionCheckPhase Next, const FString& Detail);
    void Observe(bool bPass, const FString& Detail);
    bool WriteReport(bool bComplete, bool bPass) const;
    void Finish(bool bPass, const FString& Detail);
    const TCHAR* PhaseName() const;
    float PhaseTimeout() const;
    FString EvidenceDirectory() const;

    TWeakObjectPtr<AANANTACityController> Controller;
    TWeakObjectPtr<AANANTACityVehicle> Car;
    TSet<FKey> HeldKeys;
    TMap<FKey, double> PulseReleaseTimes;
    TArray<FString> Observations;
    TArray<FVector> Waypoints;
    TSet<FName> SeenActiveEnemies;
    TSet<FName> ObservedDefeats;
    FTransform ExpectedPlayer;
    FTransform ExpectedCar;
    FVector LastLocation = FVector::ZeroVector;
    FVector MotionOrigin = FVector::ZeroVector;
    ECityMissionCheckPhase Phase = ECityMissionCheckPhase::WaitReady;
    double StartTime = 0;
    double PhaseStartTime = 0;
    double Now = 0;
    double MotionTime = 0;
    double LastAttackTime = -100;
    float PhaseElapsed = 0;
    int32 Objective = 0;
    int32 Waypoint = 0;
    int32 ExitFrames = 0;
    uint32 SaveAttemptsBefore = 0;
    uint32 SavesBefore = 0;
    bool bReload = false;
    bool bInputSent = false;
    bool bFinished = false;
    bool bPassed = false;
};
