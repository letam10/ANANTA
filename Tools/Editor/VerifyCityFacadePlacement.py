"""Read back corrected architectural transforms and navigation coverage."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityExpansionLayout import generate
from CityExpansionData import VENUES
from CityLayout import CAFE, APARTMENT


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([d.guid for d in descriptors
                                                      if d.native_class.get_name() != "WorldPartitionHLOD"])
    actors = {a.get_actor_label(): a for a in
              unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
    samples = 0
    groups = 0
    errors = []
    for index, group in enumerate(generate()["groups"]):
        mesh = group["mesh"]
        if not mesh.startswith("Facade") and mesh not in ("Storefront", "Balcony", "Cornice"):
            continue
        cx, cy = group["cell"]
        actor = actors[f"City_{cx}_{cy}_{mesh}_{index}"]
        component = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)[0]
        if component.get_instance_count() != len(group["instances"]):
            errors.append(f"Instance count changed: {actor.get_actor_label()}")
            continue
        groups += 1
        for item_index in {0, len(group["instances"]) // 2, len(group["instances"]) - 1}:
            item = group["instances"][item_index]
            actual = component.get_instance_transform(item_index, True)
            yaw = actual.rotation.rotator().yaw
            difference = (yaw - item["yaw"] - 180 + 180) % 360 - 180
            if abs(difference) > 0.01:
                errors.append(f"Incorrect saved facing: {actor.get_actor_label()} index={item_index}")
            samples += 1
    rooms = ({"id": "Cafe", **CAFE}, {"id": "Apartment", **APARTMENT}) + VENUES
    for room in rooms:
        prefix = "City_" if room["id"] in ("Cafe", "Apartment") else "Expansion_"
        entry = actors[prefix + room["id"] + "_Entry"]
        difference = (entry.get_actor_rotation().yaw - 90 * room["face"]) % 360 - 180
        if abs(difference) > 0.01:
            errors.append(f"Incorrect entry facing: {entry.get_actor_label()}")
    _, extent = actors["City_NavigationBounds"].get_actor_bounds(False)
    if min(extent.x, extent.y) < 85999:
        errors.append(f"Navigation coverage was not saved: {extent}")
    report = dict(groups=groups, transformSamples=samples, entries=len(rooms),
                  navigationExtent=[extent.x, extent.y, extent.z], errors=errors)
    (PROJECT / "Saved/QA/CityFacadePlacementReadback.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert not errors, errors
    unreal.log(f"CITY_FACADE_PLACEMENT_READBACK_OK {report}")


if __name__ == "__main__":
    main()
