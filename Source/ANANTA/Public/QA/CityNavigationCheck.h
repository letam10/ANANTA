#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityNavigationCheck.generated.h"

UCLASS()
class ANANTA_API UCityNavigationCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    double StartTime = 0;
    double LastCheck = 0;
    bool bFinished = false;
};
