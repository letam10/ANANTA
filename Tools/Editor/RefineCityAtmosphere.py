"""Apply the lighting refinement to saved actors without rebuilding the city."""

import unreal


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([d.guid for d in descriptors
                                                      if d.native_class.get_name() != "WorldPartitionHLOD"])
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    changed = 0
    for actor in actors:
        label = actor.get_actor_label()
        if isinstance(actor, unreal.RectLight) and "_AreaLight" in label:
            actor.modify()
            actor.light_component.set_intensity(3200)
            actor.light_component.set_editor_property("max_draw_distance", 4500)
            actor.light_component.set_editor_property("max_distance_fade_range", 800)
            changed += 1
        elif label == "City_Exposure":
            actor.modify()
            settings = actor.get_editor_property("settings")
            settings.set_editor_property("override_auto_exposure_bias", True)
            settings.set_editor_property("auto_exposure_bias", -0.35)
            actor.set_editor_property("settings", settings)
        elif label == "City_Sky":
            actor.modify()
            actor.light_component.set_intensity(1.15)
    assert changed == 16, changed
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log(f"CITY_ATMOSPHERE_REFINED roomLights={changed}")


if __name__ == "__main__":
    main()
