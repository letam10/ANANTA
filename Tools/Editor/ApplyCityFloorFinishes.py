"""Apply sourced PBR flooring to four venues after the active HLOD build ends."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import create_material
from CityScene import ACTORS, material_asset
from CityInteriorFinishes import FLOORS


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([d.guid for d in descriptors
                                                      if d.native_class.get_name() != "WorldPartitionHLOD"])
    matches = [a for a in ACTORS.get_all_level_actors() if a.get_actor_label() in FLOORS]
    assert len(matches) == len(FLOORS), [a.get_actor_label() for a in matches]
    source = PROJECT / "Assets/City"
    catalog = json.loads((source / "interior_finish_catalog.json").read_text(encoding="utf-8"))
    for item in catalog["materials"]:
        create_material(item, source)
    for name in set(FLOORS.values()):
        material_asset(name)
    changed = []
    for actor in matches:
        component = actor.static_mesh_component
        target = material_asset(FLOORS[actor.get_actor_label()])
        if component.get_material(0) == target:
            continue
        actor.modify()
        component.modify()
        component.set_material(0, target)
        changed.append(actor.get_actor_label())
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(floors=FLOORS, changed=changed, hlodRebuildRequired=bool(changed),
                  independentReadbackVerified=False, runtimeVerified=False)
    path = PROJECT / "Saved/QA/CityFloorFinishesApplied.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_FLOOR_FINISHES_APPLIED count={len(changed)}")


if __name__ == "__main__":
    main()
