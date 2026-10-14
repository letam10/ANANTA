"""Compact original coastal props in metres, with ground pivots and +Z up."""

import math

from meshlib import box, cylinder, ellipsoid, finish, lathe, rod


def build():
    objects = []

    box((0.32, 0.19, 0.24), (0, 0, 0.12), "wood", 0.02)
    box((0.24, 0.13, 0.03), (0, 0, 0.255), "black", 0.008)
    for index, offset in enumerate((-0.09, 0, 0.09)):
        box((0.025, 0.012, 0.17), (offset, 0, 0.36), "metal", 0.002,
            rotation=(0, (-1 + index) * 0.08, 0))
        rod((offset, 0, 0.43), (offset + (index - 1) * 0.018, 0, 0.52),
            0.018, "black")
    objects.append(finish("KitchenKnifeBlock"))

    lathe([(0.145, 0), (0.175, 0.03), (0.185, 0.33), (0.17, 0.38),
           (0.001, 0.38)], "white", vertices=16)
    cylinder(0.19, 0.025, (0, 0, 0.395), "metal", vertices=16)
    box((0.11, 0.03, 0.025), (0, -0.205, 0.06), "metal", 0.004)
    objects.append(finish("BathroomBin"))

    box((0.28, 0.14, 0.05), (0, 0, 0.025), "wood", 0.012)
    rod((0, 0, 0.05), (0, 0, 0.19), 0.014, "wood")
    cylinder(0.16, 0.065, (0, 0, 0.30), "wood", (math.pi / 2, 0, 0), 16)
    cylinder(0.125, 0.012, (0, -0.038, 0.30), "white", (math.pi / 2, 0, 0), 16)
    rod((0, -0.047, 0.30), (0.065, -0.047, 0.30), 0.006, "black")
    rod((0, -0.047, 0.30), (-0.025, -0.047, 0.36), 0.006, "black")
    objects.append(finish("BedroomClock"))

    box((0.22, 0.22, 0.16), (-0.12, -0.02, 0.08), "red", 0.02)
    box((0.18, 0.18, 0.13), (0.10, 0.03, 0.145), "blue", 0.018)
    box((0.14, 0.14, 0.10), (0, 0.11, 0.26), "yellow", 0.015)
    cylinder(0.045, 0.03, (0, -0.105, 0.27), "green", (math.pi / 2, 0, 0), 12)
    objects.append(finish("ToyBlocks"))

    box((0.9, 0.22, 0.06), (0, 0, 0.86), "wood", 0.01)
    box((0.9, 0.22, 0.05), (0, 0, 0.08), "wood", 0.01)
    for side in (-0.4, 0.4):
        box((0.05, 0.05, 0.86), (side, 0, 0.46), "metal", 0.006)
    rod((-0.35, -0.12, 0.74), (0.35, -0.12, 0.74), 0.012, "metal")
    for offset in (-0.28, 0, 0.28):
        glass = lathe([(0.018, 0), (0.024, 0.06), (0.06, 0.08),
                       (0.07, 0.19), (0.055, 0.24), (0.001, 0.24)],
                      "glass", vertices=12)
        glass.location.x = offset
        glass.location.y = -0.01
        glass.location.z = 0.46
    objects.append(finish("BarGlassRack"))

    box((0.28, 0.25, 0.04), (0, 0, 0.02), "black", 0.01)
    lathe([(0.13, 0.04), (0.16, 0.08), (0.115, 0.43),
           (0.065, 0.48), (0.001, 0.48)], "yellow", vertices=16)
    lathe([(0.105, 0.23), (0.125, 0.24), (0.12, 0.29),
           (0.095, 0.30), (0.001, 0.30)], "white", vertices=16)
    cylinder(0.055, 0.03, (0, 0, 0.495), "black", vertices=12)
    objects.append(finish("TrafficCone"))

    lathe([(0.12, 0), (0.17, 0.04), (0.18, 0.10), (0.145, 0.12),
           (0.14, 0.48), (0.17, 0.52), (0.16, 0.58), (0.001, 0.58)],
          "red", vertices=12)
    cylinder(0.13, 0.04, (0, 0, 0.60), "metal", vertices=12)
    cylinder(0.11, 0.10, (0, -0.17, 0.34), "red", (math.pi / 2, 0, 0), 12)
    cylinder(0.09, 0.025, (0, -0.23, 0.34), "yellow", (math.pi / 2, 0, 0), 12)
    objects.append(finish("FireHydrant"))

    cylinder(0.23, 0.05, (0, 0, 0.025), "metal", vertices=12)
    rod((0, 0, 0.05), (0, 0, 1.15), 0.035, "metal")
    box((0.25, 0.18, 0.30), (0, 0, 1.28), "metal", 0.025)
    ellipsoid((0.14, 0.11, 0.10), (0, 0, 1.48), "black")
    cylinder(0.09, 0.015, (0, -0.10, 1.30), "glass", (math.pi / 2, 0, 0), 12)
    box((0.05, 0.02, 0.10), (0, -0.11, 1.31), "yellow", 0.004)
    objects.append(finish("ParkingMeter"))

    box((0.9, 0.45, 0.10), (0, 0, 0.10), "metal", 0.015)
    # Bánh xe quay quanh trục Y để mặt lăn hướng theo +X của xe.
    for horizontal in (-0.35, 0.35):
        for depth in (-0.21, 0.21):
            cylinder(0.09, 0.05, (horizontal, depth, 0.08), "black",
                     (math.pi / 2, 0, 0), 12)
    box((0.38, 0.32, 0.32), (-0.16, 0, 0.30), "blue", 0.02)
    box((0.30, 0.28, 0.24), (0.22, 0, 0.26), "red", 0.02)
    rod((-0.42, -0.20, 0.12), (-0.42, -0.20, 0.68), 0.018, "metal")
    rod((-0.42, 0.20, 0.12), (-0.42, 0.20, 0.68), 0.018, "metal")
    rod((-0.42, -0.20, 0.68), (-0.42, 0.20, 0.68), 0.018, "metal")
    objects.append(finish("AirportCart"))

    # Bốn khối bo cạnh ghép thành vòng cứu sinh đứng, giữ lỗ giữa rõ ở xa.
    box((0.48, 0.10, 0.10), (0, 0, 0.63), "red", 0.035)
    box((0.48, 0.10, 0.10), (0, 0, 0.09), "white", 0.035)
    box((0.10, 0.10, 0.55), (-0.20, 0, 0.36), "white", 0.035)
    box((0.10, 0.10, 0.55), (0.20, 0, 0.36), "red", 0.035)
    objects.append(finish("Lifebuoy"))

    return objects
