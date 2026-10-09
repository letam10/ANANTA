"""Move the authored starter car to its curb bay without touching player saves."""

from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityScene import box


def main():
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    guids = [item.guid for item in descriptors if str(item.label) == "City_PlayerCar"
             or str(item.label).startswith("TrafficParking_")]
    if guids:
        unreal.WorldPartitionBlueprintLibrary.load_actors(guids)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    moved = 0
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        if label == "City_PlayerCar":
            actor.modify()
            actor.set_actor_location(unreal.Vector(-22000, 790, 70), False, True)
            moved += 1
        elif label.startswith("TrafficParking_"):
            assert actors.destroy_actor(actor)
    assert moved == 1
    for index, y in enumerate((685, 895)):
        actor = box(f"TrafficParking_Line{index}", (-22000, y, 3), (540, 5, 1), "RoadMark", False)
        actor.set_editor_property("is_spatially_loaded", True)
    assert level.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log("CITY_TRAFFIC_PARKING_OK authoredCarY=790 savedPlayerCarUntouched=1")


if __name__ == "__main__":
    main()
