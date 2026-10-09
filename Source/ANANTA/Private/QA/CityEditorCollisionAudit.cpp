#include "QA/CityEditorTools.h"

#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "PhysicsEngine/BodySetup.h"

FString UCityEditorTools::AuditLoadedCollision(UWorld* World)
{
#if WITH_EDITOR
    if (!World)
    {
        return TEXT("passed=0\nerror=Missing editor world\n");
    }
    int32 Components = 0;
    int32 Instances = 0;
    int32 RoadSamples = 0;
    int32 Errors = 0;
    FString Detail;
    for (TActorIterator<AActor> It(World); It; ++It)
    {
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
    // Kiem tra mat duong tren toan luoi 3,4 km, doc lap voi so luong instance trong script.
    const auto CheckRoad = [&](const FVector& Point)
    {
        if (Point.X >= 120000 && Point.Y <= -120000)
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
    for (int32 X = -168000; X <= 168000; X += 12000)
    {
        for (int32 Y = -168000; Y <= 168000; Y += 12000)
        {
            CheckRoad(FVector(X, Y, 0));
            if (X < 168000)
            {
                CheckRoad(FVector(X + 6000, Y + 420, 0));
                CheckRoad(FVector(X + 6000, Y - 420, 0));
            }
            if (Y < 168000)
            {
                CheckRoad(FVector(X + 420, Y + 6000, 0));
                CheckRoad(FVector(X - 420, Y + 6000, 0));
            }
        }
    }
    return FString::Printf(TEXT("passed=%d\nblockingComponents=%d\nblockingInstances=%d\n")
        TEXT("roadSamples=%d\nerrors=%d\nscope=loaded map bodies and road support, not every player trajectory\n"),
        Errors == 0 && Components > 0 && RoadSamples > 0, Components, Instances, RoadSamples, Errors) + Detail;
#else
    return TEXT("passed=0\nerror=Editor only\n");
#endif
}
