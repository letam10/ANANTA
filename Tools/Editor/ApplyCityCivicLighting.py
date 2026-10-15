"""Repair unlit civic interiors without regenerating city geometry."""

from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityCivicLighting import furnish


def main():
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    guids = [item.guid for item in descriptors if str(item.label).startswith("District_Light_")]
    if guids:
        unreal.WorldPartitionBlueprintLibrary.load_actors(guids)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in actors.get_all_level_actors():
        if actor.get_actor_label().startswith("District_Light_"):
            assert actors.destroy_actor(actor)
    assert len(furnish()) == 16
    assert level.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log("CITY_CIVIC_LIGHTING_OK lights=16")


if __name__ == "__main__":
    main()
