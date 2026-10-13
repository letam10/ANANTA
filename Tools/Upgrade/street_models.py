"""Street, industry, entertainment and landmark meshes in metres."""

import math

from meshlib import box, cylinder, ellipsoid, finish, mesh, rod


def build():
    objects = []
    cylinder(0.16, 0.12, (0, 0, 0.06), "metal")
    cylinder(0.07, 3.5, (0, 0, 1.8), "metal")
    box((0.2, 0.4, 0.97), (0.15, 0, 3.04), "black", 0.06)
    for index, color in enumerate(("green", "yellow", "red")):
        cylinder(0.115, 0.025, (0.258, 0, 2.75 + index * 0.29), color, (0, math.pi / 2, 0))
        box((0.18, 0.31, 0.03), (0.28, 0, 2.92 + index * 0.29), "black")
    objects.append(finish("TrafficLight"))
    cylinder(0.09, 5.6, (0, 0, 2.8), "metal")
    rod((0, 0, 5.45), (1.4, 0, 5.6), 0.065, "metal")
    box((0.7, 0.3, 0.11), (1.45, 0, 5.56), "white")
    objects.append(finish("StreetLamp"))
    cylinder(0.055, 2.7, (0, 0, 1.35), "metal")
    box((0.06, 1.05, 0.43), (0, 0, 2.5), "blue")
    objects.append(finish("StreetSign"))
    for x in (-1.2, 0, 1.2):
        cylinder(0.045, 1.1, (x, 0, 0.55), "metal", vertices=12)
    for z in (0.4, 1.05):
        rod((-1.25, 0, z), (1.25, 0, z), 0.035, "metal")
    objects.append(finish("Railing"))
    for y in (-0.18, 0, 0.18):
        box((1.8, 0.15, 0.06), (0, y, 0.46), "wood")
    for z in (0.63, 0.8):
        box((1.8, 0.05, 0.13), (0, 0.27, z), "wood")
    for x in (-0.68, 0.68):
        box((0.065, 0.5, 0.45), (x, 0, 0.225), "metal")
    objects.append(finish("ParkBench"))
    cylinder(0.22, 0.8, (0, 0, 0.4), "metal")
    cylinder(0.24, 0.05, (0, 0, 0.84), "black")
    objects.append(finish("StreetBin"))
    cylinder(0.28, 0.83, (0, 0, 0.415), "blue", vertices=20)
    for z in (0.09, 0.72):
        cylinder(0.292, 0.025, (0, 0, z), "metal", vertices=20)
    objects.append(finish("FactoryBarrel"))
    box((1.2, 1, 0.13), (0, 0, 0.065), "wood")
    box((1.06, 0.86, 0.8), (0, 0, 0.54), "wood")
    for side in (-1, 1):
        box((0.07, 0.89, 0.78), (side * 0.46, 0, 0.55), "metal")
    objects.append(finish("FactoryCrate"))
    box((2.3, 0.95, 0.13), (0, 0, 0.83), "black")
    for x in (-0.93, 0.93):
        for y in (-0.38, 0.38):
            rod((x, y, 0), (x, y, 0.79), 0.04, "metal")
    for x in (-0.9, -0.6, -0.3, 0, 0.3, 0.6, 0.9):
        cylinder(0.055, 0.8, (x, 0, 0.92), "metal", (math.pi / 2, 0, 0), 12)
    objects.append(finish("FactoryConveyor"))
    box((1, 0.65, 1.8), (0, 0, 0.9), "blue")
    box((0.05, 0.51, 0.45), (0.515, 0, 1.44), "black")
    for index in range(4):
        cylinder(0.035, 0.025, (0.55, -0.15 + index * 0.1, 1), "red", (0, math.pi / 2, 0), 12)
    objects.append(finish("FactoryControl"))
    box((0.7, 0.6, 0.95), (0, 0, 0.48), "black")
    box((0.7, 0.3, 0.85), (0, 0.18, 1.36), "blue", 0.06)
    box((0.53, 0.02, 0.5), (0, -0.015, 1.32), "glass", rotation=(-0.18, 0, 0))
    box((0.71, 0.38, 0.08), (0, -0.13, 0.98), "red", rotation=(-0.12, 0, 0))
    objects.append(finish("ArcadeCabinet"))
    cylinder(1.7, 0.22, (0, 0, 0.11), "stone", vertices=24)
    cylinder(0.82, 1.3, (0, 0, 0.83), "stone", vertices=16)
    ellipsoid((0.38, 0.25, 0.48), (0, 0, 2.4), "metal")
    ellipsoid((0.23, 0.22, 0.25), (0, 0, 3.07), "metal")
    for side in (-1, 1):
        rod((side * 0.15, 0, 1.48), (side * 0.2, 0, 2.2), 0.13, "metal")
        rod((side * 0.32, 0, 2.67), (side * 0.85, 0, 3.04), 0.08, "metal")
    objects.append(finish("Monument"))
    box((0.07, 0.9, 2.35), (0, 0, 1.175), "wood", 0.012)
    cylinder(0.035, 0.12, (0.075, -0.31, 1.03), "metal", (0, math.pi / 2, 0))
    objects.append(finish("Door"))
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        rod((0, 0, 6), (4.8 * math.cos(rad), 0, 6 + 4.8 * math.sin(rad)), 0.055, "metal")
        box((0.7, 0.9, 0.55), (4.8 * math.cos(rad), 0, 6 + 4.8 * math.sin(rad)), "yellow")
    for index in range(48):
        a = index * math.tau / 48
        b = (index + 1) * math.tau / 48
        rod((4.8 * math.cos(a), 0, 6 + 4.8 * math.sin(a)),
            (4.8 * math.cos(b), 0, 6 + 4.8 * math.sin(b)), 0.075, "white")
    for side in (-1, 1):
        rod((side * 3, -1.8, 0), (0, 0, 6), 0.2, "metal")
    objects.append(finish("FerrisWheel"))
    for side in (-1, 1):
        box((0.25, 0.15, 0.09), (0.07, side * 0.11, 0.05), "black")
        rod((0, side * 0.11, 0.13), (0, side * 0.12, 0.88), 0.08, "blue")
        rod((0, side * 0.28, 1.42), (0.05, side * 0.32, 0.95), 0.065, "fabric")
    ellipsoid((0.14, 0.24, 0.34), (0, 0, 1.2), "fabric")
    cylinder(0.055, 0.1, (0, 0, 1.56), "wood", vertices=12)
    ellipsoid((0.12, 0.11, 0.15), (0, 0, 1.73), "wood")
    ellipsoid((0.125, 0.115, 0.065), (-0.015, 0, 1.84), "black")
    objects.append(finish("Citizen"))
    cylinder(0.25, 5.7, (0, 0, 2.85), "wood", vertices=12)
    for x, y, z, scale in ((0, 0, 6, 1.8), (0.8, 0.1, 5.5, 1.5), (-0.6, -0.4, 6.6, 1.4)):
        ellipsoid((scale, scale * 0.85, scale * 0.9), (x, y, z), "green")
    objects.append(finish("ParkTree"))
    return objects


def opera_roof():
    for offset in (-5, 0, 5):
        vertices = []
        for ring in range(13):
            a = ring * math.pi / 24
            for side in range(17):
                b = (side / 16 - 0.5) * math.pi
                vertices.append((offset + 4.8 * math.cos(b) * math.sin(a),
                                 9 * math.sin(b) * math.sin(a), 1 + 9 * math.cos(a)))
        faces = []
        for ring in range(12):
            for side in range(16):
                a = ring * 17 + side
                faces.append((a, a + 1, a + 18, a + 17))
        mesh(vertices, faces, "white")
    return finish("OperaShells")
