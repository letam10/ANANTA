#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "ANANTACityGameMode.generated.h"

UCLASS()
class ANANTA_API AANANTACityGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AANANTACityGameMode();
    virtual void BeginPlay() override;
};
