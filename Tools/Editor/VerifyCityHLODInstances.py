"""Read saved instanced HLODs, checking geometry and source material references."""

import json
import os
from pathlib import Path
import unreal


MAP = "/Game/ANANTA/Maps/ANANTA_City"
LABEL = os.environ.get("ANANTA_HLOD_LABEL", "")


def main():
    layer = unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD")
    assert layer.get_editor_property("layer_type") == unreal.HLODLayerType.INSTANCING
    builder = layer.get_editor_property("hlod_builder_settings")
    assert not builder.get_editor_property("disallow_nanite")
    assert builder.get_editor_property("instance_filtering_type") == unreal.InstanceFilteringType.FILTER_NONE
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(MAP)
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    selected = [item for item in descriptors if item.native_class.get_name() == "WorldPartitionHLOD"
                and (not LABEL or str(item.label) == LABEL)]
    assert selected, "No matching HLOD descriptor"
    unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in selected])
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WorldPartitionHLOD)
    actors = [actor for actor in actors if not LABEL or actor.get_actor_label() == LABEL]
    errors = []
    entries = []
    if len(actors) != len(selected):
        errors.append(f"Loaded {len(actors)} of {len(selected)} HLODs")
    for actor in actors:
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
        rendered = [component for component in components if component.static_mesh]
        record = dict(label=actor.get_actor_label(), components=[], instances=0)
        if not rendered:
            errors.append(f"No geometry: {record['label']}")
        for component in rendered:
            if not isinstance(component, unreal.InstancedStaticMeshComponent):
                errors.append(f"Non-instanced proxy: {record['label']}")
                continue
            count = component.get_instance_count()
            if count < 1:
                errors.append(f"Empty instance group: {record['label']}")
            materials = [component.get_material(slot) for slot in range(component.get_num_materials())]
            if not materials or any(material is None for material in materials):
                errors.append(f"Missing source material: {record['label']}")
            record["instances"] += count
            record["components"].append(dict(mesh=component.static_mesh.get_path_name(), instances=count,
                                             materials=[material.get_path_name() if material else None
                                                        for material in materials]))
        entries.append(record)
    report = dict(map=MAP, selectedLabel=LABEL or None, descriptors=len(selected), actors=len(actors),
                  instances=sum(entry["instances"] for entry in entries), entries=entries, errors=errors,
                  naniteAllowed=True, instanceFiltering=False, fpsAccepted=False)
    name = "CityHLODInstancesSample.json" if LABEL else "CityHLODInstances.json"
    output = Path(unreal.Paths.project_saved_dir()).resolve() / "QA" / name
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert not errors, "\n".join(errors)
    unreal.log(f"CITY_HLOD_INSTANCES_OK actors={len(actors)} instances={report['instances']}")


if __name__ == "__main__":
    main()
