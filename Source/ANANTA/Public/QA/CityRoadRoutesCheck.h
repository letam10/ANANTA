#pragma once

#include "CoreMinimal.h"
#include "City/Mobility/CityMobilityData.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityRoadRoutesCheck.generated.h"

class ACityRouteVehicle;
class ACityTransportManager;
class UWorldPartitionStreamingSourceComponent;

struct FCityRoadProbe
{
    TWeakObjectPtr<ACityRouteVehicle> Vehicle;
    FVector Previous = FVector::ZeroVector;
    FString Status = TEXT("PENDING");
    FString Reason;
    FString LastBlocker;
    double LastProgressAt = 0;
    double Travel = 0;
    double Elapsed = 0;
    double StartDistance = 0;
    double MaxDeviation = 0;
    double MaxFloorGap = 0;
    double OriginHeight = 0;
    double SideTravel[4] = {};
    int32 InitialPoint = 0;
    int32 Boarded = 0;
    int32 Alighted = 0;
    int32 BoardedMask = 0;
    int32 AlightedMask = 0;
    int32 PointMask = 0;
    bool bReturned = false;
};

struct FCityRoadResult
{
    FString Kind;
    ECityTransportKind TransportKind = ECityTransportKind::Coach;
    FCityTransportRoute Route;
    TArray<FCityRoadProbe> Probes;
};

UCLASS()
class ANANTA_API UCityRoadRoutesCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    void SelectRegion();
    bool HasUnexpectedFleet() const;
    void SuppressManager(AActor* Actor);
    bool PrepareStreaming();
    void SpawnVehicles();
    void Observe(FCityRoadResult& Result, FCityRoadProbe& Probe, double Now);
    void Finish(const FString& Reason);
    void Cleanup();
    TArray<FCityRoadResult> Results;
    TArray<TWeakObjectPtr<ACityTransportManager>> PausedManagers;
    TWeakObjectPtr<AActor> Observer;
    TWeakObjectPtr<AActor> PreviousView;
    TWeakObjectPtr<UWorldPartitionStreamingSourceComponent> StreamingSource;
    FDelegateHandle SpawnHandle;
    FString Region = TEXT("Core");
    FVector SourcePlayerLocation = FVector::ZeroVector;
    FVector ObserverLocation = FVector(12000, 0, 2000);
    bool bValidRegion = true;
    double StartedAt = 0;
    double ReadyAt = 0;
    double StableAt = 0;
    bool bFinished = false;
    bool bPassed = false;
    int32 ExitFrames = 0;
};
