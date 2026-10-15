"""Reopen the saved city and verify every expected HLOD has renderable mesh data."""

import json
from pathlib import Path
import unreal


def main():
    level = "/Game/ANANTA/Maps/ANANTA_City"
    if not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(level):
        raise RuntimeError("Could not reopen city map")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    hlod_descriptors = [item for item in descriptors
                        if item.native_class.get_name() == "WorldPartitionHLOD"]
    unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in hlod_descriptors])
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    # HLOD bi API actor editor loai bo vi khong cho chinh sua trong Outliner.
    hlods = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WorldPartitionHLOD)
    errors = []
    entries = []
    build_path = Path(unreal.Paths.project_saved_dir()).resolve() / "QA/CityMapBuild.json"
    expanded = json.loads(build_path.read_text(encoding="utf-8")).get("stage") == "expanded"
    if len(hlods) != len(hlod_descriptors) or len(hlods) < (153 if expanded else 152):
        errors.append(f"HLOD count incomplete: actors={len(hlods)}, descriptors={len(hlod_descriptors)}")
    for actor in hlods:
        meshes = actor.get_components_by_class(unreal.StaticMeshComponent)
        rendered = [component for component in meshes if component.static_mesh]
        label = actor.get_actor_label()
        if not rendered:
            errors.append(f"HLOD has no built mesh: {label}")
        for component in rendered:
            for slot in range(component.get_num_materials()):
                if not component.get_material(slot):
                    errors.append(f"Missing HLOD material: {label} slot {slot}")
        entries.append({"label": label, "meshComponents": len(rendered)})
    report = {"map": level, "hlodActors": len(hlods), "hlodDescriptors": len(hlod_descriptors),
              "errors": errors, "actors": entries}
    path = Path(unreal.Paths.project_saved_dir()).resolve() / "QA/CityHLODReadback.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if errors:
        raise RuntimeError("\n".join(errors))
    unreal.log(f"CITY_HLOD_READBACK_OK actors={len(hlods)}")


if __name__ == "__main__":
    main()
