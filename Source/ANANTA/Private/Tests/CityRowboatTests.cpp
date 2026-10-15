#if WITH_DEV_AUTOMATION_TESTS
#include "City/Mobility/CityRowboat.h"
#include "City/Mobility/CityMobilityData.h"
#include "City/CityWorldBounds.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Misc/AutomationTest.h"

namespace
{
    struct FBoatWorld
    {
        UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);

        ~FBoatWorld()
        {
            World->DestroyWorld(false);
        }

        void Dock()
        {
            auto* Actor = World->SpawnActor<AActor>();
            auto* Shape = NewObject<UBoxComponent>(Actor);
            Actor->SetRootComponent(Shape);
            Shape->SetBoxExtent(FVector(680, 300, 25));
            Shape->SetCollisionProfileName(TEXT("BlockAll"));
            Shape->RegisterComponent();
            Actor->SetActorLocation(FVector(128620, -137000, -10));
        }

        ACityRowboat* Boat(const FVector& Location, const float Yaw)
        {
            FActorSpawnParameters Params;
            Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
            return World->SpawnActor<ACityRowboat>(Location, FRotator(0, Yaw, 0), Params);
        }
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityBoatPierTest, "ANANTA.City.Rowboat.CannotSlideUnderPier",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityBoatPierTest::RunTest(const FString& Parameters)
{
    FBoatWorld Fixture;
    Fixture.Dock();
    const FVector Start(129540, -137000, CityMobility::WaterLevel);
    auto* Legacy = Fixture.Boat(Start, 180);
    Legacy->CollisionBody->SetBoxExtent(FVector(190, 70, 35));
    for (int32 Frame = 0; Frame < 240; ++Frame)
    {
        Legacy->Drive(1, 0, false, .05f);
    }
    TestTrue(TEXT("Reproduce low hull passing below authored pier thickness"), Legacy->GetActorLocation().X < 129300);
    Legacy->Destroy();
    auto* Fixed = Fixture.Boat(Start, 180);
    for (int32 Frame = 0; Frame < 240; ++Frame)
    {
        Fixed->Drive(1, 0, false, .05f);
    }
    TestTrue(TEXT("Full hull stops before dock"), Fixed->GetActorLocation().X >= 129489);
    TestTrue(TEXT("Boat stays at water level"), FMath::IsNearlyEqual(Fixed->GetActorLocation().Z, -120.0));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityBoatExitTest, "ANANTA.City.Rowboat.ExitRequiresDryDock",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityBoatExitTest::RunTest(const FString& Parameters)
{
    FBoatWorld Fixture;
    Fixture.Dock();
    auto* Hero = Fixture.World->SpawnActor<ACharacter>();
    Hero->GetCapsuleComponent()->SetCapsuleSize(38, 92);
    Hero->SetActorEnableCollision(false);
    auto* Boat = Fixture.Boat(FVector(129440, -137000, -120), 90);
    FVector Exit;
    TestTrue(TEXT("Dock beside rowboat supports capsule"), Boat->FindSafeExit(Hero, Exit));
    TestTrue(TEXT("Exit rests above pier surface"), FMath::IsNearlyEqual(Exit.Z, 110.0));
    Boat->SetActorLocation(FVector(150000, -130000, -120));
    TestFalse(TEXT("No teleport down to seabed or into open water"), Boat->FindSafeExit(Hero, Exit));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityBoatEdgeTest, "ANANTA.City.Rowboat.MapBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityBoatEdgeTest::RunTest(const FString& Parameters)
{
    FBoatWorld Fixture;
    auto* Boat = Fixture.Boat(FVector(CityWorldBounds::RoadExtent - 600, -130000, -120), 0);
    for (int32 Frame = 0; Frame < 240; ++Frame)
    {
        Boat->Drive(1, 0, false, .05f);
    }
    TestTrue(TEXT("Rowing cannot leave playable city"), Boat->GetActorLocation().X <= CityWorldBounds::RoadExtent - 500);
    TestTrue(TEXT("Boat moved toward boundary"), Boat->GetActorLocation().X > CityWorldBounds::RoadExtent - 600);
    return true;
}
#endif
