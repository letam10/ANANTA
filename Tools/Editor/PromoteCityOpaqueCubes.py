"""Keep cube geometry/collision/materials while moving opaque city instances onto Nanite."""

import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityScene import promote_cube_component


def main():
    path = "/Game/ANANTA/City/Meshes/SM_CityCubeNanite"
    mesh = unreal.load_asset(path)
    if not mesh:
        mesh = unreal.EditorAssetLibrary.duplicate_asset("/Engine/BasicShapes/Cube", path)
    assert mesh
    settings = mesh.get_editor_property("nanite_settings")
    settings.set_editor_property("enabled", True)
    mesh.set_editor_property("nanite_settings", settings)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([
        item.guid for item in descriptors if item.native_class.get_name() != "WorldPartitionHLOD"
    ])
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    components = 0
    instances = 0
    for actor in actors:
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            if promote_cube_component(component):
                actor.modify()
                components += 1
                instances += component.get_instance_count() if isinstance(
                    component, unreal.InstancedStaticMeshComponent) else 1
    assert components > 1000 and instances > 100000, (components, instances)
    assert level.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(components=components, instances=instances, geometryChanged=False,
                  materialChanged=False, collisionChanged=False, fpsAccepted=False, hlodRebuildRequired=True)
    (PROJECT / "Saved/QA/CityNaniteCubes.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_NANITE_CUBES_OK components={components} instances={instances}")


if __name__ == "__main__":
    main()
