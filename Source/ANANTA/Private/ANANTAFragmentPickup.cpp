#include "ANANTAFragmentPickup.h"

#include "ANANTAGameInstance.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"

AANANTAFragmentPickup::AANANTAFragmentPickup()
    : FragmentId(TEXT("Fragment_001"))
    , bDestroyOnCollect(false)
    , bCollected(false)
{
    PrimaryActorTick.bCanEverTick = false;

    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

    FragmentMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FragmentMesh"));
    FragmentMesh->SetupAttachment(RootComponent);
    FragmentMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    CollectionTrigger = CreateDefaultSubobject<UBoxComponent>(TEXT("CollectionTrigger"));
    CollectionTrigger->SetupAttachment(RootComponent);
    CollectionTrigger->SetBoxExtent(FVector(120.0f, 120.0f, 160.0f));
    CollectionTrigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    CollectionTrigger->SetCollisionResponseToAllChannels(ECR_Ignore);
    CollectionTrigger->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    CollectionTrigger->SetGenerateOverlapEvents(true);
}

void AANANTAFragmentPickup::BeginPlay()
{
    Super::BeginPlay();
    CollectionTrigger->OnComponentBeginOverlap.AddDynamic(this, &AANANTAFragmentPickup::HandleTriggerBeginOverlap);
}

bool AANANTAFragmentPickup::Collect(AActor* Collector)
{
    if (bCollected || !Collector || !GetWorld())
    {
        return false;
    }

    if (!Collector->IsA<ACharacter>())
    {
        return false;
    }

    UANANTAGameInstance* GameInstance = GetWorld()->GetGameInstance<UANANTAGameInstance>();
    if (!GameInstance || !GameInstance->RegisterFragment(FragmentId))
    {
        return false;
    }

    bCollected = true;
    OnFragmentCollected.Broadcast(FragmentId);

    if (bDestroyOnCollect)
    {
        Destroy();
    }

    return true;
}

void AANANTAFragmentPickup::HandleTriggerBeginOverlap(
    UPrimitiveComponent* OverlappedComponent,
    AActor* OtherActor,
    UPrimitiveComponent* OtherComponent,
    int32 OtherBodyIndex,
    bool bFromSweep,
    const FHitResult& SweepResult)
{
    Collect(OtherActor);
}
