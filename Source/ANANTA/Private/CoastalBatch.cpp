#include "CoastalBatch.h"

#include "Components/HierarchicalInstancedStaticMeshComponent.h"

ACoastalBatch::ACoastalBatch()
{
    PrimaryActorTick.bCanEverTick = false;
    Instances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("Instances"));
    RootComponent = Instances;
    Instances->SetMobility(EComponentMobility::Static);
    Instances->SetCollisionProfileName(TEXT("BlockAll"));
}
