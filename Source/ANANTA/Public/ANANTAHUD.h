#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "ANANTAHUD.generated.h"

class UUserWidget;

/**
 * Owns the persistent in-game HUD for ANANTA.
 *
 * The widget class is resolved from the Nova HUD Widget Blueprint by default,
 * while remaining editable from a GameMode or Blueprint override.
 */
UCLASS(Blueprintable)
class ANANTA_API AANANTAHUD : public AHUD
{
    GENERATED_BODY()

public:
    AANANTAHUD();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ANANTA|UI")
    TSubclassOf<UUserWidget> NovaHUDClass;

    UPROPERTY(Transient, BlueprintReadOnly, Category = "ANANTA|UI")
    TObjectPtr<UUserWidget> NovaHUDWidget;
};
