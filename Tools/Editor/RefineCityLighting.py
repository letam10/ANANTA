"""Update the persistent exposure volume without regenerating partitioned geometry."""

import unreal


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    volumes = [actor for actor in actors
               if isinstance(actor, unreal.PostProcessVolume) and actor.get_actor_label() == "City_Exposure"]
    if len(volumes) != 1:
        raise RuntimeError(f"Expected one city exposure volume, found {len(volumes)}")
    volume = volumes[0]
    volume.modify()
    settings = volume.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_max_brightness", True)
    settings.set_editor_property("auto_exposure_max_brightness", 16.0)
    volume.set_editor_property("settings", settings)
    if not unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True):
        raise RuntimeError("City exposure package could not be saved")
    value = volume.get_editor_property("settings").get_editor_property("auto_exposure_max_brightness")
    if value != 16.0:
        raise RuntimeError(f"Exposure readback differs: {value}")
    unreal.log("CITY_EXPOSURE_UPDATED maxEV=16")


if __name__ == "__main__":
    main()
