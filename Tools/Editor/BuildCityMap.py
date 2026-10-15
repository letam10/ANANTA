"""Assemble the city in a copy of ANANTA_Slice; never change the source map."""

import json
import os
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityLayout import generate, stage_groups
from CityScene import ACTORS, instance_group, lighting, camera, navigation
from CityInteriors import furnish, mission

MAP = "/Game/ANANTA/Maps/ANANTA_City"
SOURCE = "/Game/ANANTA/Maps/ANANTA_Slice"


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    stage = os.environ.get("ANANTA_CITY_STAGE", "hero")
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        assert levels.load_level(MAP)
    else:
        assert levels.new_level_from_template(MAP, SOURCE)
    if unreal.WorldPartitionBlueprintLibrary.get_actor_descs():
        raise RuntimeError("Restore the pre-partition build copy before regenerating the full layout")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    settings = world.get_world_settings()
    settings.set_editor_property("default_game_mode", unreal.ANANTACityGameMode)
    for actor in ACTORS.get_all_level_actors():
        protected = isinstance(actor, unreal.WorldSettings) or actor.get_class() == unreal.Brush.static_class()
        if not protected:
            ACTORS.destroy_actor(actor)
    layout = generate()
    included = stage_groups(layout, stage)
    for index, group in enumerate(included):
        instance_group(group, index)
    manifest = json.loads((PROJECT / "Assets/City/manifest.json").read_text(encoding="utf-8"))
    furnish(manifest)
    mission()
    lighting()
    navigation()
    camera("City_Camera_Cafe", (-23500, 500, 230), (-2, 155, 0))
    camera("City_Camera_Boulevard", (-24000, -600, 220), (1, 0, 0))
    camera("City_Camera_Apartment", (650, 2200, 190), (-3, 25, 0))
    camera("City_Camera_Transit", (22500, 1500, 250), (3, 35, 0))
    camera("City_Camera_Overview", (-10000, -18000, 32000), (-50, 50, 0))
    assert levels.save_current_level()
    report = {"map": MAP, "stage": stage, "layout": layout["audit"],
              "writtenGroups": len(included),
              "writtenInstances": sum(len(g["instances"]) for g in included),
              "actorCount": len(ACTORS.get_all_level_actors()), "interiors": ["Cafe", "Apartment"]}
    path = PROJECT / "Saved/QA/CityMapBuild.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_MAP_SAVED {report}")


if __name__ == "__main__":
    main()
