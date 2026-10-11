#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CityTransportManager.generated.h"

class ACityRouteVehicle;
class UStaticMesh;

UCLASS()
class ANANTA_API ACityTransportManager : public AActor
{
    GENERATED_BODY()

public:
    ACityTransportManager();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

private:
    UPROPERTY()
    TArray<TObjectPtr<UStaticMesh>> Meshes;
    UPROPERTY()
    TArray<TObjectPtr<ACityRouteVehicle>> Fleet;
};
