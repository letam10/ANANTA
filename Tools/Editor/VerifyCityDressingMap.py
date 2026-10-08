"""Verify saved dressing, room lighting and shared window material after reopening."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityVenueDressing import describe as venue_items
from CityStreetLandmarks import describe as landmark_items
from CityAssetOrientation import imported_yaw


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([d.guid for d in descriptors
                                                      if d.native_class.get_name() != "WorldPartitionHLOD"])
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    dressing = [a for a in actors if a.get_actor_label().startswith(("Dressing_", "Landmark_"))]
    expected = {item["label"]: item for item in venue_items() + landmark_items()}
    errors = []
    labels = [actor.get_actor_label() for actor in dressing]
    if len(labels) != len(expected) or len(set(labels)) != len(expected) or set(labels) != set(expected):
        errors.append("Saved dressing labels do not match the authored props")
    for actor in dressing:
        item = expected.get(actor.get_actor_label())
        if not item:
            continue
        location = actor.get_actor_location()
        if any(abs(a - b) > 0.1 for a, b in zip((location.x, location.y, location.z), item["location"])):
            errors.append(f"Incorrect saved position: {actor.get_actor_label()}")
        scale = actor.get_actor_scale3d()
        if any(abs(a - b) > 0.001 for a, b in zip((scale.x, scale.y, scale.z), item["scale"])):
            errors.append(f"Incorrect saved scale: {actor.get_actor_label()}")
        yaw = imported_yaw(item["mesh"], item["yaw"])
        if abs((actor.get_actor_rotation().yaw - yaw + 180) % 360 - 180) > 0.1:
            errors.append(f"Incorrect saved rotation: {actor.get_actor_label()}")
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
        if not components or not components[0].static_mesh:
            errors.append(f"Missing saved mesh: {actor.get_actor_label()}")
        elif components[0].static_mesh.get_name() != ("Cube" if item["mesh"] == "Cube" else f"SM_{item['mesh']}"):
            errors.append(f"Incorrect saved mesh: {actor.get_actor_label()}")
        for component in components:
            profile = "BlockAll" if item["collision"] else "NoCollision"
            if str(component.get_collision_profile_name()) != profile:
                errors.append(f"Incorrect saved collision profile: {actor.get_actor_label()}")
            if any(not component.get_material(i) for i in range(component.get_num_materials())):
                errors.append(f"Missing material: {actor.get_actor_label()}")
    lights = [a for a in actors if isinstance(a, unreal.RectLight) and "_AreaLight" in a.get_actor_label()]
    if len(lights) != 16 or any(abs(a.light_component.intensity - 3200) > 0.1 for a in lights):
        errors.append("Room light values were not saved")
    services = [a for a in actors if isinstance(a, unreal.CityServiceInteractable)]
    if len(services) != 8:
        errors.append("Eight service actors must remain")
    root = "/Game/ANANTA/City"
    window = unreal.load_asset(root + "/Materials/M_City_WindowGlass")
    if not unreal.MaterialEditingLibrary.get_material_property_input_node(
            window, unreal.MaterialProperty.MP_EMISSIVE_COLOR):
        errors.append("Window emissive graph is disconnected")
    report = dict(dressing=len(dressing), lights=len(lights), services=len(services), errors=errors)
    (PROJECT / "Saved/QA/CityDressingReadback.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert not errors, errors
    unreal.log(f"CITY_DRESSING_READBACK_OK {report}")


if __name__ == "__main__":
    main()
