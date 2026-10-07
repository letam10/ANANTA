#pragma once

#include "CoreMinimal.h"
#include "CityServiceState.generated.h"

UENUM(BlueprintType)
enum class ECityServiceKind : uint8
{
    Rest,
    Heal,
    Supplies,
    Read
};

USTRUCT(BlueprintType)
struct ANANTA_API FCityServiceState
{
    GENERATED_BODY()

    UPROPERTY(SaveGame, BlueprintReadOnly)
    TSet<FName> VisitedIds;

    UPROPERTY(SaveGame, BlueprintReadOnly)
    TSet<FName> ClaimedSupplyIds;

    UPROPERTY(SaveGame, BlueprintReadOnly)
    int32 SuppliesCount = 0;

    bool Discover(FName Id);
    bool ClaimSupply(FName Id);
    bool IsValid() const;
    static bool IsServiceId(FName Id, ECityServiceKind Kind);
    static bool IsVisitId(FName Id);
};
