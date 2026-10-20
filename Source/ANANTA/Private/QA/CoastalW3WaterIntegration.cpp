#include "QA/CoastalW3WaterIntegration.h"

#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "Engine/CollisionProfile.h"
#include "Materials/MaterialInterface.h"

namespace
{
    struct FBoundarySpec
    {
        const TCHAR* EdgeName;
        FVector Location;
        FVector Extent;
    };

    constexpr const TCHAR* TargetActorNames[] = {
        TEXT("CoastalBatch_269"),
        TEXT("CoastalBatch_465"),
        TEXT("CoastalBatch_716"),
        TEXT("CoastalBatch_808")
    };

    const FBoundarySpec BoundarySpecs[] = {
        {TEXT("West"), FVector(-70500.0f, 0.0f, 0.0f), FVector(500.0f, 41000.0f, 5000.0f)},
        {TEXT("East"), FVector(70500.0f, 0.0f, 0.0f), FVector(500.0f, 41000.0f, 5000.0f)},
        {TEXT("South"), FVector(0.0f, -40500.0f, 0.0f), FVector(71000.0f, 500.0f, 5000.0f)},
        {TEXT("North"), FVector(0.0f, 40500.0f, 0.0f), FVector(71000.0f, 500.0f, 5000.0f)}
    };

    constexpr const TCHAR* BoundaryTag = TEXT("ANANTA_CoastalW3Boundary");
    constexpr const TCHAR* WaterMaterialPath =
        TEXT("/Game/ANANTA/WaterW3_20261020/M_WaveSpec_Opaque.M_WaveSpec_Opaque");
    constexpr const TCHAR* WaterMeshPath = TEXT("/Engine/BasicShapes/Plane.Plane");

    int32 TargetIndex(const FString& ObjectName)
    {
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(TargetActorNames); ++Index)
        {
            if (ObjectName == TargetActorNames[Index])
            {
                return Index;
            }
        }
        return INDEX_NONE;
    }
}

bool UCoastalW3WaterIntegration::ShouldCreateSubsystem(UObject* Outer) const
{
    const UWorld* World = Cast<UWorld>(Outer);
    const FString MapName = World ? World->GetMapName() : FString();
    return World && World->IsGameWorld()
        && MapName.Contains(TEXT("ANANTA_CoastalCity"));
}

TStatId UCoastalW3WaterIntegration::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCoastalW3WaterIntegration, STATGROUP_Tickables);
}

void UCoastalW3WaterIntegration::Tick(const float DeltaTime)
{
    if (bApplied || !GetWorld() || !GetWorld()->HasBegunPlay())
    {
        return;
    }

    TotalElapsed += DeltaTime;
    RetryElapsed += DeltaTime;
    if (RetryElapsed < 0.25f)
    {
        return;
    }
    RetryElapsed = 0.0f;
    bApplied = ApplyToLoadedWaterActors();
}

bool UCoastalW3WaterIntegration::ApplyToLoadedWaterActors()
{
    UMaterialInterface* WaterMaterial = LoadObject<UMaterialInterface>(nullptr, WaterMaterialPath);
    if (!WaterMaterial)
    {
        UE_LOG(LogTemp, Error, TEXT("COASTAL_W3_WATER_MATERIAL_MISSING path=%s"), WaterMaterialPath);
        return false;
    }

    TSet<FString> FoundActors;
    int32 AppliedComponents = 0;
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        AActor* Actor = *It;
        if (!Actor)
        {
            continue;
        }

        const FString ObjectName = Actor->GetName();
        if (TargetIndex(ObjectName) == INDEX_NONE)
        {
            continue;
        }

        TInlineComponentArray<UStaticMeshComponent*> Components(Actor);
        Actor->GetComponents(Components);
        bool bAppliedActor = false;
        for (UStaticMeshComponent* Component : Components)
        {
            if (!Component || !Component->GetStaticMesh())
            {
                continue;
            }
            if (Component->GetStaticMesh()->GetPathName() != WaterMeshPath)
            {
                UE_LOG(LogTemp, Error, TEXT("COASTAL_W3_WATER_MESH_MISMATCH actor=%s mesh=%s"),
                    *ObjectName, *Component->GetStaticMesh()->GetPathName());
                continue;
            }
            Component->SetMaterial(0, WaterMaterial);
            bAppliedActor = true;
            ++AppliedComponents;
        }
        if (bAppliedActor)
        {
            FoundActors.Add(ObjectName);
        }
    }

    if (FoundActors.Num() == UE_ARRAY_COUNT(TargetActorNames))
    {
        if (!bBoundariesApplied && !CreateBoundaryActors())
        {
            return false;
        }
        UE_LOG(LogTemp, Display,
            TEXT("COASTAL_W3_WATER_APPLIED map=%s actors=%d components=%d material=%s boundaries=%d"),
            *GetWorld()->GetMapName(), FoundActors.Num(), AppliedComponents, WaterMaterialPath,
            BoundaryActors.Num());
        return true;
    }

    if (TotalElapsed >= 10.0f && !bLoggedFailure)
    {
        TArray<FString> Missing;
        for (const TCHAR* TargetName : TargetActorNames)
        {
            if (!FoundActors.Contains(TargetName))
            {
                Missing.Add(TargetName);
            }
        }
        bLoggedFailure = true;
        UE_LOG(LogTemp, Error,
            TEXT("COASTAL_W3_WATER_INCOMPLETE map=%s found=%d expected=%d missing=%s"),
            *GetWorld()->GetMapName(), FoundActors.Num(), UE_ARRAY_COUNT(TargetActorNames),
            *FString::Join(Missing, TEXT(",")));
    }
    return false;
}

bool UCoastalW3WaterIntegration::CreateBoundaryActors()
{
    if (bBoundariesApplied)
    {
        return true;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    for (const FBoundarySpec& Spec : BoundarySpecs)
    {
        FActorSpawnParameters SpawnParameters;
        SpawnParameters.Name = FName(FString::Printf(TEXT("ANANTA_CoastalW3Boundary_%s"), Spec.EdgeName));
        SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        SpawnParameters.ObjectFlags |= RF_Transient;

        AActor* BoundaryActor = World->SpawnActor<AActor>(
            AActor::StaticClass(),
            Spec.Location,
            FRotator::ZeroRotator,
            SpawnParameters);
        if (!BoundaryActor)
        {
            UE_LOG(LogTemp, Error, TEXT("COASTAL_W3_BOUNDARY_SPAWN_FAILED edge=%s"), Spec.EdgeName);
            for (AActor* ExistingActor : BoundaryActors)
            {
                if (IsValid(ExistingActor))
                {
                    ExistingActor->Destroy();
                }
            }
            BoundaryActors.Reset();
            return false;
        }

        BoundaryActor->SetFlags(RF_Transient);
        BoundaryActor->Tags.Add(FName(BoundaryTag));
        BoundaryActor->SetActorHiddenInGame(true);

        UBoxComponent* Box = NewObject<UBoxComponent>(
            BoundaryActor,
            FName(FString::Printf(TEXT("%s_Box"), Spec.EdgeName)));
        if (!Box)
        {
            BoundaryActor->Destroy();
            UE_LOG(LogTemp, Error, TEXT("COASTAL_W3_BOUNDARY_COMPONENT_FAILED edge=%s"), Spec.EdgeName);
            for (AActor* ExistingActor : BoundaryActors)
            {
                if (IsValid(ExistingActor))
                {
                    ExistingActor->Destroy();
                }
            }
            BoundaryActors.Reset();
            return false;
        }

        BoundaryActor->SetRootComponent(Box);
        BoundaryActor->SetActorLocation(Spec.Location);
        Box->SetBoxExtent(Spec.Extent);
        Box->SetCollisionProfileName(UCollisionProfile::BlockAll_ProfileName);
        Box->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        Box->SetCollisionResponseToAllChannels(ECR_Block);
        Box->SetGenerateOverlapEvents(false);
        Box->SetCanEverAffectNavigation(false);
        Box->ComponentTags.Add(FName(BoundaryTag));
        Box->RegisterComponent();
        BoundaryActors.Add(BoundaryActor);
    }

    bBoundariesApplied = true;
    const bool bProbePassed = VerifyBoundaryRays();
    UE_LOG(LogTemp, Display,
        TEXT("COASTAL_W3_BOUNDARY_APPLIED map=%s count=%d probe=%d"),
        *World->GetMapName(), BoundaryActors.Num(), bProbePassed ? 1 : 0);
    return true;
}

bool UCoastalW3WaterIntegration::VerifyBoundaryRays() const
{
    UWorld* World = GetWorld();
    if (!World || BoundaryActors.Num() != UE_ARRAY_COUNT(BoundarySpecs))
    {
        return false;
    }

    struct FBoundaryProbe
    {
        const TCHAR* EdgeName;
        FVector Start;
        FVector End;
    };

    const FBoundaryProbe Probes[] = {
        {TEXT("West"), FVector(-69900.0f, 0.0f, 100.0f), FVector(-70600.0f, 0.0f, 100.0f)},
        {TEXT("East"), FVector(69900.0f, 0.0f, 100.0f), FVector(70600.0f, 0.0f, 100.0f)},
        {TEXT("South"), FVector(0.0f, -39900.0f, 100.0f), FVector(0.0f, -40600.0f, 100.0f)},
        {TEXT("North"), FVector(0.0f, 39900.0f, 100.0f), FVector(0.0f, 40600.0f, 100.0f)}
    };

    bool bAllPassed = true;
    for (const FBoundaryProbe& Probe : Probes)
    {
        FHitResult Hit;
        FCollisionQueryParams QueryParams(TEXT("CoastalW3BoundaryProbe"), false);
        const bool bBlocked = World->LineTraceSingleByChannel(
            Hit,
            Probe.Start,
            Probe.End,
            ECC_Visibility,
            QueryParams);
        const AActor* HitActor = Hit.GetActor();
        const bool bBoundaryHit = bBlocked
            && HitActor
            && HitActor->ActorHasTag(FName(BoundaryTag));
        const FString HitActorName = HitActor ? HitActor->GetName() : TEXT("None");
        UE_LOG(LogTemp, Display,
            TEXT("COASTAL_W3_BOUNDARY_RAY edge=%s blocked=%d boundary=%d impact=(%.1f,%.1f,%.1f) actor=%s"),
            Probe.EdgeName,
            bBlocked ? 1 : 0,
            bBoundaryHit ? 1 : 0,
            Hit.ImpactPoint.X,
            Hit.ImpactPoint.Y,
            Hit.ImpactPoint.Z,
            *HitActorName);
        bAllPassed = bAllPassed && bBoundaryHit;
    }
    return bAllPassed;
}
