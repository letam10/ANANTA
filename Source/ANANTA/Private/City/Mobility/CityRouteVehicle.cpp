#include "City/Mobility/CityRouteVehicle.h"

#include "City/Mobility/CityTransitPassenger.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"

ACityRouteVehicle::ACityRouteVehicle()
{
    PrimaryActorTick.bCanEverTick = true;
    CollisionBody = CreateDefaultSubobject<UBoxComponent>(TEXT("RouteCollision"));
    SetRootComponent(CollisionBody);
    CollisionBody->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    CollisionBody->SetCanEverAffectNavigation(false);
    BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RouteBody"));
    BodyMesh->SetupAttachment(RootComponent);
    BodyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    BodyMesh->SetCanEverAffectNavigation(false);
    SetCanBeDamaged(false);
}

bool ACityRouteVehicle::Configure(const ECityTransportKind InKind, const FCityTransportRoute& InRoute,
    UStaticMesh* Mesh, const int32 InitialPoint)
{
    if (!Mesh || !InRoute.Points.IsValidIndex(InitialPoint) || InRoute.Points.Num() < 2)
    {
        return false;
    }
    Kind = InKind;
    Route = InRoute;
    BodyMesh->SetStaticMesh(Mesh);
    const FBox Bounds = Mesh->GetBoundingBox();
    Extent = Bounds.GetExtent();
    Extent.Z = FMath::Max(Extent.Z, 30.f);
    OriginHeight = Bounds.GetCenter().Z + 5.f;
    CollisionBody->SetBoxExtent(Extent);
    BodyMesh->SetRelativeLocation(-Bounds.GetCenter());
    FVector Position = Route.Points[InitialPoint];
    if (!PlaceOnSurface(Position))
    {
        return false;
    }
    Point = (InitialPoint + 1) % Route.Points.Num();
    FVector Direction = Route.Points[Point] - Route.Points[InitialPoint];
    Direction.Z = 0;
    const FQuat Rotation = Direction.Rotation().Quaternion();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRouteSpawn), false, this);
    if (GetWorld()->OverlapBlockingTestByChannel(Position, Rotation, ECC_WorldDynamic,
        FCollisionShape::MakeBox(Extent), Params))
    {
        return false;
    }
    SetActorLocationAndRotation(Position, Rotation);
    bStopped = Route.Stops.Contains(InitialPoint);
    bConfigured = true;
    return true;
}

bool ACityRouteVehicle::PlaceOnSurface(FVector& Position) const
{
    if (Route.bWater)
    {
        Position.Z = CityMobility::WaterLevel + OriginHeight;
        return true;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRouteGround), false, this);
    FHitResult Floor;
    const FCollisionObjectQueryParams Objects(ECC_WorldStatic);
    if (!GetWorld()->LineTraceSingleByObjectType(Floor, Position + FVector(0, 0, 400),
        Position - FVector(0, 0, 1200), Objects, Params) || Floor.ImpactNormal.Z < 0.85f)
    {
        return false;
    }
    Position.Z = Floor.ImpactPoint.Z + OriginHeight;
    return true;
}

void ACityRouteVehicle::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (!bConfigured)
    {
        return;
    }
    if (bStopped)
    {
        ServiceStop(DeltaTime);
    }
    else
    {
        MoveAlongRoute(DeltaTime);
    }
}

void ACityRouteVehicle::MoveAlongRoute(const float DeltaTime)
{
    FVector Direction = Route.Points[Point] - GetActorLocation();
    Direction.Z = 0;
    const float Distance = Direction.Size();
    if (Distance < 45)
    {
        bStopped = Route.Stops.Contains(Point);
        Point = (Point + 1) % Route.Points.Num();
        bServiced = false;
        StopElapsed = 0;
        return;
    }
    const FVector Forward = Direction / Distance;
    const bool bReverse = Route.ReverseTargets.Contains(Point);
    const FVector Heading = bReverse ? -Direction : Direction;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRouteMovement), false, this);
    Params.AddIgnoredActor(Passenger);
    const float Step = FMath::Min(DeltaTime, 0.05f);
    const FRotator NextRotation = FMath::RInterpConstantTo(GetActorRotation(), Heading.Rotation(), Step, 45);
    // Sweep khong kiem tra phep xoay, chia goc quay thanh buoc nho va kiem tra the tich moi.
    if (GetWorld()->OverlapBlockingTestByChannel(GetActorLocation(), NextRotation.Quaternion(),
        ECC_WorldDynamic, FCollisionShape::MakeBox(Extent), Params))
    {
        BlockedReason = TEXT("Rotation occupied");
        return;
    }
    // Vat can phia truoc khong duoc khoa huong lai da kiem tra an toan, neu khong xe ket o goc re.
    SetActorRotation(NextRotation);
    FHitResult Obstacle;
    const float Travel = FMath::Min(Distance, CityMobility::CruiseSpeed(Kind) * Step * (bReverse ? .5f : 1.f));
    if (GetWorld()->SweepSingleByChannel(Obstacle, GetActorLocation(),
        GetActorLocation() + Forward * (Travel + 180), NextRotation.Quaternion(), ECC_WorldDynamic,
        FCollisionShape::MakeBox(Extent), Params))
    {
        BlockedReason = FString::Printf(TEXT("Obstacle %s at %s"),
            *GetNameSafe(Obstacle.GetActor()), *Obstacle.ImpactPoint.ToString());
        return;
    }
    FVector Target = GetActorLocation() + Forward * Travel;
    if (!PlaceOnSurface(Target))
    {
        BlockedReason = TEXT("Missing loaded road support");
        return;
    }
    BlockedReason.Reset();
    FHitResult Hit;
    SetActorLocation(Target, true, &Hit);
}

void ACityRouteVehicle::EndPlay(const EEndPlayReason::Type Reason)
{
    if (IsValid(Passenger))
    {
        Passenger->Destroy();
    }
    Super::EndPlay(Reason);
}
