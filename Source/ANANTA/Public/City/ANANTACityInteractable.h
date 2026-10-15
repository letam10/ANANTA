#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "City/ANANTACityState.h"
#include "ANANTACityInteractable.generated.h"

class UStaticMeshComponent;
class UPointLightComponent;

UCLASS()
class ANANTA_API AANANTACityInteractable : public AActor
{
    GENERATED_BODY()

public:
    AANANTACityInteractable();
    virtual void Tick(float DeltaTime) override;
    virtual bool IsAvailable() const;
    virtual bool Interact(APawn* Player);
    virtual FString GetPrompt() const;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FName InteractionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    ECityInteractionKind InteractionKind = ECityInteractionKind::Clue;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> VisualMesh;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPointLightComponent> MarkerLight;
};
