#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "ANANTACityHUD.generated.h"

UCLASS()
class ANANTA_API AANANTACityHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;
};
