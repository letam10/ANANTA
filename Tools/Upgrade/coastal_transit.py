"""Two independent rail directions and a small airfield integrated into the road grid."""

import unreal


def station(scene):
    gauge = 1.435
    for track, y in enumerate((190, 196)):
        scene.box((-16, y, 2.06), (384, 3.4, 0.12), "Stone" if "Stone" in scene.palette else "Concrete")
        for side in (-1, 1):
            scene.box((-16, y + side * gauge / 2, 2.18), (384, 0.07, 0.15), "Metal", collision=False)
        for index in range(640):
            scene.box((-207.7 + index * 0.6, y, 2.12), (0.22, 2.7, 0.13), "Wood", collision=False)
        direction = 1 if track == 0 else -1
        train = scene.spawn(unreal.CoastalTrain, f"Train_{track}", (-100 * direction, y, 2.18),
                            yaw=0 if direction > 0 else 180)
        train.mesh.set_static_mesh(unreal.load_asset("/Game/ANANTA/CoastalUpgrade/Models/Train"))
        train.mesh.set_material(0, scene.surface)
        train.direction = direction
    for index, y in enumerate((186.35, 199.65)):
        scene.box((0, y, 2.375), (54, 4, 0.75), "Sidewalk")
        scene.box((0, y, 6.3), (56, 5, 0.2), "White")
        for x in (-24, -12, 12, 24):
            scene.box((x, y + (-1.6 if index == 0 else 1.6), 4.55), (0.18, 0.18, 3.6), "Metal")
            scene.model("ParkBench", (x, y, 2.75), yaw=0 if index == 0 else 180)
        sign = "PLATFORM 1 | EASTBOUND" if index == 0 else "PLATFORM 2 | WESTBOUND"
        scene.text(f"Platform_{index}", (0, y - 0.1, 5.5), sign, yaw=-90, size=0.6)
        edge = y - 2 if index == 0 else y + 2
        for step in range(5):
            sign_y = -1 if index == 0 else 1
            scene.box((0, edge + sign_y * (1.25 - step * 0.25), 2 + (step + 1) * 0.075),
                      (4, 0.25, (step + 1) * 0.15), "Sidewalk")
    # Cầu vượt nối hai sân ga; thang máy tránh người đi bộ băng qua ray.
    scene.box((31, 193, 7.5), (4, 21, 0.2), "Concrete")
    for y, destination in ((182, 204), (204, 182)):
        control = scene.action(f"Station_Bridge_{y}", (31, y, 2),
                               "Crossed the pedestrian overpass", kind=4)
        control.destination = unreal.Vector(3100, destination * 100, 296)
    scene.text("Station", (0, 180, 5), "NOVA COAST STATION", yaw=-90, size=0.9)


def airfield(scene):
    scene.box((-199, -25, 2.03), (16, 176, 0.06), "Road")
    for y in range(-106, 62, 7):
        scene.box((-199, y, 2.065), (0.2, 3, 0.01), "White", collision=False)
    for side in (-1, 1):
        scene.box((-199 + side * 7, -25, 2.065), (0.15, 176, 0.01), "White", collision=False)
    scene.model("CivilAirplane", (-199, -22, 2.08), yaw=90)
    for x in (-205, -193):
        scene.model("AirportCart", (x, 62, 2.08), yaw=90, scale=(0.8, 0.8, 0.8), collision=False)
    scene.box((-198, 76, 2.08), (18, 18, 0.16), "Road")
    for side in (-1, 1):
        scene.box((-198 + side * 1.4, 76, 2.17), (0.25, 4, 0.01), "White", collision=False)
    scene.box((-198, 76, 2.17), (3, 0.25, 0.01), "White", collision=False)
    scene.model("Helicopter", (-198, 76, 2.2), yaw=90)
    scene.text("Airfield", (-199, 87, 4.3), "COAST AIRFIELD", yaw=-90, size=0.7)
    scene.action("Airfield_Control", (-191, 85, 2), "Airfield inspected. Aircraft are display models.")
