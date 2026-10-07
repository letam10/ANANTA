#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ANANTAFragmentPickup.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class UPrimitiveComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FANANTAFragmentCollected, FName, FragmentId);

UCLASS(Blueprintable)
class ANANTA_API AANANTAFragmentPickup : public AActor
{
    GENERATED_BODY()

public:
    AANANTAFragmentPickup();

    UFUNCTION(BlueprintCallable, Category = "ANANTA|Fragments")
    bool Collect(AActor* Collector);

    UFUNCTION(BlueprintPure, Category = "ANANTA|Fragments")
    bool IsCollected() const { return bCollected; }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ANANTA|Fragments")
    FName FragmentId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ANANTA|Fragments")
    bool bDestroyOnCollect;

    UPROPERTY(BlueprintAssignable, Category = "ANANTA|Fragments")
    FANANTAFragmentCollected OnFragmentCollected;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ANANTA|Components")
    TObjectPtr<UStaticMeshComponent> FragmentMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ANANTA|Components")
    TObjectPtr<UBoxComponent> CollectionTrigger;

protected:
    virtual void BeginPlay() override;

private:
    UFUNCTION()
    void HandleTriggerBeginOverlap(
        UPrimitiveComponent* OverlappedComponent,
        AActor* OtherActor,
        UPrimitiveComponent* OtherComponent,
        int32 OtherBodyIndex,
        bool bFromSweep,
        const FHitResult& SweepResult);

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "ANANTA|Fragments", meta = (AllowPrivateAccess = "true"))
    bool bCollected;
};
