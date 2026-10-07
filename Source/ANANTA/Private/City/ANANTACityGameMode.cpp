#include "City/ANANTACityGameMode.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACityHUD.h"
#include "City/CityStreetLighting.h"
#include "Engine/World.h"

AANANTACityGameMode::AANANTACityGameMode()
{
    DefaultPawnClass = AANANTACityCharacter::StaticClass();
    PlayerControllerClass = AANANTACityController::StaticClass();
    HUDClass = AANANTACityHUD::StaticClass();
}

void AANANTACityGameMode::BeginPlay()
{
    Super::BeginPlay();
    GetWorld()->SpawnActor<ACityStreetLighting>();
}
