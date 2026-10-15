#pragma once

#include "CoreMinimal.h"
#include "InputCoreTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityInputSmokeSubsystem.generated.h"

class AANANTACityCharacter;
class AANANTACityController;
class AANANTACityInteractable;
class AANANTACityVehicle;
class UANANTACitySubsystem;

enum class ECityInputSmokePhase : uint8
{
    WaitReady,
    WalkToGiver,
    StartMission,
    LeaveCafe,
    WalkToCar,
    EnterCar,
    Drive,
    Brake,
    ExitCar,
    Save,
    Done
};

UCLASS()
class ANANTA_API UCityInputSmokeSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;

private:
    bool Prepare();
    void RunPhase();
    void RunWalkingPhase();
    void RunVehiclePhase();
    bool WalkToward(const FVector& Destination, float Tolerance);
    bool CheckCamera(bool bVehicle) const;
    bool CheckSafeExit() const;
    bool VerifySavedProgress() const;
    void SetKey(const FKey& Key, bool bDown);
    void TapKey(const FKey& Key);
    void ReleaseKeys();
    void NextPhase(ECityInputSmokePhase Next, const FString& Detail);
    void Observe(bool bPass, const FString& Detail);
    bool WriteReport(bool bComplete, bool bPass) const;
    void Finish(bool bPass, const FString& Detail);
    const TCHAR* PhaseName() const;
    float PhaseTimeout() const;
    AANANTACityCharacter* GetHero() const;
    UANANTACitySubsystem* GetState() const;

    TWeakObjectPtr<AANANTACityController> Controller;
    TWeakObjectPtr<AANANTACityInteractable> Giver;
    TWeakObjectPtr<AANANTACityVehicle> Car;
    TSet<FKey> HeldKeys;
    TMap<FKey, double> PulseReleaseTimes;
    TArray<FString> Observations;
    FVector InitialLocation = FVector::ZeroVector;
    FVector DriveOrigin = FVector::ZeroVector;
    FVector DriveTarget = FVector::ZeroVector;
    ECityInputSmokePhase Phase = ECityInputSmokePhase::WaitReady;
    double StartTime = 0;
    double PhaseStartTime = 0;
    double Now = 0;
    float PhaseElapsed = 0;
    int32 CafeWaypoint = 0;
    int32 ExitFrames = 0;
    uint32 SaveAttemptsBefore = 0;
    uint32 SavesBefore = 0;
    bool bInputSent = false;
    bool bFinished = false;
    bool bPassed = false;
};
