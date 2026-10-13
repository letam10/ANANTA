#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "CoastalHUD.generated.h"

UCLASS()
class ANANTA_API ACoastalHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;

private:
    FString Prompt;
    double NextQuery = 0;
};
