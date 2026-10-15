#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityPersistenceCheckSubsystem.generated.h"

class UANANTACitySubsystem;
class UANANTACitySave;

UCLASS()
class ANANTA_API UCityPersistenceCheckSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;

private:
    UANANTACitySubsystem* State() const;
    FString EvidenceDirectory() const;
    FString Snapshot(const UANANTACitySave* Save) const;
    bool StartRun();
    bool ExecuteCheck();
    bool ExecuteReload();
    bool ReadCheckpoint();
    bool WriteCheckpoint(const UANANTACitySave* Save) const;
    bool ReadSlotSnapshot(const FString& Slot, FString& OutSnapshot) const;
    bool WriteEvidence(const FString& FileName, const FString& Body) const;
    void Finish(bool bSuccess, const FString& Detail);

    FString ExpectedSnapshot;
    FTransform ExpectedVehicleTransform;
    uint32 PreviousProcessId = 0;
    int32 ExitFrames = 0;
    double StartedAt = 0;
    bool bReload = false;
    bool bStarted = false;
    bool bFinished = false;
    bool bPassed = false;
    bool bEvidenceWritten = false;
};
