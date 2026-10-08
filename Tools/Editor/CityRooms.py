"""Small accessible rooms with real entry openings and daylight windows."""

import unreal
from CityScene import box, prop, spawn


def window(prefix, x, y, width):
    box(prefix + "_Sill", (x, y, 40), (30, width, 50), "City_stone_wall_02")
    box(prefix + "_Header", (x, y, 300), (30, width, 70), "City_Teal")
    box(prefix + "_Glass", (x, y, 165), (3, width - 24, 200), "InteriorGlass")
    for side in (-1, 0, 1):
        box(prefix + f"_Mullion{side}", (x, y + side * (width / 2 - 6), 165),
            (16, 12, 200), "City_Dark")


def room(prefix, centre, size, face, entry):
    x, y = centre
    width, depth = size
    wall = "InteriorPlaster"
    box(prefix + "_Floor", (x, y, 5), (width, depth, 20), "InteriorFloor")
    box(prefix + "_Roof", (x, y, 352), (width + 50, depth + 50, 35), "Roof")
    box(prefix + "_Ceiling", (x, y, 331), (width, depth, 8), wall)
    for side in (-1, 1):
        box(prefix + f"_Side{side}", (x, y + side * depth / 2, 175), (width, 25, 320), wall)
        box(prefix + f"_Skirting{side}", (x, y + side * (depth / 2 - 17), 29),
            (width, 9, 28), "City_oak_veneer_01")
    box(prefix + "_Back", (x - face * width / 2, y, 175), (25, depth, 320), wall)
    front = x + face * width / 2
    prop(entry, prefix + "_Entry", (front, y, 15), 90 * face, collision=False)
    # Collision nam trong hai tru cua; khoang di 140 cm giu nguyen nhu mesh.
    for side in (-1, 1):
        box(prefix + f"_DoorPier{side}", (front, y + side * 135, 142),
            (25, 130, 254), "City_stone_wall_02")
        bay = (depth - 400) / 2
        window(prefix + f"_Window{side}", front, y + side * (200 + bay / 2), bay)
    box(prefix + "_DoorLintel", (front, y, 301), (35, 400, 68), "City_Teal")
    for xx in (x - width / 4, x + width / 4):
        lamp = spawn(unreal.RectLight, prefix + f"_AreaLight{int(xx)}", (xx, y, 314))
        lamp.set_actor_rotation(unreal.Rotator(pitch=-90, yaw=0, roll=0), False)
        light = lamp.light_component
        light.set_mobility(unreal.ComponentMobility.MOVABLE)
        light.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
        light.set_intensity(3200)
        light.set_editor_property("attenuation_radius", 1600)
        light.set_editor_property("max_draw_distance", 4500)
        light.set_editor_property("max_distance_fade_range", 800)
        light.set_editor_property("source_width", 120)
        light.set_editor_property("source_height", 40)
        light.set_editor_property("use_temperature", True)
        light.set_editor_property("temperature", 4200)
        light.set_cast_shadows(True)
        box(prefix + f"_LampFrame{int(xx)}", (xx, y, 323), (130, 50, 5), "City_Brass", False)
    return front, y
