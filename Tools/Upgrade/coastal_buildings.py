"""Door clearances, facade rhythm and roof access derived from floor dimensions."""

import unreal

from coastal_windows import ground_wall


FLOOR_HEIGHT = 3.2
FLOOR_Z = 2.0
DOOR_CLEARANCE = 0.98


def building(scene, name, center, floors, color, width=20, depth=22):
    x, y = center
    front = y - depth / 2
    height = floors * FLOOR_HEIGHT
    z = FLOOR_Z
    scene.box((x, y, z - 0.12), (width + 0.4, depth + 0.4, 0.24), "Concrete")
    for side in (-1, 1):
        ground_wall(scene, (x + side * width / 2, y, z), depth, color, yaw=90)
        if floors > 1:
            scene.box((x + side * width / 2, y, z + (height + FLOOR_HEIGHT) / 2),
                      (0.22, depth, height - FLOOR_HEIGHT), color)
    scene.box((x, y + depth / 2, z + height / 2), (width, 0.22, height), color)
    ground_wall(scene, (x, front, z), width, color, doorway=True)
    door = scene.action(f"{name}_Door", (x, front - 0.12, z), "", kind=1, model="Door", yaw=90)
    # Mesh local Y là chiều ngang cửa: xoay 90° để mặt cửa hướng về phía phố.
    door.set_actor_location(unreal.Vector((x - 0.45) * 100, (front - 0.12) * 100, z * 100), False, False)
    door.mesh.set_relative_location(unreal.Vector(0, -45, 0), False, False)
    for floor in range(1, floors):
        level_z = z + floor * FLOOR_HEIGHT
        scene.box((x, y, level_z - 0.09), (width, depth, 0.18), "Plaster")
        scene.box((x, front, level_z + FLOOR_HEIGHT / 2), (width, 0.22, FLOOR_HEIGHT), color)
        scene.box((x, front - 0.13, level_z), (width + 0.5, 0.42, 0.13), "White")
        count = int((width - 2) / 3)
        for index in range(count):
            wx = x + (index - (count - 1) / 2) * 3
            scene.box((wx, front - 0.16, level_z + 1.65), (2, 0.06, 1.65), "Glass", collision=False)
            for side in (-1, 1):
                scene.box((wx + side * 1.025, front - 0.2, level_z + 1.65),
                          (0.075, 0.12, 1.75), "White", collision=False)
            scene.box((wx, front - 0.2, level_z + 0.8), (2.15, 0.18, 0.1), "White", collision=False)
    roof_z = z + height
    scene.box((x, y, roof_z), (width + 0.5, depth + 0.5, 0.22), "White")
    scene.box((x, front - 1.1, z + 2.7), (6, 2.2, 0.12), "Teal", collision=False)
    scene.box((x, front - 0.28, z + 3.8), (8.5, 0.14, 0.8), "Blue", collision=False)
    scene.text(f"{name}_Sign", (x, front - 0.38, z + 3.65), name.replace("_", " "), yaw=-90)
    for side in (-1, 1):
        scene.model("PotPlant", (x + side * 1.8, front - 1.3, z), scale=(1.7, 1.7, 1.7))
    return {"name": name, "center_m": [x, y], "width_m": width, "depth_m": depth,
            "floors": floors, "ground_m": z, "roof_m": roof_z,
            "entrance_m": [x, front - 1.5, z + 0.96]}


def roof_access(scene, data, pool=False, helipad=False):
    x, y = data["center_m"]
    top = data["roof_m"] + 0.12
    half_width = data["width_m"] / 2
    half_depth = data["depth_m"] / 2
    for side in (-1, 1):
        scene.box((x + side * half_width, y, top + 0.45), (0.18, 2 * half_depth, 0.9), "Concrete")
        scene.box((x, y + side * half_depth, top + 0.45), (2 * half_width, 0.18, 0.9), "Concrete")
    lift = scene.action(data["name"] + "_RoofLift", (x, y - 8, FLOOR_Z),
                        "Roof terrace", kind=4)
    lift.destination = unreal.Vector(x * 100, (y - 8) * 100, (top + 0.96) * 100)
    down = scene.action(data["name"] + "_GroundLift", (x, y - 8, top),
                        "Ground floor", kind=4)
    down.destination = unreal.Vector(x * 100, (y - 8) * 100, (FLOOR_Z + 0.96) * 100)
    if pool:
        for side in (-1, 1):
            scene.box((x - 2 + side * 3.5, y + 3, top + 0.45), (0.25, 4.8, 0.9), "White")
            scene.box((x - 2, y + 3 + side * 2.4, top + 0.45), (7.25, 0.25, 0.9), "White")
        plane = unreal.load_asset("/Engine/BasicShapes/Plane")
        from coastal_materials import ocean
        scene.instance(plane, ocean(), (x - 2, y + 3, top + 0.65), (7, 4.6, 1), collision=False)
        for offset in (-3, 0, 3):
            scene.model("Chair", (x + offset, y - 1, top))
    if helipad:
        scene.box((x - 3, y + 3, top + 0.04), (11, 11, 0.08), "Road")
        for side in (-1, 1):
            scene.box((x - 3 + side * 1.3, y + 3, top + 0.09), (0.25, 3.2, 0.01), "White", collision=False)
        scene.box((x - 3, y + 3, top + 0.09), (2.8, 0.25, 0.01), "White", collision=False)
        scene.model("Helicopter", (x - 3, y + 3, top + 0.1), yaw=90)
