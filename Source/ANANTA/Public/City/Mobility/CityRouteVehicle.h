#pragma once

#include "CoreMinimal.h"
#include "City/Mobility/CityMobilityData.h"
#include "GameFramework/Actor.h"
#include "CityRouteVehicle.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class UStaticMesh;
class ACityTransitPassenger;

UCLASS()
class ANANTA_API ACityRouteVehicle : public AActor
{
    GENERATED_BODY()

public:
    ACityRouteVehicle();
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    bool Configure(ECityTransportKind InKind, const FCityTransportRoute& InRoute, UStaticMesh* Mesh,
        int32 InitialPoint);
    void RecordBoarding();
    void RecordAlighting();
    int32 GetBoardingCount() const { return BoardingCount; }
    int32 GetAlightingCount() const { return AlightingCount; }
    bool IsStopped() const { return bStopped; }
    ECityTransportKind GetKind() const { return Kind; }
    const FString& GetBlockedReason() const { return BlockedReason; }

private:
    bool PlaceOnSurface(FVector& Position) const;
    bool DoorAndSidewalk(FVector& Door, FVector& Sidewalk) const;
    void ServiceStop(float DeltaTime);
    void MoveAlongRoute(float DeltaTime);

    UPROPERTY()
    TObjectPtr<UBoxComponent> CollisionBody;
    UPROPERTY()
    TObjectPtr<UStaticMeshComponent> BodyMesh;
    UPROPERTY()
    TObjectPtr<ACityTransitPassenger> Passenger;

    FCityTransportRoute Route;
    FString BlockedReason;
    ECityTransportKind Kind = ECityTransportKind::CityBus;
    FVector Extent = FVector(220, 100, 80);
    float OriginHeight = 80;
    float StopElapsed = 0;
    int32 Point = 0;
    int32 BoardingCount = 0;
    int32 AlightingCount = 0;
    bool bStopped = true;
    bool bServiced = false;
    bool bConfigured = false;
};
