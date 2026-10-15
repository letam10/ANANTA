#pragma once

#include "CoreMinimal.h"
#include "CoastalTransitTypes.h"
#include "GameFramework/Actor.h"
#include "CoastalTrain.generated.h"

class ACoastalCharacter;
class AController;
class UStaticMeshComponent;

UCLASS()
class ANANTA_API ACoastalTrain : public AActor
{
    GENERATED_BODY()

public:
    ACoastalTrain();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Transit|Route")
    float Direction = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Transit|Route")
    float RouteHalfLength = 17500;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Transit|Signal")
    ECoastalTrainSignalState SignalState = ECoastalTrainSignalState::Clear;

    UPROPERTY(BlueprintReadOnly, Category = "Transit|State")
    ECoastalTrainState TrainState = ECoastalTrainState::Running;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Transit|Station")
    FVector StationLocation = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Transit|Station")
    float StationRadius = 250.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Transit|Station")
    float StationDwellSeconds = 6.f;

    UFUNCTION(BlueprintCallable, Category = "Transit|Signal")
    void SetSignalState(ECoastalTrainSignalState NewState);

    UFUNCTION(BlueprintCallable, Category = "Transit|Passenger")
    bool Board(ACoastalCharacter* Character);

    UFUNCTION(BlueprintCallable, Category = "Transit|Passenger")
    bool Alight();

    UFUNCTION(BlueprintCallable, Category = "Transit|QA")
    void HoldAtStationForBoarding();

    UFUNCTION(BlueprintPure, Category = "Transit|Passenger")
    int32 GetBoardingCount() const { return BoardingCount; }

    UFUNCTION(BlueprintPure, Category = "Transit|Passenger")
    int32 GetAlightingCount() const { return AlightingCount; }

    UFUNCTION(BlueprintPure, Category = "Transit|State")
    bool IsStopped() const { return TrainState != ECoastalTrainState::Running; }

    UFUNCTION(BlueprintPure, Category = "Transit|State")
    ECoastalTrainState GetTrainState() const { return TrainState; }

    UFUNCTION(BlueprintPure, Category = "Transit|State")
    FString GetBlockedReason() const { return BlockedReason; }

protected:
    virtual void Tick(float DeltaSeconds) override;

private:
    UPROPERTY()
    TObjectPtr<ACoastalCharacter> Passenger;

    UPROPERTY()
    TObjectPtr<AController> PassengerController;

    float Dwell = 0;
    bool bStoppedAtStation = false;
    int32 BoardingCount = 0;
    int32 AlightingCount = 0;
    FString BlockedReason;

    bool IsAtStation(const FVector& Location) const;
    void SetBlocked(const FString& Reason);
};
