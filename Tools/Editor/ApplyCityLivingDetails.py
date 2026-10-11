"""Replace only Living_ actors, including unloaded world partition instances."""

import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityLivingDetails import describe, furnish
from CityScene import mesh_asset, material_asset


def main():
    items = describe()
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    for item in items:
        mesh = mesh_asset(item["mesh"])
        if item["collision"] and editor.get_simple_collision_count(mesh) == 0:
            raise RuntimeError(f"Missing simple collision: {item['mesh']}")
        if item["material"]:
            material_asset(item["material"])
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level("/Game/ANANTA/Maps/ANANTA_City"):
        raise RuntimeError("City map did not load")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors
                                                      if str(item.label).startswith("Living_")])
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = []
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        if label.startswith("Living_"):
            if not actors.destroy_actor(actor):
                raise RuntimeError(f"Could not remove {label}")
            removed.append(label)
    created = furnish()
    labels = [actor.get_actor_label() for actor in created]
    assert len(labels) == len(set(labels)) == len(items)
    assert set(labels) == {item["label"] for item in items}
    if not level.save_current_level() or not unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True):
        raise RuntimeError("Living details did not save")
    report = dict(created=labels, removed=removed, mapReadbackVerified=False,
                  runtimeVerified=False, hlodRebuildRequired=True)
    path = PROJECT / "Saved/QA/CityLivingAssets/applied.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_LIVING_APPLIED count={len(created)}")


if __name__ == "__main__":
    main()
