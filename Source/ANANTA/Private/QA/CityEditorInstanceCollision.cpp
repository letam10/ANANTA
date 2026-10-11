#include "QA/CityEditorTools.h"

#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"

#if WITH_EDITOR
#include "StaticMeshCompiler.h"
#endif

FString UCityEditorTools::FinalizeInstanceCollision(UHierarchicalInstancedStaticMeshComponent* Component)
{
#if WITH_EDITOR
    if (!Component || !Component->GetStaticMesh())
    {
        return TEXT("passed=0\nerror=Missing instance component or mesh\n");
    }
    const bool bCompiling = Component->GetStaticMesh()->IsCompiling();
    const bool bPhysicsBefore = Component->IsPhysicsStateCreated();
    const FVector ExtentBefore = Component->Bounds.BoxExtent;
    // Commandlet can luu bounds va body sau khi mesh/tree da san sang.
    FStaticMeshCompilingManager::Get().FinishCompilation({Component->GetStaticMesh()});
    Component->BuildTreeIfOutdated(false, true);
    Component->UpdateBounds();
    Component->RecreatePhysicsState();
    const bool bPhysicsAfter = Component->IsPhysicsStateCreated();
    return FString::Printf(TEXT("passed=%d\ncompilingBefore=%d\nphysicsBefore=%d\nphysicsAfter=%d\n")
        TEXT("extentBefore=%s\nextentAfter=%s\n"), bPhysicsAfter, bCompiling, bPhysicsBefore,
        bPhysicsAfter, *ExtentBefore.ToString(), *Component->Bounds.BoxExtent.ToString());
#else
    return TEXT("passed=0\nerror=Editor only\n");
#endif
}
