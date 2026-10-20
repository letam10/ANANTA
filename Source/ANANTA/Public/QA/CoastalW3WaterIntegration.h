#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CoastalW3WaterIntegration.generated.h"

UCLASS()
class ANANTA_API UCoastalW3WaterIntegration : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    bool ApplyToLoadedWaterActors();

    float RetryElapsed = 0.0f;
    float TotalElapsed = 0.0f;
    bool bApplied = false;
    bool bLoggedFailure = false;
};
