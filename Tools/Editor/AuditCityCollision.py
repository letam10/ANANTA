"""Load the complete latest city and inspect collision bodies and road support."""

from pathlib import Path
import unreal


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([
        item.guid for item in descriptors if item.native_class.get_name() != "WorldPartitionHLOD"
    ])
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    report = unreal.CityEditorTools.audit_loaded_collision(world)
    path = Path(unreal.Paths.project_saved_dir()) / "QA/CityWholeMapCollision.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    assert report.startswith("passed=1\n"), f"City collision audit failed; see {path}"
    unreal.log("CITY_WHOLE_MAP_COLLISION_OK " + report.replace("\n", " "))


if __name__ == "__main__":
    main()
