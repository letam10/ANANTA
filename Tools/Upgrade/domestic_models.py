"""Compact household assets in metres, with one shared vertex-colour material."""

import math

from meshlib import box, cylinder, finish, lathe, rod


def build():
    objects = []
    # Các đường tròn nhỏ chỉ cần 16 cạnh ở khoảng cách camera góc nhìn thứ ba.
    lathe([(0.001, 0), (0.11, 0), (0.145, 0.024), (0.14, 0.032),
           (0.095, 0.014), (0.001, 0.014)], "white", vertices=24)
    objects.append(finish("DinnerPlate"))

    box((0.012, 0.16, 0.007), (-0.025, 0, 0.006), "metal", 0.002)
    box((0.03, 0.07, 0.006), (-0.025, 0.1, 0.006), "metal", 0.002)
    box((0.012, 0.14, 0.007), (0.025, 0, 0.006), "metal", 0.002)
    for offset in (-0.009, 0, 0.009):
        box((0.004, 0.055, 0.006), (0.025 + offset, 0.09, 0.006), "metal", 0.001)
    objects.append(finish("Cutlery"))

    lathe([(0.001, 0), (0.105, 0), (0.13, 0.08), (0.115, 0.18),
           (0.07, 0.22), (0.001, 0.22)], "metal", vertices=20)
    cylinder(0.075, 0.012, (0, 0, 0.224), "black")
    cylinder(0.022, 0.035, (0, 0, 0.247), "black")
    rod((0.09, 0, 0.07), (0.21, 0, 0.18), 0.028, "metal")
    rod((-0.1, 0, 0.05), (-0.17, 0, 0.07), 0.018, "black")
    rod((-0.17, 0, 0.07), (-0.17, 0, 0.19), 0.018, "black")
    rod((-0.17, 0, 0.19), (-0.1, 0, 0.19), 0.018, "black")
    objects.append(finish("Kettle"))

    box((0.075, 0.06, 0.14), (0, 0, 0.07), "white", 0.014)
    cylinder(0.017, 0.035, (0, 0, 0.155), "metal", vertices=12)
    box((0.075, 0.022, 0.015), (0.023, 0, 0.177), "metal", 0.003)
    objects.append(finish("SoapDispenser"))

    for index, color in enumerate(("fabric", "white", "fabric")):
        box((0.42, 0.29, 0.055), (0, 0, 0.029 + index * 0.057), color, 0.012)
        box((0.34, 0.006, 0.009), (0, -0.146, 0.029 + index * 0.057), "white", 0.001)
    objects.append(finish("TowelStack"))

    # Pivot ở đáy khung; mặt sau y=+0.03 để tính khoảng hở khi treo tường.
    box((0.7, 0.06, 0.92), (0, 0, 0.46), "wood", 0.015)
    box((0.63, 0.012, 0.85), (0, -0.035, 0.46), "glass", 0.004)
    objects.append(finish("WallMirror"))

    box((1.05, 0.045, 0.68), (0, 0, 0.34), "wood", 0.01)
    box((0.96, 0.012, 0.59), (0, -0.027, 0.34), "white", 0.003)
    box((0.87, 0.004, 0.18), (0, -0.035, 0.19), "blue", 0)
    box((0.43, 0.004, 0.12), (-0.17, -0.039, 0.27), "green", 0)
    cylinder(0.085, 0.006, (0.26, -0.039, 0.46), "yellow", (math.pi / 2, 0, 0), 20)
    objects.append(finish("CoastalPicture"))

    for offset in (-0.48, 0.48):
        box((0.035, 0.07, 1.8), (offset, 0.18, 0.9), "metal", 0.006)
    for height in (0.12, 0.6, 1.08, 1.56):
        box((1.02, 0.42, 0.04), (0, 0, height), "wood", 0.007)
        for index in range(5):
            book_height = 0.24 + (index % 3) * 0.045
            box((0.06, 0.2, book_height), (-0.38 + index * 0.073, 0.04,
                height + 0.025 + book_height / 2), ("blue", "white", "red")[index % 3], 0.003)
    objects.append(finish("Bookshelf"))

    cylinder(0.24, 0.035, (0, 0, 0.018), "metal", vertices=20)
    cylinder(0.018, 1.42, (0, 0, 0.73), "metal", vertices=12)
    lathe([(0.29, 1.25), (0.18, 1.65), (0.17, 1.65),
           (0.28, 1.25), (0.29, 1.25)], "white", vertices=20)
    objects.append(finish("FloorLamp"))

    box((0.55, 0.48, 0.055), (0, 0, 0.53), "wood", 0.012)
    for horizontal in (-0.21, 0.21):
        for depth in (-0.17, 0.17):
            box((0.045, 0.045, 0.5), (horizontal, depth, 0.25), "wood", 0.005)
    objects.append(finish("SideTable"))

    box((1.55, 0.45, 0.42), (0, 0, 0.28), "wood", 0.016)
    for side in (-1, 1):
        box((0.7, 0.025, 0.3), (side * 0.39, -0.235, 0.29), "white", 0.007)
        box((0.075, 0.25, 0.07), (side * 0.59, 0, 0.035), "black", 0.005)
        rod((side * 0.43, 0, 0.72), (side * 0.56, -0.13, 0.49), 0.014, "black")
    box((1.34, 0.065, 0.77), (0, 0, 1.08), "black", 0.013)
    box((1.26, 0.008, 0.69), (0, -0.038, 1.08), "glass", 0.003)
    objects.append(finish("TVConsole"))

    box((1.12, 1.12, 0.08), (0, 0, 0.04), "white", 0.024)
    for side in (-1, 1):
        box((0.055, 1.12, 0.12), (side * 0.533, 0, 0.1), "white", 0.012)
        box((1.02, 0.055, 0.12), (0, side * 0.533, 0.1), "white", 0.012)
    cylinder(0.045, 0.003, (0, 0, 0.082), "metal")
    rod((0, 0.48, 0.16), (0, 0.48, 2.04), 0.018, "metal")
    rod((0, 0.48, 2.04), (0, 0.18, 2.04), 0.018, "metal")
    cylinder(0.11, 0.025, (0, 0.16, 2.025), "metal", vertices=20)
    cylinder(0.032, 0.08, (0, 0.44, 1.03), "metal", (math.pi / 2, 0, 0))
    objects.append(finish("ShowerTray"))

    box((0.36, 0.26, 0.026), (0, 0, 0.013), "wood", 0.018)
    box((0.18, 0.024, 0.012), (0.015, 0, 0.032), "metal", 0.002)
    box((0.08, 0.024, 0.019), (-0.115, 0, 0.035), "black", 0.003)
    objects.append(finish("ChoppingBoard"))

    box((0.7, 0.23, 0.015), (0, 0, 0.008), "wood", 0.004)
    for index, height in enumerate((0.22, 0.31, 0.25)):
        bottle = lathe([(0.001, 0.016), (0.045, 0.016), (0.045, height * 0.7),
                        (0.018, height * 0.85), (0.018, height), (0.001, height)],
                       ("green", "blue", "white")[index], vertices=12)
        bottle.location.x = (index - 1) * 0.18
    objects.append(finish("BottleTray"))
    return objects
