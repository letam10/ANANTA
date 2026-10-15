#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoastalInteractable.generated.h"

class UStaticMeshComponent;

UCLASS()
class ANANTA_API ACoastalInteractable : public AActor
{
    GENERATED_BODY()

public:
    ACoastalInteractable();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString ActionName = TEXT("Inspect");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString Message = TEXT("Welcome to the coastal district.");

    // 0: dịch vụ, 1: cửa, 2: NPC, 3: vật phẩm, 4: thang máy, 5: prop nhỏ.
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Kind = 0;

    // Lịch nhẹ cho cư dân (Kind = 2), di chuyển quanh điểm neo.
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bScheduleEnabled = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float ScheduleRadius = 120.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float ScheduleSpeed = 0.65f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FVector Destination = FVector::ZeroVector;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly)
    bool bUsed = false;

    UFUNCTION(BlueprintCallable)
    FString Use();

private:
    FRotator ClosedRotation;
    FVector ScheduleOrigin;
    float SchedulePhase = 0.f;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
};
