#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityFleetCheck.generated.h"

class AActor;
class ACityRouteVehicle;
class ACityTransitPassenger;

struct FCityFleetFixture
{
    TWeakObjectPtr<ACityRouteVehicle> Vehicle;
    TWeakObjectPtr<ACityTransitPassenger> Passenger;
    TWeakObjectPtr<AActor> DoorBlocker;
    TWeakObjectPtr<AActor> LaneBlocker;
    FVector Start = FVector::ZeroVector;
    FVector Extent = FVector::ZeroVector;
    FVector PassengerStart = FVector::ZeroVector;
    FVector AlightStart = FVector::ZeroVector;
    FString Name;
    float Elapsed = 0;
    float BlockedElapsed = 0;
    float Travel = 0;
    int32 WalkingChecks = 0;
    int32 Stage = 0;
    bool bApproached = false;
    bool bSeated = false;
    bool bAlighted = false;
};

UCLASS()
class ANANTA_API UCityFleetCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;
    virtual void Deinitialize() override;

private:
    bool BuildFixtures();
    AActor* AddBox(const FVector& Location, const FVector& Extent);
    bool ObservePassenger(FCityFleetFixture& Fixture);
    bool UpdateFixture(FCityFleetFixture& Fixture, float DeltaTime);
    void Finish(bool bSuccess, const FString& Detail);
    void Cleanup();
    TArray<FCityFleetFixture> Fixtures;
    TArray<TWeakObjectPtr<AActor>> Geometry;
    double StartedAt = 0;
    FString Evidence;
    bool bStarted = false;
    bool bFinished = false;
    bool bPassed = false;
    int32 ExitFrames = 0;
};
