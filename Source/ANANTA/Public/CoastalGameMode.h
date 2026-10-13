#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "CoastalGameMode.generated.h"

UCLASS()
class ANANTA_API ACoastalGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ACoastalGameMode();

protected:
    virtual void BeginPlay() override;
};
