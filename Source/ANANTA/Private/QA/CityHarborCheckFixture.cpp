#include "QA/CityHarborCheck.h"

#include "Camera/CameraActor.h"
#include "City/Mobility/CityRouteVehicle.h"
#include "City/Mobility/CityTransportManager.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"

bool UCityHarborCheck::PrepareStreaming()
{
    if (!GetWorld()->GetMapName().Contains(TEXT("ANANTA_City")) || !GetWorld()->GetWorldPartition())
    {
        Finish(TEXT("Requires authored ANANTA_City World Partition map"));
        return false;
    }
    for (TActorIterator<ACityRouteVehicle> It(GetWorld()); It; ++It)
    {
        Finish(TEXT("Unexpected existing fleet: manager suppression did not precede fleet creation"));
        return false;
    }
    auto* Camera = GetWorld()->SpawnActor<ACameraActor>();
    if (!Camera)
    {
        Finish(TEXT("Cannot create physics fixture streaming observer"));
        return false;
    }
    Observer = Camera;
    Camera->Tags.Add(TEXT("QA_AuthoredHarborPhysicsFixture"));
    Camera->SetActorLocationAndRotation(FVector(135200, -135500, 2000), FRotator(-30, -90, 0));
    auto* Source = NewObject<UWorldPartitionStreamingSourceComponent>(Camera);
    Camera->AddInstanceComponent(Source);
    FStreamingSourceShape Shape;
    Shape.bUseGridLoadingRange = false;
    Shape.Radius = 20000;
    Source->Shapes.Add(Shape);
    Source->TargetState = EStreamingSourceTargetState::Activated;
    Source->EnableStreamingSource();
    Source->RegisterComponent();
    StreamingSource = Source;
    auto* Controller = GetWorld()->GetFirstPlayerController();
    PreviousView = Controller->GetViewTarget();
    Controller->SetViewTarget(Camera);
    UE_LOG(LogTemp, Display, TEXT("CITY_HARBOR_FIXTURE observer relocation; authored map; radius=20000cm"));
    return true;
}

void UCityHarborCheck::SpawnVessels()
{
    for (int32 Index = 0; Index < Results.Num(); ++Index)
    {
        FCityHarborResult& Result = Results[Index];
        const auto Kind = static_cast<ECityTransportKind>(static_cast<int32>(ECityTransportKind::CargoShip) + Index);
        const FString Path = FString::Printf(TEXT("/Game/ANANTA/City/Meshes/SM_%s.SM_%s"),
            *Result.Kind, *Result.Kind);
        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
        const FCityTransportRoute Route = CityMobility::MakeRoute(Kind);
        if (!Mesh || !Mesh->GetBoundingBox().IsValid || Route.Points.IsEmpty())
        {
            Result.Status = TEXT("FAIL");
            Result.Reason = TEXT("Missing imported mesh bounds or authored route");
            continue;
        }
        Result.Dock = Route.Points[0];
        Result.OriginHeight = Mesh->GetBoundingBox().GetCenter().Z + 5;
        Result.Vehicle = GetWorld()->SpawnActor<ACityRouteVehicle>();
        if (!Result.Vehicle.IsValid() || !Result.Vehicle->Configure(Kind, Route, Mesh, 0))
        {
            Result.Status = TEXT("FAIL");
            Result.Reason = TEXT("Configure rejected actual authored dock collision");
            if (Result.Vehicle.IsValid())
            {
                Result.Vehicle->Destroy();
            }
            continue;
        }
        Result.Previous = Result.Vehicle->GetActorLocation();
        Result.MinimumWaterline = Result.Previous.Z - Result.OriginHeight;
        Result.LastProgressAt = ReadyAt;
    }
}

void UCityHarborCheck::Observe(FCityHarborResult& Result, const double Now)
{
    if (Result.Status != TEXT("PENDING"))
    {
        return;
    }
    Result.Elapsed = Now - ReadyAt;
    if (!Result.Vehicle.IsValid())
    {
        Result.Status = TEXT("FAIL");
        Result.Reason = TEXT("Fixture vessel disappeared");
        return;
    }
    const ACityRouteVehicle* Vehicle = Result.Vehicle.Get();
    const FVector Position = Vehicle->GetActorLocation();
    if (Position.ContainsNaN() || !Vehicle->GetActorEnableCollision())
    {
        Result.Status = TEXT("FAIL");
        Result.Reason = TEXT("Invalid vessel position or disabled actor collision");
        return;
    }
    Result.MinimumWaterline = FMath::Min(Result.MinimumWaterline, Position.Z - Result.OriginHeight);
    Result.DockDistance = FVector::Dist2D(Position, Result.Dock);
    Result.MaximumDistance = FMath::Max(Result.MaximumDistance, Result.DockDistance);
    const double Step = FVector::Dist2D(Position, Result.Previous);
    Result.TravelDistance += Step;
    Result.Previous = Position;
    if (Step > 0.1 || Result.Boarded != Vehicle->GetBoardingCount()
        || Result.Alighted != Vehicle->GetAlightingCount())
    {
        Result.LastProgressAt = Now;
    }
    Result.Boarded = Vehicle->GetBoardingCount();
    Result.Alighted = Vehicle->GetAlightingCount();
    if (!Vehicle->GetBlockedReason().IsEmpty())
    {
        Result.LastBlocker = Vehicle->GetBlockedReason();
    }
    if (Result.MinimumWaterline < CityMobility::WaterLevel - 5)
    {
        Result.Status = TEXT("FAIL");
        Result.Reason = TEXT("Vessel waterline descended below authored water level");
    }
    else if (Result.DockDistance > 9000)
    {
        if (Result.Boarded == 0)
        {
            Result.Status = TEXT("FAIL");
            Result.Reason = TEXT("Outbound vessel never boarded a passenger at its authored dock");
        }
        Result.bOutbound = true;
    }
    if (Result.bOutbound && Result.DockDistance < 200 && Vehicle->IsStopped())
    {
        Result.bReturned = true;
    }
    if (Result.Status == TEXT("PENDING") && Result.bReturned && Result.Alighted > 0)
    {
        Result.Status = TEXT("PASS");
        Result.Reason = TEXT("Boarded, travelled beyond 9000 cm, returned stopped at dock, and alighted");
    }
    else if (Result.Status == TEXT("PENDING") && Now - Result.LastProgressAt > 35)
    {
        Result.Status = TEXT("FAIL");
        Result.Reason = TEXT("No movement or passenger progress for 35 seconds; blocker: ") + Result.LastBlocker;
    }
}

void UCityHarborCheck::Cleanup()
{
    for (FCityHarborResult& Result : Results)
    {
        if (Result.Vehicle.IsValid())
        {
            Result.Vehicle->Destroy();
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
