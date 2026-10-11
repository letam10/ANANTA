"""Apply two imported venue fixtures without rebuilding unrelated decoration actors."""

import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityVenueDressing import describe
from CityVenueFixtures import REMOVED_LABELS
from CityAssetOrientation import imported_yaw


def main():
    mesh_ids = {"ClinicSupplyCabinet", "TransitRouteDisplay"}
    items = {item["label"]: item for item in describe() if item["mesh"] in mesh_ids}
    if len(items) != 2:
        raise RuntimeError("Expected two detailed venue fixtures")
    meshes = {label: unreal.load_asset(f"/Game/ANANTA/City/Meshes/SM_{item['mesh']}")
              for label, item in items.items()}
    if not all(meshes.values()):
        raise RuntimeError("Import venue fixture meshes before applying the layout")
    mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not mesh_editor:
        mesh_editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    for label, item in items.items():
        if item["collision"] and mesh_editor.get_simple_collision_count(meshes[label]) == 0:
            raise RuntimeError(f"Required cabinet collision is missing: {label}")
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level("/Game/ANANTA/Maps/ANANTA_City"):
        raise RuntimeError("City map did not load")
    wanted = set(items) | REMOVED_LABELS
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors
                                                      if str(item.label) in wanted])
    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [actor for actor in editor.get_all_level_actors() if actor.get_actor_label() in wanted]
    matches = {label: [actor for actor in actors if actor.get_actor_label() == label] for label in items}
    if any(len(value) != 1 for value in matches.values()):
        raise RuntimeError("Venue source actors are missing or duplicated")
    for label, item in items.items():
        actor = matches[label][0]
        actor.modify()
        component = actor.static_mesh_component
        component.modify()
        component.set_static_mesh(meshes[label])
        # Xoa override cua primitive cu de hien dung vat lieu cua model moi.
        component.set_editor_property("override_materials", [])
        component.set_collision_profile_name("BlockAll" if item["collision"] else "NoCollision")
        actor.set_actor_location(unreal.Vector(*item["location"]), False, True)
        rotation = unreal.Rotator(pitch=0, yaw=imported_yaw(item["mesh"], item["yaw"]), roll=0)
        actor.set_actor_rotation(rotation, True)
        actor.set_actor_scale3d(unreal.Vector(*item["scale"]))
    removed = []
    for actor in actors:
        label = actor.get_actor_label()
        if label in REMOVED_LABELS:
            if not editor.destroy_actor(actor):
                raise RuntimeError(f"Could not remove replaced venue blockout: {label}")
            removed.append(label)
    if not level.save_current_level() or not unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True):
        raise RuntimeError("Venue fixture changes did not save")
    report = dict(updated=sorted(items), removed=sorted(removed),
                  hlodRebuildRequired=True, mapReadbackVerified=False)
    path = PROJECT / "Saved/QA/CityVenueFixturesApplied.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_VENUE_FIXTURES_APPLIED updated=2 removed={len(removed)}")


if __name__ == "__main__":
    main()
