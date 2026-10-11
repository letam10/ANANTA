#include "QA/CityEditorTools.h"
#include "City/CityWorldBounds.h"

#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "PhysicsEngine/BodySetup.h"

FString UCityEditorTools::AuditCollisionActors(UWorld* World, const TArray<FGuid>& ActorGuids)
{
#if WITH_EDITOR
    if (!World)
    {
        return TEXT("passed=0\nerror=Missing editor world\n");
    }
    int32 Components = 0;
    int32 Instances = 0;
    int32 Actors = 0;
    int32 Errors = 0;
    FString Detail;
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        if (!ActorGuids.IsEmpty() && !ActorGuids.Contains(It->GetActorGuid()))
        {
            continue;
        }
        ++Actors;
        TInlineComponentArray<UStaticMeshComponent*> Meshes;
        It->GetComponents(Meshes);
        for (UStaticMeshComponent* Component : Meshes)
        {
            if (!Component->IsQueryCollisionEnabled()
                || Component->GetCollisionResponseToChannel(ECC_Pawn) != ECR_Block)
            {
                continue;
            }
            UStaticMesh* Mesh = Component->GetStaticMesh();
            if (!Mesh)
            {
                continue;
            }
            ++Components;
            const auto* Instanced = Cast<UInstancedStaticMeshComponent>(Component);
            Instances += Instanced ? Instanced->GetInstanceCount() : 1;
            UBodySetup* Body = Mesh->GetBodySetup();
            if (!Body || (Body->AggGeom.GetElementCount() == 0 && Body->CollisionTraceFlag != CTF_UseComplexAsSimple))
            {
                ++Errors;
                Detail += FString::Printf(TEXT("missingBody=%s mesh=%s\n"),
                    *It->GetActorLabel(), *Mesh->GetPathName());
            }
        }
    }
    if (!ActorGuids.IsEmpty() && Actors != ActorGuids.Num())
    {
        ++Errors;
        Detail += FString::Printf(TEXT("missingLoadedActors=%d/%d\n"), Actors, ActorGuids.Num());
    }
    return FString::Printf(TEXT("passed=%d\nblockingComponents=%d\nblockingInstances=%d\nerrors=%d\n"),
        Errors == 0, Components, Instances, Errors) + Detail;
#else
    return TEXT("passed=0\nerror=Editor only\n");
#endif
}

FString UCityEditorTools::AuditRoadRegion(UWorld* World, FVector Minimum, FVector Maximum)
{
#if WITH_EDITOR
    if (!World)
    {
        return TEXT("passed=0\nerror=Missing editor world\n");
    }
    int32 RoadSamples = 0;
    int32 Errors = 0;
    FString Detail;
    // Ra mat duong toan luoi hien hanh, doc lap voi so instance cua script.
    const auto CheckRoad = [&](const FVector& Point)
    {
        if (Point.X < Minimum.X || Point.X >= Maximum.X || Point.Y < Minimum.Y || Point.Y >= Maximum.Y
            || CityWorldBounds::IsStreetCutout(Point.X, Point.Y))
        {
            return;
        }
        ++RoadSamples;
        FHitResult Floor;
        const FCollisionQueryParams Params(SCENE_QUERY_STAT(CityWholeMapRoad), false);
        const bool bHit = World->LineTraceSingleByObjectType(Floor, Point + FVector(0, 0, 500),
            Point - FVector(0, 0, 200), FCollisionObjectQueryParams(ECC_WorldStatic), Params);
        if (!bHit || Floor.ImpactNormal.Z < .85f || Floor.ImpactPoint.Z < -5 || Floor.ImpactPoint.Z > 25)
        {
            ++Errors;
            Detail += FString::Printf(TEXT("roadInvalid=%s hit=%s z=%.1f\n"), *Point.ToString(),
                *GetNameSafe(Floor.GetActor()), Floor.ImpactPoint.Z);
        }
    };
    for (int32 X = -CityWorldBounds::RoadExtent; X <= CityWorldBounds::RoadExtent; X += 12000)
    {
        for (int32 Y = -CityWorldBounds::RoadExtent; Y <= CityWorldBounds::RoadExtent; Y += 12000)
        {
            CheckRoad(FVector(X, Y, 0));
            if (X < CityWorldBounds::RoadExtent)
            {
                CheckRoad(FVector(X + 6000, Y + 420, 0));
                CheckRoad(FVector(X + 6000, Y - 420, 0));
            }
            if (Y < CityWorldBounds::RoadExtent)
            {
                CheckRoad(FVector(X + 420, Y + 6000, 0));
                CheckRoad(FVector(X - 420, Y + 6000, 0));
            }
        }
    }
    return FString::Printf(TEXT("passed=%d\nroadSamples=%d\nerrors=%d\n"), Errors == 0, RoadSamples, Errors) + Detail;
#else
    return TEXT("passed=0\nerror=Editor only\n");
#endif
}

FString UCityEditorTools::AuditLoadedCollision(UWorld* World)
{
    const FString Bodies = AuditCollisionActors(World, {});
    const float Edge = CityWorldBounds::RoadExtent;
    const FString Roads = AuditRoadRegion(World, FVector(-Edge, -Edge, -1000), FVector(Edge + 1, Edge + 1, 1000));
    const bool bPassed = Bodies.StartsWith(TEXT("passed=1\n")) && Roads.StartsWith(TEXT("passed=1\n"));
    return FString::Printf(TEXT("passed=%d\n"), bPassed) + Bodies.Mid(9) + Roads.Mid(9);
}
