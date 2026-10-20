#include "QA/CoastalW3WaterIntegration.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace
{
    constexpr const TCHAR* TargetActorNames[] = {
        TEXT("CoastalBatch_269"),
        TEXT("CoastalBatch_465"),
        TEXT("CoastalBatch_716"),
        TEXT("CoastalBatch_808")
    };

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
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    const FString CommandLine = FCommandLine::Get();
    const FString MapName = World ? World->GetMapName() : FString();
    return World && World->IsGameWorld()
        && MapName.Contains(TEXT("ANANTA_CoastalCity"))
        && FParse::Param(*CommandLine, TEXT("CoastalW3Water"));
#endif
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
        UE_LOG(LogTemp, Display,
            TEXT("COASTAL_W3_WATER_APPLIED map=%s actors=%d components=%d material=%s"),
            *GetWorld()->GetMapName(), FoundActors.Num(), AppliedComponents, WaterMaterialPath);
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
