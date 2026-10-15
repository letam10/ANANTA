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

USTRUCT(BlueprintType)
struct ANANTA_API FCityInteractionState
{
    GENERATED_BODY()

    UPROPERTY(SaveGame)
    TSet<FName> OpenedDoorIds;

    UPROPERTY(SaveGame)
    TSet<FName> UsedPropIds;

    UPROPERTY(SaveGame)
    TSet<FName> VisitedDistrictIds;

    bool IsValid() const;
};

USTRUCT(BlueprintType)
struct ANANTA_API FCityNpcScheduleState
{
    GENERATED_BODY()

    UPROPERTY(SaveGame)
    TMap<FName, float> PhaseByNpcId;

    UPROPERTY(SaveGame)
    TSet<FName> ActiveNpcIds;

    bool IsValid() const;
};

USTRUCT(BlueprintType)
struct ANANTA_API FCityVehicleTransitState
{
    GENERATED_BODY()

    UPROPERTY(SaveGame)
    TMap<FName, FTransform> VehicleTransforms;

    UPROPERTY(SaveGame)
    TMap<FName, int32> RouteStopById;

    UPROPERTY(SaveGame)
    TSet<FName> BoardedTransitIds;

    UPROPERTY(SaveGame)
    TMap<FName, uint8> SignalStateById;

    bool IsValid() const;
};

USTRUCT(BlueprintType)
struct ANANTA_API FCityEconomyState
{
    GENERATED_BODY()

    UPROPERTY(SaveGame)
    TMap<FName, int32> Inventory;

    UPROPERTY(SaveGame)
    int32 CityTokens = 0;

    bool IsValid() const;
};

USTRUCT(BlueprintType)
struct ANANTA_API FCityDayNightState
{
    GENERATED_BODY()

    UPROPERTY(SaveGame)
    int32 DayIndex = 0;

    UPROPERTY(SaveGame)
    float TimeHours = 12.f;

    UPROPERTY(SaveGame)
    FName LightingLayer = TEXT("Day");

    bool IsValid() const;
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

    UPROPERTY(SaveGame)
    FCityInteractionState InteractionState;

    UPROPERTY(SaveGame)
    FCityNpcScheduleState NpcSchedule;

    UPROPERTY(SaveGame)
    FCityVehicleTransitState VehicleTransit;

    UPROPERTY(SaveGame)
    FCityEconomyState Economy;

    UPROPERTY(SaveGame)
    FCityDayNightState DayNight;

    bool IsValidSave() const;
    bool MigrateToCurrentSchema();
    static int32 GetCurrentSchemaVersion() { return 2; }
};
