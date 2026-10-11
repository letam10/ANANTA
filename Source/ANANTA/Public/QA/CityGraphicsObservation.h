#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityGraphicsObservation.generated.h"

UCLASS()
class ANANTA_API UCityGraphicsObservation : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;

private:
    void RecordConfiguration();
    TArray<FString> Rows;
    double LastTime = 0;
    double FirstTime = 0;
    bool bConfigured = false;
    bool bProfileRequested = false;
};
