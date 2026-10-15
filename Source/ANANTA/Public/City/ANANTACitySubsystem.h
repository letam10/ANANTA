#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "City/ANANTACityState.h"
#include "ANANTACitySubsystem.generated.h"

UCLASS()
class ANANTA_API UANANTACitySubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintPure)
    ECityMissionStage GetMissionStage() const { return Progress->Mission.Stage; }

    UFUNCTION(BlueprintPure)
    FString GetObjectiveText() const;

    UFUNCTION(BlueprintCallable)
    bool TryInteract(FName Id, ECityInteractionKind Kind);

    UFUNCTION(BlueprintCallable)
    bool RegisterEnemyDefeated(FName Id);

    UFUNCTION(BlueprintCallable)
    bool SaveProgress();

    UFUNCTION(BlueprintCallable)
    bool LoadProgress();

    const FCityMissionState& GetMission() const { return Progress->Mission; }
    UANANTACitySave* GetProgress() const { return Progress; }
    bool RegisterLegacyFragment(FName Id);
    bool HasLegacyFragment(FName Id) const;
    bool TryUseService(FName Id, ECityServiceKind Kind, const FString& Description);
    const FCityServiceState& GetServices() const { return Progress->Services; }
    FString GetServiceSummary() const;
    FString ServiceMessage;
    bool IsUsingQASlot() const { return bUseQASlot; }
    const FString& GetSaveSlotName() const { return SaveSlot; }
    uint32 GetSaveAttemptCount() const { return SaveAttemptCount; }
    uint32 GetSuccessfulSaveCount() const { return SuccessfulSaveCount; }
    FString SaveStatus;

private:
    UPROPERTY()
    TObjectPtr<UANANTACitySave> Progress;

    FString SaveSlot = TEXT("ANANTA_City_v1");
    FString BackupSlot = TEXT("ANANTA_City_v1_Backup");
    uint32 SaveAttemptCount = 0;
    uint32 SuccessfulSaveCount = 0;
    bool bUseQASlot = false;
};
