#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityRailCheck.generated.h"

class AActor;
class ACityRailShuttle;
class UWorldPartitionStreamingSourceComponent;

struct FCityRailCheckResult
{
    TWeakObjectPtr<ACityRailShuttle> Train;
    FVector Start = FVector::ZeroVector;
    FVector Previous = FVector::ZeroVector;
    double Travel = 0;
    double MaximumDistance = 0;
    int32 BoardedAtStart = 0;
    int32 AlightedAtStart = 0;
    bool bStartedAtStop = false;
    bool bPassed = false;
};

UCLASS()
class ANANTA_API UCityRailCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    void Finish(bool bPassed, const FString& Reason);
    TWeakObjectPtr<AActor> Observer;
    TWeakObjectPtr<UWorldPartitionStreamingSourceComponent> Source;
    TArray<FCityRailCheckResult> Results;
    double StartedAt = 0;
    double ReadyAt = 0;
    double StableAt = 0;
    bool bFinished = false;
};
