"""Replace only the old wheel blocks and update independent map counts."""

import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityScene import instance_group, mesh_asset
from CityExpansionLayout import generate


def main():
    mesh = mesh_asset("FerrisWheel")
    body = mesh.get_editor_property("body_setup")
    body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([
        item.guid for item in descriptors if item.native_class.get_name() != "WorldPartitionHLOD"
    ])
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removals = []
    existing = []
    for actor in subsystem.get_all_level_actors():
        if not actor.get_actor_label().startswith("City_"):
            continue
        for component in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            name = component.get_editor_property("static_mesh").get_name()
            if name == "SM_FerrisWheel":
                existing.append(actor)
            if name not in ("Cube", "SM_CityCubeNanite"):
                continue
            indices = []
            for index in range(component.get_instance_count()):
                position = component.get_instance_transform(index, True).translation
                if abs(position.x + 4550) <= 261 and abs(position.y + 4300) <= 1551 and 100 < position.z < 3401:
                    indices.append(index)
            if indices:
                removals.append((actor, component, indices))
    removed = sum(len(item[2]) for item in removals)
    assert removed == 282 or (removed == 0 and len(existing) == 1), (removed, len(existing))
    for actor, component, indices in removals:
        actor.modify()
        assert component.remove_instances(indices)
        if component.get_instance_count() == 0:
            assert subsystem.destroy_actor(actor)
    for actor in existing:
        assert subsystem.destroy_actor(actor)
    data = generate()
    group = next(item for item in data["groups"] if item["mesh"] == "FerrisWheel")
    actor = instance_group(group, "FerrisRepair")
    actor.set_editor_property("hlod_layer", unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD"))
    components = [component for actor in subsystem.get_all_level_actors()
                  if actor.get_actor_label().startswith("City_")
                  for component in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)]
    counts = (len(components), sum(component.get_instance_count() for component in components))
    assert counts == (len(data["groups"]), data["audit"]["instances"]), (counts, data["audit"])
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    path = PROJECT / "Saved/QA/CityExpansionApplied.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report.update(writtenGroups=counts[0], writtenInstances=counts[1], layout=data["audit"],
                  hlodRebuildRequired=True, runtimeVerified=False)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_FERRIS_APPLIED removedBlocks={removed} groups={counts[0]} instances={counts[1]}")


if __name__ == "__main__":
    main()
