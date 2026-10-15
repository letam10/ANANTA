"""Replace only the workshop blockout actors after importing the audited meshes."""

import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityVenueDressing import describe
from CityAssetOrientation import imported_yaw


def main():
    items = {item["label"]: item for item in describe() if item["mesh"].startswith("Workshop")}
    if len(items) != 2:
        raise RuntimeError("Expected two detailed workshop props")
    meshes = {label: unreal.load_asset(f"/Game/ANANTA/City/Meshes/SM_{item['mesh']}")
              for label, item in items.items()}
    if not all(meshes.values()):
        raise RuntimeError("Import workshop detail meshes before applying the layout")
    mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not mesh_editor:
        mesh_editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    for label, item in items.items():
        if item["collision"] and mesh_editor.get_simple_collision_count(meshes[label]) == 0:
            raise RuntimeError(f"Required workshop collision is missing: {label}")
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level("/Game/ANANTA/Maps/ANANTA_City"):
        raise RuntimeError("City map did not load")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    selected = [item.guid for item in descriptors if str(item.label).startswith("Dressing_Workshop_")]
    unreal.WorldPartitionBlueprintLibrary.load_actors(selected)
    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [actor for actor in editor.get_all_level_actors()
              if actor.get_actor_label().startswith("Dressing_Workshop_")]
    matches = {label: [actor for actor in actors if actor.get_actor_label() == label] for label in items}
    if any(len(value) != 1 for value in matches.values()):
        raise RuntimeError("Workshop source actors are missing or duplicated")
    for label, item in items.items():
        actor = matches[label][0]
        actor.modify()
        component = actor.static_mesh_component
        component.modify()
        component.set_static_mesh(meshes[label])
        # Bo material cua khoi prototype de dung day du slot cua model moi.
        component.set_editor_property("override_materials", [])
        component.set_collision_profile_name("BlockAll" if item["collision"] else "NoCollision")
        actor.set_actor_location(unreal.Vector(*item["location"]), False, True)
        rotation = unreal.Rotator(pitch=0, yaw=imported_yaw(item["mesh"], item["yaw"]), roll=0)
        actor.set_actor_rotation(rotation, True)
        actor.set_actor_scale3d(unreal.Vector(*item["scale"]))
    rails = [actor for actor in actors if actor.get_actor_label().startswith("Dressing_Workshop_ToolRail")]
    for actor in rails:
        if not editor.destroy_actor(actor):
            raise RuntimeError("Could not remove a replaced workshop tool rail")
    # Can luu level de giu viec xoa external actor qua lan mo lai.
    if not level.save_current_level() or not unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True):
        raise RuntimeError("Workshop changes did not save")
    report = dict(updated=sorted(items), removedRails=len(rails), mapReadbackVerified=False,
                  hlodRebuildRequired=True)
    path = PROJECT / "Saved/QA/CityWorkshopDetailApply.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_WORKSHOP_DETAIL_APPLIED updated=2 removedRails={len(rails)}")


if __name__ == "__main__":
    main()
