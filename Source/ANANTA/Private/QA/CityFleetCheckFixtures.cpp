#include "QA/CityFleetCheck.h"

#include "City/Mobility/CityRouteVehicle.h"
#include "Components/BoxComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"

AActor* UCityFleetCheck::AddBox(const FVector& Location, const FVector& Extent)
{
    AActor* Actor = GetWorld()->SpawnActor<AActor>();
    if (!Actor)
    {
        return nullptr;
    }
    Geometry.Add(Actor);
    UBoxComponent* Box = NewObject<UBoxComponent>(Actor);
    Actor->SetRootComponent(Box);
    Actor->AddInstanceComponent(Box);
    Box->SetMobility(EComponentMobility::Static);
    Box->SetBoxExtent(Extent);
    Box->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Box->SetCollisionObjectType(ECC_WorldStatic);
    Box->SetCollisionResponseToAllChannels(ECR_Block);
    Box->SetCanEverAffectNavigation(false);
    Box->SetWorldLocation(Location);
    Box->RegisterComponent();
    return Actor;
}

bool UCityFleetCheck::BuildFixtures()
{
    for (int32 Index = 0; Index < static_cast<int32>(ECityTransportKind::Count); ++Index)
    {
        const auto Kind = static_cast<ECityTransportKind>(Index);
        FCityFleetFixture& Fixture = Fixtures.AddDefaulted_GetRef();
        Fixture.Name = CityMobility::MeshName(Kind);
        const FString Path = FString::Printf(TEXT("/Game/ANANTA/City/Meshes/SM_%s.SM_%s"),
            *Fixture.Name, *Fixture.Name);
        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
        if (!Mesh || !Mesh->GetBoundingBox().IsValid)
        {
            Finish(false, Fixture.Name + TEXT(": imported mesh missing or invalid bounds"));
            return false;
        }
        Fixture.Extent = Mesh->GetBoundingBox().GetExtent();
        const FVector Size = Fixture.Extent * 2;
        if (Size.ContainsNaN() || Size.GetMin() < 100 || Size.GetMax() > 4000)
        {
            Finish(false, Fixture.Name + TEXT(": imported bounds outside centimetre fleet scale"));
            return false;
        }
        // Tach fixture khoi thanh pho; khong dich chuyen nhan vat dang choi hay sua tuyen that.
        const FVector Base(600000 + Index * 20000, 600000, 0);
        const auto Authored = CityMobility::MakeRoute(Kind);
        const bool bWater = Authored.bWater;
        const bool bRail = Authored.bRail;
        const float FloorHeight = bRail ? 51.f : 0.f;
        const float Length = FMath::Max(5000.f, static_cast<float>(Size.X * 2));
        const FVector HalfLength(Length * .5f, 0, 0);
        bool bGeometryReady = true;
        if (!bWater)
        {
            bGeometryReady &= AddBox(Base + HalfLength + FVector(0, 0, FloorHeight - 50),
                FVector(Length * .5f + Fixture.Extent.X + 500, 1300, 50)) != nullptr;
            bGeometryReady &= AddBox(Base + HalfLength + FVector(0, bRail ? 800 : 700, bRail ? 50 : 9),
                FVector(Length * .5f + 400, 300, bRail ? 50 : 9)) != nullptr;
        }
        else
        {
            // Mat cau tau chi o ben phai hull, khong tao san vo hinh tren hanh lang nuoc.
            bGeometryReady &= AddBox(Base + HalfLength + FVector(0, Fixture.Extent.Y + 260, -70),
                FVector(Length * .5f + 400, 220, 50)) != nullptr;
        }
        const float DoorY = bRail ? 430.f : Fixture.Extent.Y + 65;
        Fixture.DoorBlocker = AddBox(Base + FVector(0, DoorY, 140), FVector(60, 40, 180));
        const float BodyZ = Mesh->GetBoundingBox().GetCenter().Z + 5
            + (bWater ? CityMobility::WaterLevel : FloorHeight);
        Fixture.LaneBlocker = AddBox(Base + FVector(Fixture.Extent.X + 240, 0, BodyZ),
            FVector(40, Fixture.Extent.Y + 20, Fixture.Extent.Z + 20));
        if (!bGeometryReady || !Fixture.DoorBlocker.IsValid() || !Fixture.LaneBlocker.IsValid())
        {
            Finish(false, Fixture.Name + TEXT(": fixture geometry spawn failed"));
            return false;
        }
        FCityTransportRoute Route;
        Route.Id = FName(*(TEXT("QA_Fixture_") + Fixture.Name));
        Route.bWater = bWater;
        Route.bRail = bRail;
        Route.Points = {Base, Base + FVector(Length, 0, 0), Base + FVector(Length + 4000, 0, 0)};
        Route.Stops = {0, 1};
        Fixture.Vehicle = GetWorld()->SpawnActor<ACityRouteVehicle>();
        if (!Fixture.Vehicle.IsValid() || !Fixture.Vehicle->Configure(Kind, Route, Mesh, 0))
        {
            Finish(false, Fixture.Name + TEXT(": Configure rejected supported unoccupied start"));
            return false;
        }
        Fixture.Start = Fixture.Vehicle->GetActorLocation();
        UE_LOG(LogTemp, Display, TEXT("CITY_FLEET_FIXTURE_START kind=%s water=%d bounds=%s"),
            *Fixture.Name, bWater, *Size.ToString());
    }
    return true;
}
