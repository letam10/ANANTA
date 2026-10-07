#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ANANTACityCrowd.generated.h"

class UStaticMesh;

UCLASS()
class ANANTA_API AANANTACityCrowd : public AActor
{
    GENERATED_BODY()

public:
    AANANTACityCrowd();
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, meta = (ClampMin = "0", ClampMax = "24"))
    int32 PedestrianLimit = 24;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, meta = (ClampMin = "0", ClampMax = "6"))
    int32 TrafficLimit = 6;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TObjectPtr<UStaticMesh> TrafficMesh;

private:
    void MaintainPopulation(const FVector& Player, bool bTraffic);
    bool MakeRoute(const FVector& Player, bool bTraffic, FVector& Start, FVector& End);

    UPROPERTY()
    TArray<TObjectPtr<AActor>> Pedestrians;

    UPROPERTY()
    TArray<TObjectPtr<AActor>> Traffic;

    FRandomStream Random = FRandomStream(48127);
};
