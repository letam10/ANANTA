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

    // 0: dịch vụ, 1: cửa, 2: NPC, 3: vật phẩm, 4: thang máy.
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Kind = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FVector Destination = FVector::ZeroVector;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly)
    bool bUsed = false;

    UFUNCTION(BlueprintCallable)
    FString Use();

private:
    FRotator ClosedRotation;
    virtual void BeginPlay() override;
};
