"""Local practical lighting for the four accessible civic rooms."""

import unreal
from CityCivicDistrict import SITES
from CityScene import spawn, box


def furnish():
    actors = []
    for name, x, y, _, _ in SITES[:4]:
        for index, (dx, dy) in enumerate(((2700, -900), (4250, -900), (2700, 900), (4250, 900))):
            prefix = f"District_Light_{name}_{index}"
            box(prefix + "_Housing", (x + dx, y + dy, 484), (170, 75, 10), "DistrictSteel", False)
            lamp = spawn(unreal.RectLight, prefix, (x + dx, y + dy, 475))
            lamp.set_actor_rotation(unreal.Rotator(pitch=-90, yaw=0, roll=0), False)
            light = lamp.light_component
            light.set_mobility(unreal.ComponentMobility.MOVABLE)
            light.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
            light.set_intensity(24000 if name in ("Police", "Fire") else 16000)
            light.set_editor_property("attenuation_radius", 2300)
            light.set_editor_property("source_width", 150)
            light.set_editor_property("source_height", 55)
            light.set_editor_property("use_temperature", True)
            light.set_editor_property("temperature", 3000 if name == "Bar" else 4200)
            light.set_editor_property("max_draw_distance", 4500)
            light.set_editor_property("max_distance_fade_range", 700)
            light.set_cast_shadows(True)
            lamp.set_editor_property("is_spatially_loaded", True)
            actors.append(lamp)
    return actors
