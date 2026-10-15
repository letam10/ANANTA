#include "QA/CityEditorTools.h"

#include "Engine/World.h"
#include "NavigationSystem.h"
#include "NavMesh/RecastNavMesh.h"

ARecastNavMesh* UCityEditorTools::EnsureNavigation(UWorld* World)
{
#if WITH_EDITOR
    if (!World)
    {
        return nullptr;
    }
    auto* System = FNavigationSystem::GetCurrent<UNavigationSystemV1>(World);
    if (!System)
    {
        FNavigationSystem::AddNavigationSystemToWorld(*World, FNavigationSystemRunMode::EditorMode);
        System = FNavigationSystem::GetCurrent<UNavigationSystemV1>(World);
    }
    // Recast la NotPlaceable; de NavigationSystem tao va dang ky actor dung cach.
    return System ? Cast<ARecastNavMesh>(System->GetDefaultNavDataInstance(FNavigationSystem::Create)) : nullptr;
#else
    return nullptr;
#endif
}
