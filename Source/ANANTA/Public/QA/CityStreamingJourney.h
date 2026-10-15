#pragma once

#include "CoreMinimal.h"
#include "InputCoreTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityStreamingJourney.generated.h"

class AANANTACityCharacter;
class AANANTACityController;
class UANANTACitySubsystem;

enum class ECityStreamingPhase : uint8
{
    WaitReady,
    Route,
    Settle,
    Capture
};

UCLASS()
class ANANTA_API UCityStreamingJourney : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;

private:
    AANANTACityCharacter* GetHero() const;
    UANANTACitySubsystem* GetState() const;
    bool Begin();
    void Prepare();
    bool CheckMovement(float DeltaTime);
    void RunRoute();
    void RunCapture();
    void SetKey(const FKey& Key, bool bDown);
    void ReleaseKeys();
    void NextPhase(ECityStreamingPhase Next, const FString& Detail);
    void Observe(const FString& Detail);
    bool WriteReport(bool bComplete, bool bPass) const;
    void Finish(bool bPass, const FString& Detail);
    FString EvidenceDirectory() const;
    FString ScreenshotPath(int32 Index) const;

    TWeakObjectPtr<AANANTACityController> Controller;
    TSet<FKey> HeldKeys;
    TArray<FVector> Waypoints;
    TArray<FString> Observations;
    TArray<FString> InputEvents;
    TArray<double> FrameMilliseconds;
    FVector InitialLocation = FVector::ZeroVector;
    FVector LastLocation = FVector::ZeroVector;
    FVector MotionOrigin = FVector::ZeroVector;
    ECityStreamingPhase Phase = ECityStreamingPhase::WaitReady;
    double StartTime = 0;
    double Now = 0;
    double PhaseStart = 0;
    double LastFrameTime = 0;
    double MotionTime = 0;
    double SettleStart = 0;
    double AirborneStart = 0;
    double PathDistance = 0;
    double PlannedDistance = 0;
    double GroundChecks = 0;
    double SprintSpeed = 0;
    double WalkSpeed = 0;
    int32 Waypoint = 0;
    int32 CaptureIndex = 0;
    int32 StreamingEndpoints = 0;
    int32 ExitFrames = 0;
    bool bFinished = false;
    bool bPassed = false;
};
