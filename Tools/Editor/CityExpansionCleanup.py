"""Delete the previous generated city in saved batches without retaining its full geometry."""

import unreal
from CityExpansionData import GRID_EXTENT
from CityScene import ACTORS


def clear_previous(levels):
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    guids = [d.guid for d in descriptors if d.native_class.get_name() != "WorldPartitionHLOD"]
    preserved = {}
    removed = 0
    navigation_updated = False
    for offset in range(0, len(guids), 1000):
        batch = guids[offset:offset + 1000]
        unreal.WorldPartitionBlueprintLibrary.load_actors(batch)
        actors = list(ACTORS.get_all_level_actors())
        keep = []
        for actor in actors:
            label = actor.get_actor_label()
            generated = label.startswith("City_") and actor.get_components_by_class(
                unreal.HierarchicalInstancedStaticMeshComponent)
            if generated or label.startswith(("Expansion_", "Dressing_", "Landmark_", "District_", "Living_")):
                assert ACTORS.destroy_actor(actor)
                removed += 1
                continue
            keep.append(actor.get_editor_property("actor_guid"))
            if label in ("City_PlayerStart", "City_PlayerCar", "City_MissionGiver", "City_AnomalyFragment"):
                location = actor.get_actor_location()
                preserved[label] = [location.x, location.y, location.z]
            elif label == "City_NavigationBounds" and not navigation_updated:
                actor.modify()
                _, extent = actor.get_actor_bounds(False)
                scale = actor.get_actor_scale3d()
                actor.set_actor_scale3d(unreal.Vector(scale.x * (GRID_EXTENT + 2000) / extent.x,
                                                    scale.y * (GRID_EXTENT + 2000) / extent.y, scale.z))
                navigation_updated = True
        assert levels.save_current_level()
        assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        unreal.WorldPartitionBlueprintLibrary.unload_actors(keep)
        del actors
        unreal.SystemLibrary.collect_garbage()
        unreal.log(f"CITY_EXPANSION_REMOVED_BATCH {offset + len(batch)}/{len(guids)} removed={removed}")
    assert len(preserved) == 4, preserved
    assert navigation_updated, "Missing navigation bounds"
    return removed, preserved
