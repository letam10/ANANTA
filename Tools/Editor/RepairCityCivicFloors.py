"""Separate the four paving/wood surfaces without moving props or replacing the city."""

import json
from pathlib import Path
import sys
import unreal


ROOT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityCivicDistrict import SITES


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([
        item.guid for item in descriptors if item.native_class.get_name() != "WorldPartitionHLOD"
    ])
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    repaired = []
    for actor in actors.get_all_level_actors():
        if not actor.get_actor_label().startswith("City_"):
            continue
        for component in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            material = component.get_material(0)
            if not material or material.get_name() != "M_DistrictPaving":
                continue
            for index in range(component.get_instance_count()):
                transform = component.get_instance_transform(index, True)
                position = transform.translation
                site = next((name for name, x, y, _, _ in SITES[:4]
                             if abs(position.x - x - 3400) < 0.1 and abs(position.y - y) < 0.1), None)
                if not site:
                    continue
                assert abs(transform.scale3d.x - 41) < 0.01 and abs(transform.scale3d.y - 44) < 0.01
                actor.modify()
                transform.translation = unreal.Vector(position.x, position.y, 7)
                transform.scale3d = unreal.Vector(41, 44, 0.14)
                assert component.update_instance_transform(index, transform, True, True, True)
                actual = component.get_instance_transform(index, True)
                assert abs(actual.translation.z + actual.scale3d.z * 50 - 14) < 0.001
                repaired.append(site)
    assert sorted(repaired) == sorted(site[0] for site in SITES[:4]), repaired
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(repaired=repaired, pavingTopCm=14, woodTopCm=15, requiresGPUReview=True)
    (ROOT / "Saved/QA/CityCivicFloors.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_CIVIC_FLOORS_REPAIRED count=4 separationCm=1")


if __name__ == "__main__":
    main()
