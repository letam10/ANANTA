#if WITH_DEV_AUTOMATION_TESTS
#include "City/ANANTACityVehicle.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/TraversalComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Misc/AutomationTest.h"

namespace
{
    struct FCollisionFixture
    {
        UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);

        ~FCollisionFixture()
        {
            World->DestroyWorld(false);
        }

        UBoxComponent* Box(const FVector& Location, const FVector& Extent)
        {
            AActor* Actor = World->SpawnActor<AActor>();
            auto* Shape = NewObject<UBoxComponent>(Actor);
            Actor->SetRootComponent(Shape);
            Shape->SetBoxExtent(Extent);
            Shape->SetCollisionProfileName(TEXT("BlockAll"));
            Shape->RegisterComponent();
            Actor->SetActorLocation(Location);
            return Shape;
        }

        ACharacter* Character(const FVector& Location)
        {
            FActorSpawnParameters Params;
            Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
            auto* Hero = World->SpawnActor<ACharacter>(Location, FRotator::ZeroRotator, Params);
            Hero->GetCapsuleComponent()->SetCapsuleSize(38, 92);
            Hero->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
            return Hero;
        }
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityExitHeadroomTest, "ANANTA.City.Collision.ExitChecksEntireCapsule",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityExitHeadroomTest::RunTest(const FString& Parameters)
{
    FCollisionFixture Fixture;
    Fixture.Box(FVector(0, 0, -10), FVector(1000, 1000, 10));
    auto* Car = Fixture.World->SpawnActor<AANANTACityVehicle>(FVector(0, 0, 70), FRotator::ZeroRotator);
    auto* Hero = Fixture.Character(FVector(0, 0, 95));
    Hero->SetActorEnableCollision(false);
    FVector Exit;
    TestTrue(TEXT("Unobstructed exit remains available"), Car->FindSafeExit(Hero, Exit));
    TArray<UBoxComponent*> Beams;
    for (const float Side : {-1.f, 1.f})
    {
        Beams.Add(Fixture.Box(FVector(0, Side * 130, 167), FVector(60, 5, 10)));
        Beams.Add(Fixture.Box(FVector(Side * 260, 0, 167), FVector(5, 60, 10)));
    }
    // Cac dam khong cham xe hay diem den, chi cat qua phan dau tren duong ra.
    TestFalse(TEXT("Head-only obstacles on every exit route reject exit"), Car->FindSafeExit(Hero, Exit));
    for (UBoxComponent* Beam : Beams)
    {
        Beam->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
    Hero->GetCapsuleComponent()->SetCapsuleSize(38, 140);
    TestTrue(TEXT("Tall capsule can exit into clear space"), Car->FindSafeExit(Hero, Exit));
    TestTrue(TEXT("Exit height follows actual capsule"), FMath::IsNearlyEqual(Exit.Z, 143.0));
    Fixture.Box(FVector(0, 0, 240), FVector(1000, 1000, 5));
    TestFalse(TEXT("Ceiling rejects tall capsule"), Car->FindSafeExit(Hero, Exit));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityMantleSupportTest, "ANANTA.City.Collision.MantleRequiresPawnSupport",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityMantleSupportTest::RunTest(const FString& Parameters)
{
    FCollisionFixture Fixture;
    Fixture.Box(FVector(0, 0, -10), FVector(1000, 1000, 10));
    auto* Ledge = Fixture.Box(FVector(125, 0, 50), FVector(75, 200, 50));
    Ledge->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore);
    auto* Hero = Fixture.Character(FVector(0, 0, 95));
    auto* Traversal = NewObject<UTraversalComponent>(Hero);
    Traversal->RegisterComponent();
    const FVector BeforeRejectedMantle = Hero->GetActorLocation();
    TestFalse(TEXT("Visibility-only ledge cannot support mantle"), Traversal->TryMantle());
    TestTrue(TEXT("Rejected mantle leaves position intact"),
        Hero->GetActorLocation().Equals(BeforeRejectedMantle));
    Ledge->SetCollisionResponseToChannel(ECC_Pawn, ECR_Block);
    Ledge->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
    TestTrue(TEXT("Pawn-blocking ledge supports mantle without visibility collision"), Traversal->TryMantle());
    // Walking dieu chinh khoang cach san theo MIN/MAX_FLOOR_DIST cua engine.
    const float FeetZ = Hero->GetActorLocation().Z - Hero->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    TestTrue(TEXT("Mantle places feet above ledge"), FeetZ > 100.f && FeetZ < 104.f);
    Hero->SetActorLocation(FVector(0, 0, 95));
    Hero->GetCharacterMovement()->DisableMovement();
    TestFalse(TEXT("Disabled movement during restore cannot mantle"), Traversal->TryMantle());
    return true;
}
#endif
