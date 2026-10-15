#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityHarborCheck.generated.h"

class AActor;
class ACityRouteVehicle;
class ACityTransportManager;
class UWorldPartitionStreamingSourceComponent;

struct FCityHarborResult
{
    TWeakObjectPtr<ACityRouteVehicle> Vehicle;
    FVector Dock = FVector::ZeroVector;
    FVector Previous = FVector::ZeroVector;
    FString Kind;
    FString Status = TEXT("PENDING");
    FString Reason;
    FString LastBlocker;
    double MaximumDistance = 0;
    double TravelDistance = 0;
    double DockDistance = 0;
    double MinimumWaterline = 0;
    double OriginHeight = 0;
    double LastProgressAt = 0;
    double Elapsed = 0;
    int32 Boarded = 0;
    int32 Alighted = 0;
    bool bOutbound = false;
    bool bReturned = false;
};

UCLASS()
class ANANTA_API UCityHarborCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    void SuppressManager(AActor* Actor);
    bool PrepareStreaming();
    void SpawnVessels();
    void Observe(FCityHarborResult& Result, double Now);
    void Finish(const FString& Reason);
    void Cleanup();
    TArray<FCityHarborResult> Results;
    TArray<TWeakObjectPtr<ACityTransportManager>> PausedManagers;
    TWeakObjectPtr<AActor> Observer;
    TWeakObjectPtr<AActor> PreviousView;
    TWeakObjectPtr<UWorldPartitionStreamingSourceComponent> StreamingSource;
    FDelegateHandle SpawnHandle;
    double StartedAt = 0;
    double ReadyAt = 0;
    double StableAt = 0;
    bool bFinished = false;
    bool bPassed = false;
    int32 ExitFrames = 0;
};
