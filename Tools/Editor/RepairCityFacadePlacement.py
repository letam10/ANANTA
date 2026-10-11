"""Correct saved architecture facing and persist expanded navigation bounds."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityAssetOrientation import imported_yaw
from CityExpansionLayout import generate
from CityExpansionData import VENUES, GRID_EXTENT
from CityLayout import CAFE, APARTMENT


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([d.guid for d in descriptors
                                                      if d.native_class.get_name() != "WorldPartitionHLOD"])
    actors = {a.get_actor_label(): a for a in
              unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
    changed = 0
    count = 0
    for index, group in enumerate(generate()["groups"]):
        if imported_yaw(group["mesh"], 0) == 0:
            continue
        cx, cy = group["cell"]
        actor = actors[f"City_{cx}_{cy}_{group['mesh']}_{index}"]
        actor.modify()
        component = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)[0]
        component.modify()
        transforms = []
        for item in group["instances"]:
            transform = unreal.Transform()
            transform.translation = unreal.Vector(*item["location"])
            transform.rotation = unreal.Rotator(yaw=imported_yaw(group["mesh"], item["yaw"])).quaternion()
            transform.scale3d = unreal.Vector(*item["scale"])
            transforms.append(transform)
        assert component.get_instance_count() == len(transforms)
        assert component.batch_update_instances_transforms(0, transforms, True, True, True)
        changed += 1
        count += len(transforms)
    rooms = ({"id": "Cafe", **CAFE}, {"id": "Apartment", **APARTMENT}) + VENUES
    for room in rooms:
        prefix = "City_" if room["id"] in ("Cafe", "Apartment") else "Expansion_"
        entry = actors[prefix + room["id"] + "_Entry"]
        entry.modify()
        entry.set_actor_rotation(unreal.Rotator(yaw=90 * room["face"] + 180), False)
    nav = actors["City_NavigationBounds"]
    nav.modify()
    _, extent = nav.get_actor_bounds(False)
    scale = nav.get_actor_scale3d()
    nav.set_actor_scale3d(unreal.Vector(scale.x * (GRID_EXTENT + 2000) / extent.x,
                                      scale.y * (GRID_EXTENT + 2000) / extent.y, scale.z))
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(groups=changed, instances=count, entries=len(rooms), navigationExtent=GRID_EXTENT + 2000)
    (PROJECT / "Saved/QA/CityFacadeRepair.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_FACADE_REPAIR_SAVED {report}")


if __name__ == "__main__":
    main()
