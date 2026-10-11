#pragma once

#include "CoreMinimal.h"
#include "InputCoreTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityServiceJourney.generated.h"

class AANANTACityCharacter;
class AANANTACityController;
class ACityServiceInteractable;
class UANANTACitySave;
class UANANTACitySubsystem;

enum class ECityServiceJourneyPhase : uint8
{
    WaitReady,
    Route,
    Interact,
    Repeat,
    Save,
    Reload
};

UCLASS()
class ANANTA_API UCityServiceJourney : public UTickableWorldSubsystem
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
    void RunInteraction(bool bRepeat);
    void BeginRoute();
    void BeginExit();
    void AddEntry(int32 Index, bool bReverse);
    bool WalkToward(const FVector& Destination);
    FName ServiceId(int32 Index) const;
    ACityServiceInteractable* FindService() const;
    AANANTACityCharacter* GetHero() const;
    UANANTACitySubsystem* GetState() const;
    bool MatchesProgress(const UANANTACitySave* Save, int32 Visits) const;
    bool VerifySavedProgress() const;
    bool WriteCheckpoint() const;
    bool ReadCheckpoint();
    bool VerifyRestoredProgress() const;
    void RunSave();
    void SetKey(const FKey& Key, bool bDown);
    void TapKey(const FKey& Key);
    void ReleaseKeys();
    void NextPhase(ECityServiceJourneyPhase Next, const FString& Detail);
    void Observe(bool bPass, const FString& Detail);
    bool WriteReport(bool bComplete, bool bPass) const;
    void Finish(bool bPass, const FString& Detail);
    const TCHAR* PhaseName() const;
    FString EvidenceDirectory() const;

    TWeakObjectPtr<AANANTACityController> Controller;
    TSet<FKey> HeldKeys;
    TMap<FKey, double> PulseReleaseTimes;
    TArray<FVector> Waypoints;
    TArray<FString> Observations;
    TArray<double> FrameMilliseconds;
    FTransform ExpectedPlayer;
    FVector LastLocation = FVector::ZeroVector;
    FVector MotionOrigin = FVector::ZeroVector;
    ECityServiceJourneyPhase Phase = ECityServiceJourneyPhase::WaitReady;
    double StartTime = 0;
    double PhaseStartTime = 0;
    double Now = 0;
    double MotionTime = 0;
    double LastFrameTime = 0;
    double PhaseElapsed = 0;
    int32 Venue = 0;
    int32 Waypoint = 0;
    int32 ExitFrames = 0;
    uint32 SaveAttemptsBefore = 0;
    uint32 SavesBefore = 0;
    bool bReload = false;
    bool bInputSent = false;
    bool bLeavingLastVenue = false;
    bool bFinished = false;
    bool bPassed = false;
};
