"""Read saved level content back independently of the assembly process."""

import json
from pathlib import Path
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
MAP = "/Game/ANANTA/Maps/ANANTA_City"


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(MAP)
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    if descriptors:
        unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    expected = json.loads((PROJECT / "Saved/QA/CityMapBuild.json").read_text(encoding="utf-8"))
    components = []
    labels = set()
    errors = []
    for actor in actors:
        label = actor.get_actor_label()
        if label in labels:
            errors.append(f"Duplicate actor label: {label}")
        labels.add(label)
        components.extend(actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
    instance_count = sum(component.get_instance_count() for component in components)
    if instance_count != expected["writtenInstances"]:
        errors.append(f"Instances lost after reopening: {instance_count}/{expected['writtenInstances']}")
    for component in components:
        if not component.static_mesh:
            errors.append(f"Empty mesh {component.get_path_name()}")
        for index in range(component.get_num_materials()):
            if not component.get_material(index):
                errors.append(f"Unassigned material {component.get_path_name()} slot {index}")
    required = ("City_PlayerStart", "City_PlayerCar", "City_Crowd", "City_MissionGiver",
                "City_AnomalyFragment", "City_Cafe_Floor", "City_Apartment_Floor", "City_Sun", "City_Sky")
    for label in required:
        if label not in labels:
            errors.append(f"Missing required actor: {label}")
    if expected.get("stage") == "expanded":
        for name in expected["interiors"]:
            prefix = "City_" if name in ("Cafe", "Apartment") else "Expansion_"
            if prefix + name + "_Floor" not in labels:
                errors.append(f"Missing expanded venue floor: {name}")
        services = [actor for actor in actors if isinstance(actor, unreal.CityServiceInteractable)]
        identifiers = [str(actor.get_editor_property("interaction_id")) for actor in services]
        if len(identifiers) != 8 or len(set(identifiers)) != 8:
            errors.append(f"Expected eight unique service actors: {identifiers}")
    materials = unreal.EditorAssetLibrary.list_assets("/Game/ANANTA/City/Materials", recursive=True)
    graph_count = 0
    for path in materials:
        material = unreal.load_asset(path)
        if not isinstance(material, unreal.Material):
            continue
        graph_count += 1
        for prop in (unreal.MaterialProperty.MP_BASE_COLOR, unreal.MaterialProperty.MP_ROUGHNESS):
            node = unreal.MaterialEditingLibrary.get_material_property_input_node(material, prop)
            if not node:
                errors.append(f"Disconnected material output: {path} {prop}")
    report = {"map": MAP, "actorCount": len(actors), "instanceGroups": len(components),
              "instances": instance_count, "materialGraphs": graph_count, "errors": errors,
              "partitionActorDescriptors": len(descriptors) if descriptors else 0,
              "externalActorPackages": sum("/__ExternalActors__/" in str(item.actor_package)
                                           for item in descriptors) if descriptors else 0,
              "renderedGameplayVerified": False}
    (PROJECT / "Saved/QA/CityMapReadback.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if errors:
        raise RuntimeError("\n".join(errors))
    unreal.log(f"CITY_READBACK_OK {report}")


if __name__ == "__main__":
    main()
