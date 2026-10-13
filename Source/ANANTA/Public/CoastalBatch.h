#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoastalBatch.generated.h"

class UHierarchicalInstancedStaticMeshComponent;

UCLASS()
class ANANTA_API ACoastalBatch : public AActor
{
    GENERATED_BODY()

public:
    ACoastalBatch();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UHierarchicalInstancedStaticMeshComponent> Instances;
};
