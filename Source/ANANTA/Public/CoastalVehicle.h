#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "CoastalTransitTypes.h"
#include "CoastalVehicle.generated.h"

class ACoastalCharacter;
class UBoxComponent;
class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;

UCLASS()
class ANANTA_API ACoastalVehicle : public APawn
{
    GENERATED_BODY()

public:
    ACoastalVehicle();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UBoxComponent> Collision;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit")
    bool bBoat = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit")
    FString VehicleName = TEXT("Vehicle");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit")
    ECoastalVehicleType VehicleType = ECoastalVehicleType::Road;

    UPROPERTY(BlueprintReadOnly, Category="Transit")
    ECoastalVehicleState VehicleState = ECoastalVehicleState::Idle;

    UPROPERTY(BlueprintReadOnly, Category="Transit")
    ECoastalTransitFailureReason FailureReason = ECoastalTransitFailureReason::None;

    UPROPERTY(BlueprintReadOnly, Category="Transit")
    FString FailureReasonText;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit|Route")
    bool bRouteBounded = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit|Route")
    FVector RouteMinBounds = FVector(-100000, -100000, -100000);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit|Route")
    FVector RouteMaxBounds = FVector(100000, 100000, 100000);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit|Stops")
    bool bStopEnabled = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit|Stops")
    FVector StopLocation = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit|Stops")
    float StopRadius = 180;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Transit|Stops")
    float StopDwellSeconds = 2;

    UFUNCTION(BlueprintCallable)
    bool Board(ACoastalCharacter* Character);

    UFUNCTION(BlueprintCallable)
    bool Leave();

    UFUNCTION(BlueprintCallable)
    void Drive(float Throttle, float Steering);

    UFUNCTION(BlueprintPure)
    bool IsOccupied() const { return Driver != nullptr; }

    UFUNCTION(BlueprintPure)
    float GetSpeed() const { return Speed; }

    UFUNCTION(BlueprintPure)
    ECoastalVehicleType GetVehicleType() const { return VehicleType; }

    UFUNCTION(BlueprintPure)
    ECoastalVehicleState GetVehicleState() const { return VehicleState; }

    UFUNCTION(BlueprintPure)
    ECoastalTransitFailureReason GetFailureReason() const { return FailureReason; }

    UFUNCTION(BlueprintPure)
    FString GetFailureReasonText() const { return FailureReasonText; }

    UFUNCTION(BlueprintPure)
    FString GetBlockedReason() const { return FailureReasonText; }

    UFUNCTION(BlueprintPure)
    float GetRowingFeedback() const { return RowingFeedback; }

    UFUNCTION(BlueprintCallable)
    void SetVehicleType(ECoastalVehicleType NewType);

    UFUNCTION(BlueprintCallable)
    void SetRouteBounds(FVector Minimum, FVector Maximum);

    UFUNCTION(BlueprintCallable)
    void ClearRouteBounds();

    UFUNCTION(BlueprintCallable)
    void SetStop(FVector Location, float Radius, float DwellSeconds);

    UFUNCTION(BlueprintCallable)
    void ClearStop();

    UFUNCTION(BlueprintPure)
    bool IsAtStop() const;

protected:
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;

private:
    UPROPERTY()
    TObjectPtr<ACoastalCharacter> Driver;

    UPROPERTY()
    TObjectPtr<USpringArmComponent> Arm;

    UPROPERTY()
    TObjectPtr<UCameraComponent> Camera;

    float Speed = 0;
    float ThrottleInput = 0;
    float SteeringInput = 0;
    float StopDwellRemaining = 0;
    float RowingFeedback = 0;
    bool bReportedBlock = false;

    void Forward(float Value);
    void Right(float Value);
    void ExitInput();
    bool TryFindExit(FVector& Exit) const;
    void SetFailure(ECoastalTransitFailureReason Reason, const FString& Text);
    void ClearFailure();
    ECoastalVehicleType GetEffectiveVehicleType() const;
    float GetMaximumSpeed() const;
};
