"""Apply one reversible daylight candidate after the HLOD writer has exited."""

import json
import os
from pathlib import Path
import unreal


def main():
    target = int(os.environ.get("ANANTA_CITY_DAYLIGHT_LUX", "40000"))
    if target not in (40000, 60000):
        raise ValueError("This review supports only the 40000 candidate or 60000 baseline")
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level("/Game/ANANTA/Maps/ANANTA_City"):
        raise RuntimeError("City map did not load")
    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    lights = [actor for actor in editor.get_all_level_actors()
              if isinstance(actor, unreal.DirectionalLight) and actor.get_actor_label() == "City_Sun"]
    if len(lights) != 1:
        raise RuntimeError("Expected one persistent City_Sun light")
    sun = lights[0]
    before = sun.light_component.intensity
    sun.modify()
    sun.light_component.modify()
    sun.light_component.set_intensity(target)
    if not level.save_current_level() or not unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True):
        raise RuntimeError("Daylight candidate did not save")
    actual = sun.light_component.intensity
    if abs(actual - target) > 0.1:
        raise RuntimeError("Daylight intensity readback differs")
    # Day chi la ung vien de so anh; chua doi gia tri nguon dung map.
    report = dict(beforeLux=before, requestedLux=target, actualLux=actual,
                  exposureChanged=False, materialChanged=False, visualAcceptance=False)
    path = Path(unreal.Paths.project_saved_dir()).resolve() / f"QA/CityDaylightReview{target}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_DAYLIGHT_REVIEW_APPLIED before={before} after={actual}")


if __name__ == "__main__":
    main()
