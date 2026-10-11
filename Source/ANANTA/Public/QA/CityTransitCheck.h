#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityTransitCheck.generated.h"

class AANANTACityController;
class ACityRouteVehicle;

UCLASS()
class ANANTA_API UCityTransitCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;
    virtual void Deinitialize() override;

private:
    void Finish(bool bSuccess, const FString& Detail);
    void SetWalking(bool bWalk);
    TWeakObjectPtr<AANANTACityController> Controller;
    TWeakObjectPtr<ACityRouteVehicle> Vehicle;
    double Start = 0;
    FVector FirstVehiclePosition = FVector::ZeroVector;
    bool bWalking = false;
    bool bDone = false;
    bool bPass = false;
    int32 ExitFrames = 0;
    int32 GroundChecks = 0;
};
