#include "QA/CityRoadRoutesCheck.h"

#include "Camera/CameraActor.h"
#include "City/Mobility/CityRouteVehicle.h"
#include "City/Mobility/CityTransportManager.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"

bool UCityRoadRoutesCheck::PrepareStreaming()
{
    if (!GetWorld()->GetWorldPartition())
    {
        Finish(TEXT("Requires authored ANANTA_City World Partition map"));
        return false;
    }
    if (HasUnexpectedFleet())
    {
        Finish(TEXT("Existing non-fixture road fleet detected before fixture setup"));
        return false;
    }
    auto* Camera = GetWorld()->SpawnActor<ACameraActor>();
    if (!Camera)
    {
        Finish(TEXT("Cannot create authored road streaming observer"));
        return false;
    }
    Observer = Camera;
    Camera->Tags.Add(TEXT("QA_AuthoredRoadPhysicsFixture"));
    if (Region != TEXT("Core"))
    {
        FBox RouteBounds(ForceInit);
        for (const auto& Result : Results)
        {
            for (const FVector& Point : Result.Route.Points)
            {
                RouteBounds += Point;
            }
        }
        ObserverLocation = RouteBounds.GetCenter();
        ObserverLocation.Z = 2000;
    }
    Camera->SetActorLocationAndRotation(ObserverLocation, FRotator(-60, 0, 0));
    // Ban kinh gom ca tam tuyen, le duong va bien cell; kiem tra diem xa nhat truoc khi spawn.
    for (const auto& Result : Results)
    {
        for (const FVector& Point : Result.Route.Points)
        {
            if (FVector::Dist(Point, Camera->GetActorLocation()) > 58000)
            {
                Finish(TEXT("Authored route exceeds pinned streaming coverage"));
                return false;
            }
        }
    }
    auto* Source = NewObject<UWorldPartitionStreamingSourceComponent>(Camera);
    Camera->AddInstanceComponent(Source);
    FStreamingSourceShape Shape;
    Shape.bUseGridLoadingRange = false;
    Shape.Radius = 62000;
    Source->Shapes.Add(Shape);
    Source->TargetState = EStreamingSourceTargetState::Activated;
    Source->EnableStreamingSource();
    Source->RegisterComponent();
    StreamingSource = Source;
    auto* Controller = GetWorld()->GetFirstPlayerController();
    PreviousView = Controller->GetViewTarget();
    Controller->SetViewTarget(Camera);
    UE_LOG(LogTemp, Display, TEXT("CITY_ROAD_FIXTURE observer relocated; radius=62000; two vehicles per route"));
    return true;
}

void UCityRoadRoutesCheck::SpawnVehicles()
{
    for (int32 Index = 0; Index < Results.Num(); ++Index)
    {
        auto& Result = Results[Index];
        const FString Path = FString::Printf(TEXT("/Game/ANANTA/City/Meshes/SM_%s.SM_%s"),
            *Result.Kind, *Result.Kind);
        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
        for (auto& Probe : Result.Probes)
        {
            if (!Mesh || !Mesh->GetBoundingBox().IsValid || Result.Route.Points.Num() != 8
                || Result.Route.Stops != TArray<int32>({0, 2, 4, 6}) || Result.Route.bWater)
            {
                Probe.Status = TEXT("FAIL");
                Probe.Reason = TEXT("Missing imported mesh or expected authored four-stop road route");
                continue;
            }
            Probe.OriginHeight = Mesh->GetBoundingBox().GetCenter().Z + 5;
            Probe.Vehicle = GetWorld()->SpawnActor<ACityRouteVehicle>();
            if (!Probe.Vehicle.IsValid() || !Probe.Vehicle->Configure(Result.TransportKind,
                Result.Route, Mesh, Probe.InitialPoint))
            {
                Probe.Status = TEXT("FAIL");
                Probe.Reason = TEXT("Configure rejected actual authored stop collision or floor");
                if (Probe.Vehicle.IsValid())
                {
                    Probe.Vehicle->Destroy();
                }
                continue;
            }
            Probe.Vehicle->Tags.Add(TEXT("QA_AuthoredRoadPhysicsFixture"));
            Probe.Previous = Probe.Vehicle->GetActorLocation();
            Probe.LastProgressAt = ReadyAt;
        }
    }
}

void UCityRoadRoutesCheck::Cleanup()
{
    for (auto& Result : Results)
    {
        for (auto& Probe : Result.Probes)
        {
            if (Probe.Vehicle.IsValid())
            {
                Probe.Vehicle->Destroy();
            }
        }
    }
    if (auto* Controller = GetWorld()->GetFirstPlayerController())
    {
        if (PreviousView.IsValid() && Controller->GetViewTarget() == Observer.Get())
        {
            Controller->SetViewTarget(PreviousView.Get());
        }
    }
    if (Observer.IsValid())
    {
        Observer->Destroy();
    }
    GetWorld()->RemoveOnActorSpawnedHandler(SpawnHandle);
    for (const auto& Manager : PausedManagers)
    {
        if (Manager.IsValid())
        {
            Manager->SetActorTickEnabled(true);
        }
    }
    PausedManagers.Empty();
}
