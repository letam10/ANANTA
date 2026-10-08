"""Read the persisted city sun value in a fresh editor process without modifying it."""

import json
import os
from pathlib import Path
import unreal


expected = int(os.environ.get("ANANTA_CITY_DAYLIGHT_LUX", "60000"))
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level("/Game/ANANTA/Maps/ANANTA_City"):
    raise RuntimeError("City map did not load")
editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lights = [actor for actor in editor.get_all_level_actors()
          if isinstance(actor, unreal.DirectionalLight) and actor.get_actor_label() == "City_Sun"]
if len(lights) != 1:
    raise RuntimeError("Expected one city sun")
actual = lights[0].light_component.intensity
if abs(actual - expected) > 0.1:
    raise RuntimeError(f"Persisted sun differs: expected {expected}, actual {actual}")
path = Path(unreal.Paths.project_saved_dir()).resolve() / f"QA/CityDaylightReadback{expected}.json"
path.write_text(json.dumps(dict(expectedLux=expected, actualLux=actual, mutated=False), indent=2),
                encoding="utf-8")
unreal.log(f"CITY_DAYLIGHT_READBACK_OK lux={actual}")
