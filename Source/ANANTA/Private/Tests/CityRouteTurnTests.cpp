#if WITH_DEV_AUTOMATION_TESTS
#include "City/Mobility/CityRouteVehicle.h"
#include "Components/BoxComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityCoachCornerTest, "ANANTA.City.Collision.CoachTurnsPastCurb",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityCoachCornerTest::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    const auto AddBox = [World](const FVector& Location, const FVector& Extent)
    {
        AActor* Actor = World->SpawnActor<AActor>();
        auto* Box = NewObject<UBoxComponent>(Actor);
        Actor->SetRootComponent(Box);
        Box->SetBoxExtent(Extent);
        Box->SetCollisionProfileName(TEXT("BlockAll"));
        Box->RegisterComponent();
        Actor->SetActorLocation(Location);
    };
    AddBox(FVector(0, 0, -50), FVector(6000, 6000, 50));
    AddBox(FVector(-1950, 1950, 9), FVector(1050, 1050, 9));
    UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr,
        TEXT("/Game/ANANTA/City/Meshes/SM_Coach.SM_Coach"));
    auto* Coach = World->SpawnActor<ACityRouteVehicle>();
    FCityTransportRoute Route;
    Route.Points = {FVector(-3000, 420, 0), FVector(-420, 420, 0), FVector(-420, 3000, 0)};
    const bool bConfigured = Coach->Configure(ECityTransportKind::Coach, Route, Mesh, 0);
    TestTrue(TEXT("Imported coach can start on clear road"), bConfigured);
    if (bConfigured)
    {
        bool bPenetrated = false;
        const FCollisionQueryParams Params(SCENE_QUERY_STAT(CoachCorner), false, Coach);
        const FVector Extent = Mesh->GetBoundingBox().GetExtent() - FVector(1);
        for (int32 Step = 0; Step < 1200 && Coach->GetActorLocation().Y < 1600; ++Step)
        {
            Coach->Tick(1.f / 60);
            bPenetrated |= World->OverlapBlockingTestByChannel(Coach->GetActorLocation(),
                Coach->GetActorQuat(), ECC_WorldDynamic, FCollisionShape::MakeBox(Extent), Params);
        }
        TestFalse(TEXT("Long coach does not penetrate curb while turning"), bPenetrated);
        TestTrue(TEXT("Clear steering continues when forward lookahead meets curb"),
            Coach->GetActorLocation().Y >= 1600);
    }
    World->DestroyWorld(false);
    return true;
}
#endif
