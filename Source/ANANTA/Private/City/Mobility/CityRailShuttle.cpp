#include "City/Mobility/CityRailShuttle.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

void ACityRailShuttle::BeginPlay()
{
    Super::BeginPlay();
    auto* Mesh = LoadObject<UStaticMesh>(nullptr,
        TEXT("/Game/ANANTA/City/Meshes/SM_PassengerTrain.SM_PassengerTrain"));
    if (!Mesh)
    {
        UE_LOG(LogTemp, Error, TEXT("CITY_RAIL_MISSING_MESH"));
        return;
    }
    const int32 Sign = DirectionSign < 0 ? -1 : 1;
    // Chua den buffer: tinh ca nua than tau va khoang sweep nhin truoc 180 cm.
    const float End = FMath::Min(2000.f, 3900.f - Mesh->GetBoundingBox().GetExtent().X - 250.f);
    if (End < 1000)
    {
        UE_LOG(LogTemp, Error, TEXT("CITY_RAIL_TRAIN_TOO_LONG halfLength=%.1f"), Mesh->GetBoundingBox().GetExtent().X);
        return;
    }
    FCityTransportRoute ShuttleRoute;
    ShuttleRoute.Id = Sign > 0 ? TEXT("RailEast") : TEXT("RailWest");
    ShuttleRoute.bRail = true;
    for (const float Offset : {-End, End, End / 3, -End / 3})
    {
        ShuttleRoute.Points.Add(StationCentre + FVector(Sign * Offset, Sign * 500.f, 0));
    }
    ShuttleRoute.Stops = {0, 1};
    ShuttleRoute.ReverseTargets = {2, 3, 0};
    const bool bReady = Configure(ECityTransportKind::PassengerTrain, ShuttleRoute, Mesh, 0);
    FString PlacementManifest;
    if (FParse::Value(FCommandLine::Get(), TEXT("CityPlacementViews="), PlacementManifest))
    {
        // Chi dung dong bang trong luot chup nam goc; gameplay thuong van chay tuyen.
        SetActorTickEnabled(false);
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_RAIL_READY ShuttleRoute=%s success=%d stopOffset=%.1f"),
        *ShuttleRoute.Id.ToString(), bReady, End);
}
