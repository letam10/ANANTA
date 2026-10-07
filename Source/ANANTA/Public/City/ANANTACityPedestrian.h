#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ANANTACityPedestrian.generated.h"

UCLASS()
class ANANTA_API AANANTACityPedestrian : public ACharacter
{
    GENERATED_BODY()

public:
    AANANTACityPedestrian();
    virtual void Tick(float DeltaTime) override;
    FVector Destination;
    FVector Origin;

private:
    float StallTime = 0;
};

UCLASS()
class ANANTA_API AANANTACityTraffic : public AActor
{
    GENERATED_BODY()

public:
    AANANTACityTraffic();
    virtual void Tick(float DeltaTime) override;
    FVector Destination;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<class UStaticMeshComponent> BodyMesh;

private:
    float StallTime = 0;
};
