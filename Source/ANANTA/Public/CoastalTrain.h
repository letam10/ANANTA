#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoastalTrain.generated.h"

class UStaticMeshComponent;

UCLASS()
class ANANTA_API ACoastalTrain : public AActor
{
    GENERATED_BODY()

public:
    ACoastalTrain();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Direction = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float RouteHalfLength = 17500;

protected:
    virtual void Tick(float DeltaSeconds) override;

private:
    float Dwell = 0;
    bool bStoppedAtStation = false;
};
