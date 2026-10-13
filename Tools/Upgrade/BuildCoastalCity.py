"""Build the upgrade map only; the original ANANTA_Slice remains available."""

import json
import sys
from datetime import datetime
from pathlib import Path

import unreal


sys.path.insert(0, str(Path(__file__).parent))
from coastal_buildings import building, roof_access
from coastal_detail import apply_texture_detail
from coastal_landscape import coast, park, streets
from coastal_materials import palette
from coastal_rooms import dress
from coastal_scene import Scene
from coastal_transit import airfield, station


MAP = "/Game/ANANTA/Maps/ANANTA_CoastalCity"
VENUES = [
    ("Police_Station", "police", 2, "Cream"),
    ("Fire_Station", "fire", 2, "Terracotta"),
    ("Coast_Clinic", "clinic", 3, "White"),
    ("Harbor_Factory", "factory", 1, "Teal"),
    ("Coast_Restaurant", "restaurant", 2, "Terracotta"),
    ("Cinema", "cinema", 2, "Blue"),
    ("Arcade_Hall", "arcade", 2, "Teal"),
    ("Coast_Bar", "bar", 2, "Terracotta"),
    ("Seaside_Hotel", "hotel", 7, "Cream"),
    ("Beach_Cafe", "cafe", 2, "White"),
    ("West_Apartments", "home", 5, "Terracotta"),
    ("Makeup_Studio", "beauty", 3, "Cream"),
    ("Central_Park", "park", 0, "Grass"),
    ("Terrace_House", "home", 3, "Teal"),
    ("Opera_Theatre", "opera", 1, "White"),
    ("Workshop", "factory", 2, "Concrete"),
    ("Garden_Apartments", "home", 4, "Cream"),
    ("Dining_Hall", "restaurant", 2, "Terracotta"),
    ("Coastal_Loft", "home", 6, "Teal"),
    ("Harbor_Hotel", "hotel", 5, "White"),
    ("North_Apartments", "home", 5, "Concrete"),
    ("Transit_Cafe", "cafe", 2, "Cream"),
    ("Station_Office", "police", 2, "White"),
    ("City_Hotel", "hotel", 8, "Terracotta"),
    ("Playground", "park", 0, "Grass"),
]


def lighting(scene):
    sun = scene.spawn(unreal.DirectionalLight, "Sun", (0, 0, 50))
    sun.set_actor_rotation(unreal.Rotator(pitch=-40, yaw=-35), False)
    sun.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(60000)
    sky = scene.spawn(unreal.SkyLight, "SkyLight", (0, 0, 30))
    sky.light_component.set_editor_property("real_time_capture", True)
    sky.light_component.set_intensity(1)
    scene.spawn(unreal.SkyAtmosphere, "Atmosphere", (0, 0, 0))
    fog = scene.spawn(unreal.ExponentialHeightFog, "Fog", (0, 0, 0))
    fog.component.set_editor_property("fog_density", 0.006)
    fog.component.set_editor_property("fog_height_falloff", 0.3)
    volume = scene.spawn(unreal.PostProcessVolume, "Exposure", (0, 0, 0))
    volume.set_editor_property("unbound", True)
    settings = volume.settings
    settings.override_auto_exposure_min_brightness = True
    settings.override_auto_exposure_max_brightness = True
    settings.auto_exposure_min_brightness = 5
    settings.auto_exposure_max_brightness = 12
    settings.override_auto_exposure_speed_up = True
    settings.override_auto_exposure_speed_down = True
    settings.auto_exposure_speed_up = 5
    settings.auto_exposure_speed_down = 5
    settings.override_auto_exposure_bias = True
    settings.auto_exposure_bias = 0
    volume.settings = settings


def main():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        unreal.EditorLoadingAndSavingUtils.load_map(MAP)
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for actor in subsystem.get_all_level_actors():
            if actor.get_actor_label().startswith("Coast_"):
                subsystem.destroy_actor(actor)
    else:
        assert unreal.EditorLevelLibrary.new_level(MAP)
    materials = palette()
    apply_texture_detail(materials)
    scene = Scene(materials)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", unreal.CoastalGameMode)
    streets(scene)
    coast(scene)
    station(scene)
    airfield(scene)
    buildings = []
    for index, (name, kind, floors, color) in enumerate(VENUES):
        x = -144 + (index % 5) * 64
        y = -144 + (index // 5) * 64
        if kind == "park":
            park(scene, x, y)
            if name == "Playground":
                scene.model("FerrisWheel", (x + 10, y + 8, 2))
            continue
        data = building(scene, name, (x, y), floors, color,
                        width=24 if kind in ("opera", "factory", "cinema") else 20)
        data["kind"] = kind
        dress(scene, data, kind)
        if kind == "hotel":
            roof_access(scene, data, pool=True)
        if name == "Coast_Clinic":
            roof_access(scene, data, helipad=True)
        if kind == "opera":
            scene.model("OperaShells", (x, y, data["roof_m"] + 0.2), yaw=90)
        if kind in ("police", "fire", "clinic"):
            vehicle = {"police": "PoliceCar", "fire": "FireEngine", "clinic": "Ambulance"}[kind]
            scene.vehicle(vehicle, (x + 17, y - 10, 2 + scene.dimensions[vehicle][2] * 0.4), yaw=90)
        buildings.append(data)
    for index in range(5):
        scene.action(f"Collectible_Book_{index}", (-12 + index * 1.5, -29, 2),
                     "Book collected", kind=3, model="Book")
    scene.spawn(unreal.PlayerStart, "PlayerStart", (-16, -32, 3.1), yaw=90)
    lighting(scene)
    assert unreal.EditorLevelLibrary.save_current_level()
    output = Path(unreal.Paths.project_dir()) / "Saved" / "Upgrade"
    report = {"built_at": datetime.now().isoformat(), "map": MAP, "buildings": buildings,
              "batches": len(scene.batches), "placements": scene.placements}
    (output / "city-layout.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"COASTAL_MAP_OK {len(buildings)} enterable buildings, "
               f"{len(scene.placements)} instances / {len(scene.batches)} HISM batches")


if __name__ == "__main__":
    main()
