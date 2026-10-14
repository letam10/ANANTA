"""Connected streets, promenade, open sea and finite playable boundaries."""

import math

import unreal

from coastal_materials import ocean


ROADS = (-176, -112, -48, 16, 80, 144)


def streets(scene):
    scene.box((-24.5, -20, 1), (401, 470, 2), "Concrete")
    for road in ROADS:
        scene.box((road, -16, 2.01), (14, 384, 0.02), "Road")
        scene.box((-16, road, 2.02), (384, 14, 0.02), "Road")
        for side in (-1, 1):
            edges = (-208,) + ROADS + (176,)
            for start, end in zip(edges, edges[1:]):
                lower = start if start == -208 else start + 7
                upper = end if end == 176 else end - 7
                midpoint = (lower + upper) / 2
                length = upper - lower
                scene.box((road + side * 8.5, midpoint, 2.08), (3, length, 0.16), "Sidewalk")
                scene.box((midpoint, road + side * 8.5, 2.08), (length, 3, 0.16), "Sidewalk")
        for coordinate in range(-196, 177, 8):
            if all(abs(coordinate - crossing) > 12 for crossing in ROADS):
                scene.box((road, coordinate, 2.035), (0.13, 3, 0.01), "Yellow", collision=False)
                scene.box((coordinate, road, 2.045), (3, 0.13, 0.01), "Yellow", collision=False)
        for coordinate in range(-192, 170, 32):
            if all(abs(coordinate - crossing) > 12 for crossing in ROADS):
                scene.model("StreetLamp", (road + 8.4, coordinate, 2.16), yaw=180)
                scene.model("StreetBin", (road + 8.6, coordinate + 2, 2.16))
                if coordinate % 64 == 0:
                    scene.model("ParkingMeter", (road + 6.4, coordinate + 3.2, 2.16),
                                yaw=180, scale=(0.8, 0.8, 0.8), collision=False)
    for x in ROADS:
        for y in ROADS:
            for side in (-1, 1):
                for stripe in range(10):
                    scene.box((x - 4.5 + stripe, y + side * 10.3, 2.045),
                              (0.5, 2.3, 0.01), "White", collision=False)
                scene.model("TrafficLight", (x + side * 8.8, y - side * 8.8, 2.16),
                            yaw=90 if side > 0 else -90)
    for coordinate in ROADS[:-1]:
        scene.model("FireHydrant", (coordinate + 4.4, coordinate + 4.4, 2.16),
                    scale=(0.8, 0.8, 0.8), collision=False)
    # Tuyến cao tốc phía nam dùng bốn làn; dải phân cách tách hai chiều.
    scene.box((-16, -223, 2.01), (430, 16, 0.02), "Road")
    scene.box((-16, -223, 2.3), (430, 0.7, 0.6), "Concrete")
    scene.box((144, -209, 2.015), (14, 28, 0.02), "Road")
    for x in range(-215, 177, 5):
        for side in (-1, 1):
            scene.model("Railing", (x, -223 + side * 9, 2), collision=True)
    scene.text("Highway_Sign", (135, -213, 6), "COAST HIGHWAY", yaw=-90, size=0.8)


def coast(scene):
    scene.box((180, -16, 1), (8, 430, 2), "Concrete")
    scene.box((180, -16, 2.08), (8, 430, 0.16), "Sidewalk")
    # Mép bãi cát xuống 2 m trong 30 m: góc dốc = atan(2 / 30).
    slope = math.degrees(math.atan2(2, 30))
    scene.box((195, -16, 0.9), (math.hypot(30, 2), 430, 0.2), "Sand", pitch=-slope)
    plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    scene.instance(plane, ocean(), (1210, 0, 0), (2000, 2000, 1), collision=False)
    scene.box((207, -115, 0.7), (14, 3.8, 0.22), "Wood")
    scene.box((187, -115, 1.4), (26, 3.8, 0.22), "Wood", pitch=-slope)
    scene.vehicle("Rowboat", (211, -117.5, 0.48), yaw=0, boat=True)
    scene.vehicle("Rowboat", (211, -112.5, 0.48), yaw=0, boat=True)
    scene.model("Lifebuoy", (207.5, -115, 1.55), yaw=90, scale=(0.9, 0.9, 0.9), collision=False)
    for x in (202, 207, 212):
        scene.model("TrafficCone", (x, -108.5, 2.16), yaw=90,
                    scale=(0.75, 0.75, 0.75), collision=False)
    for y in range(-205, 197, 12):
        scene.model("ParkBench", (178, y, 2.16), yaw=90)
        scene.model("ParkTree", (172, y, 2))
    scene.text("Harbor", (185, -111, 3.3), "ROWBOAT PIER | E TO BOARD", yaw=-90, size=0.55)
    # Nước còn kéo dài sau giới hạn để mép map không trông như thành hồ.
    borders = [((-225, 0, 30), (2, 540, 60)), ((720, 0, 30), (2, 540, 60)),
               ((247.5, -270, 30), (947, 2, 60)), ((247.5, 270, 30), (947, 2, 60))]
    for index, (position, size) in enumerate(borders):
        actor = scene.spawn(unreal.StaticMeshActor, f"Boundary_{index}", position)
        actor.static_mesh_component.set_static_mesh(scene.cube)
        actor.set_actor_scale3d(unreal.Vector(*size))
        actor.set_actor_hidden_in_game(True)
        actor.static_mesh_component.set_collision_profile_name("BlockAll")


def park(scene, x, y):
    scene.box((x, y, 2.025), (42, 42, 0.05), "Grass")
    scene.box((x, y, 2.08), (5, 42, 0.16), "Sidewalk")
    scene.box((x, y, 2.08), (42, 5, 0.16), "Sidewalk")
    scene.model("Monument", (x, y, 2.16))
    for dx in (-14, 14):
        for dy in (-14, 0, 14):
            scene.model("ParkTree", (x + dx, y + dy, 2))
            scene.model("ParkBench", (x + dx - 4, y + dy, 2.08), yaw=90)
