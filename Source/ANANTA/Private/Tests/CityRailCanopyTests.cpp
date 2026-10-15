#if WITH_DEV_AUTOMATION_TESTS
#include "City/Mobility/CityRouteVehicle.h"
#include "Components/BoxComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
    struct FRailCanopyWorld
    {
        UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
        const FVector Origin = FVector(12345, -23456, 0);
        TArray<AActor*> Canopy;

        explicit FRailCanopyWorld(const int32 Side)
        {
            AddBox(Origin + FVector(0, 0, 10), FVector(4650, 4600, 10));
            AddBox(Origin + FVector(0, Side * 1370, 60), FVector(4000, 470, 40));
            for (int32 Band = 0; Band < 7; ++Band)
            {
                const float Height = 720 - FMath::Abs(Band - 3) * 45;
                Canopy.Add(AddBox(Origin + FVector(0, Side * 1370 - 480 + Band * 160, Height),
                    FVector(4100, 90, 17.5)));
            }
        }

        ~FRailCanopyWorld()
        {
            World->DestroyWorld(false);
        }

        AActor* AddBox(const FVector& Location, const FVector& Extent)
        {
            AActor* Actor = World->SpawnActor<AActor>();
            auto* Box = NewObject<UBoxComponent>(Actor);
            Actor->SetRootComponent(Box);
            Box->SetBoxExtent(Extent);
            Box->SetCollisionProfileName(TEXT("BlockAll"));
            Box->RegisterComponent();
            Actor->SetActorLocation(Location);
            return Actor;
        }
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityRailCanopyTest, "ANANTA.City.Rail.BoardingUnderStationCanopy",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityRailCanopyTest::RunTest(const FString& Parameters)
{
    UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr,
        TEXT("/Game/ANANTA/City/Meshes/SM_PassengerTrain.SM_PassengerTrain"));
    if (!TestNotNull(TEXT("Imported passenger train exists"), Mesh))
    {
        return false;
    }
    for (const int32 Side : {-1, 1})
    {
        FRailCanopyWorld Fixture(Side);
        const FString Label = FString::Printf(TEXT("Station side %d: "), Side);
        FCityTransportRoute Route;
        Route.bRail = true;
        Route.Points = {Fixture.Origin + FVector(0, Side * 500, 51),
            Fixture.Origin + FVector(Side * 2000, Side * 500, 51)};
        Route.Stops = {0};
        FActorSpawnParameters SpawnParams;
        SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* Train = Fixture.World->SpawnActor<ACityRouteVehicle>(
            FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);
        if (!TestNotNull(Label + TEXT("Train spawned"), Train)
            || !TestTrue(Label + TEXT("Imported train configures on station track"),
                Train->Configure(ECityTransportKind::PassengerTrain, Route, Mesh, 0)))
        {
            continue;
        }
        const float SurfaceZ = Train->GetActorLocation().Z - Train->OriginHeight;
        TestTrue(Label + TEXT("Running surface remains at rail height"), FMath::IsNearlyEqual(SurfaceZ, 51.f));
        const FCollisionQueryParams Query(SCENE_QUERY_STAT(RailCanopyRegression), false, Train);
        const FCollisionObjectQueryParams Objects(ECC_WorldStatic);
        for (const float Offset : {430.f, 800.f})
        {
            const FVector Position = Train->GetActorLocation() + Train->GetActorRightVector() * Offset;
            FHitResult LegacyFloor;
            const bool bHit = Fixture.World->LineTraceSingleByObjectType(LegacyFloor,
                Position + FVector(0, 0, 600), Position - FVector(0, 0, 1500), Objects, Query);
            TestTrue(Label + TEXT("Legacy floor ray hits authored canopy"),
                bHit && Fixture.Canopy.Contains(LegacyFloor.GetActor()));
            TestTrue(Label + TEXT("Legacy canopy hit exceeds permitted boarding rise"),
                bHit && LegacyFloor.ImpactPoint.Z - SurfaceZ > 180);
        }
        FVector Door;
        FVector Sidewalk;
        if (!TestTrue(Label + TEXT("Boarding path succeeds below canopy"), Train->DoorAndSidewalk(Door, Sidewalk)))
        {
            continue;
        }
        TestTrue(Label + TEXT("Door capsule rests on platform Z100"), FMath::IsNearlyEqual(Door.Z, 195.0));
        TestTrue(Label + TEXT("Sidewalk capsule rests on platform Z100"), FMath::IsNearlyEqual(Sidewalk.Z, 195.0));
        const FCollisionShape Capsule = FCollisionShape::MakeCapsule(32, 92);
        // Vat can lech tia do san nhung van cham capsule o cua tau.
        AActor* Blocker = Fixture.AddBox(Door + Train->GetActorForwardVector() * 50, FVector(25, 45, 100));
        TestTrue(Label + TEXT("Door blocker really overlaps standing capsule"),
            Fixture.World->OverlapBlockingTestByChannel(Door, FQuat::Identity, ECC_Pawn, Capsule, Query));
        FVector BlockedDoor;
        FVector BlockedSidewalk;
        TestFalse(Label + TEXT("Door obstruction still prevents boarding"),
            Train->DoorAndSidewalk(BlockedDoor, BlockedSidewalk));
        Blocker->SetActorLocation((Door + Sidewalk) * .5);
        TestFalse(Label + TEXT("Passage blocker leaves door endpoint clear"),
            Fixture.World->OverlapBlockingTestByChannel(Door, FQuat::Identity, ECC_Pawn, Capsule, Query));
        TestFalse(Label + TEXT("Passage blocker leaves sidewalk endpoint clear"),
            Fixture.World->OverlapBlockingTestByChannel(Sidewalk, FQuat::Identity, ECC_Pawn, Capsule, Query));
        TestFalse(Label + TEXT("Obstruction between endpoints still prevents boarding"),
            Train->DoorAndSidewalk(BlockedDoor, BlockedSidewalk));
        Blocker->Destroy();
        TestTrue(Label + TEXT("Removing blocker restores boarding"), Train->DoorAndSidewalk(Door, Sidewalk));
    }
    return true;
}
#endif
