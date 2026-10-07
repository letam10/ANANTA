#pragma once

#include "CoreMinimal.h"
#include "City/ANANTACityInteractable.h"
#include "City/CityServiceState.h"
#include "CityServiceInteractable.generated.h"

UCLASS()
class ANANTA_API ACityServiceInteractable : public AANANTACityInteractable
{
    GENERATED_BODY()

public:
    virtual bool IsAvailable() const override;
    virtual bool Interact(APawn* Player) override;
    virtual FString GetPrompt() const override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "City Service")
    ECityServiceKind ServiceKind = ECityServiceKind::Read;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "City Service")
    FString DisplayName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "City Service", meta = (MultiLine = true))
    FString Description;

private:
    bool CanUseService(const APawn* Player) const;
};
