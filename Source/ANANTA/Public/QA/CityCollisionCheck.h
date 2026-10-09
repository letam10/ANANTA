#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityCollisionCheck.generated.h"

UCLASS()
class ANANTA_API UCityCollisionCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    void Finish(bool bSuccess, const TCHAR* Reason);
    double StartedAt = 0;
    double LegStartedAt = 0;
    int32 Leg = 0;
    bool bPlaced = false;
    bool bWalking = false;
    bool bFinished = false;
};
