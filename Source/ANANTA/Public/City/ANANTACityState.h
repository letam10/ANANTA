#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "City/CityServiceState.h"
#include "ANANTACityState.generated.h"

UENUM(BlueprintType)
enum class ECityMissionStage : uint8
{
    NotStarted,
    Investigating,
    Combat,
    ReturnToGiver,
    Completed
};

UENUM(BlueprintType)
enum class ECityInteractionKind : uint8
{
    Giver,
    Clue,
    Fragment
};

USTRUCT(BlueprintType)
struct ANANTA_API FCityMissionState
{
    GENERATED_BODY()

    UPROPERTY(SaveGame)
    ECityMissionStage Stage = ECityMissionStage::NotStarted;

    UPROPERTY(SaveGame)
    TSet<FName> Clues;

    UPROPERTY(SaveGame)
    TSet<FName> DefeatedEnemies;

    UPROPERTY(SaveGame)
    bool bFragmentCollected = false;

    UPROPERTY(SaveGame)
    int32 RewardCount = 0;

    bool Interact(FName Id, ECityInteractionKind Kind);
    bool Defeat(FName Id);
    bool IsValid() const;
    static bool IsClue(FName Id);
    static bool IsEnemy(FName Id);
};

UCLASS()
class ANANTA_API UANANTACitySave : public USaveGame
{
    GENERATED_BODY()

public:
    UPROPERTY(SaveGame)
    int32 SchemaVersion = 1;

    UPROPERTY(SaveGame)
    FCityMissionState Mission;

    UPROPERTY(SaveGame)
    FCityServiceState Services;

    UPROPERTY(SaveGame)
    FTransform PlayerTransform = FTransform(FRotator(0, 90, 0), FVector(-25000, 1500, 120));

    UPROPERTY(SaveGame)
    FTransform CarTransform = FTransform(FVector(-22000, 500, 70));

    UPROPERTY(SaveGame)
    bool bHasPlayerTransform = false;

    UPROPERTY(SaveGame)
    bool bHasCarTransform = false;

    UPROPERTY(SaveGame)
    TSet<FName> LegacyFragments;

    bool IsValidSave() const;
};
