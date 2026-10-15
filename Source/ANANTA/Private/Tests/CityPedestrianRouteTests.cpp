#if WITH_DEV_AUTOMATION_TESTS
#include "City/ANANTACityCrowd.h"
#include "Components/BoxComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityPedestrianRouteTest, "ANANTA.City.Collision.PedestrianRouteHasTravel",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityPedestrianRouteTest::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    AActor* Floor = World->SpawnActor<AActor>();
    auto* Box = NewObject<UBoxComponent>(Floor);
    Floor->SetRootComponent(Box);
    Box->SetBoxExtent(FVector(175000, 175000, 50));
    Box->SetCollisionProfileName(TEXT("BlockAll"));
    Box->RegisterComponent();
    Floor->SetActorLocation(FVector(0, 0, -50));
    auto* Crowd = World->SpawnActor<AANANTACityCrowd>();
    int32 Accepted = 0;
    int32 Degenerate = 0;
    for (const FVector Player : {FVector(46400, 1100, 110), FVector(-46400, -1100, 110),
        FVector(1100, 166400, 110), FVector(-1100, -166400, 110)})
    {
        for (int32 Seed = 0; Seed < 128; ++Seed)
        {
            Crowd->Random.Initialize(Seed);
            FVector Start;
            FVector End;
            if (Crowd->MakeRoute(Player, false, Start, End))
            {
                ++Accepted;
                Degenerate += FVector::Dist2D(Start, End) < 200 ? 1 : 0;
            }
        }
    }
    TestTrue(TEXT("Fixture exercised accepted sidewalk routes"), Accepted > 100);
    TestEqual(TEXT("Clamping near block ends must not create stationary pedestrians"), Degenerate, 0);
    World->DestroyWorld(false);
    return true;
}
#endif
