"""Recognizable service vehicles with sloped cabins and recessed silhouettes."""

import math

from meshlib import box, cylinder, ellipsoid, finish, mesh, prism, rod


def wheels(length, width, radius=0.34):
    for x in (-length * 0.31, length * 0.3):
        for side in (-1, 1):
            cylinder(radius, 0.22, (x, side * width * 0.48, radius), "black", (math.pi / 2, 0, 0), 20)
            cylinder(radius * 0.52, 0.235, (x, side * width * 0.48, radius), "metal", (math.pi / 2, 0, 0))


def service_car(name, kind):
    length, width = (6.4, 2.35) if kind == "fire" else (4.65, 1.85)
    if kind == "ambulance":
        length, width = 5.5, 2.08
    body_color = "red" if kind == "fire" else "white"
    box((length, width, 0.62), (0, 0, 0.73), body_color, 0.13)
    if kind == "police":
        prism(-1.5, 1.12, 0.87, 1.04, 1.7, -1.0, 0.45, "glass")
        box((1.55, 1.48, 0.09), (-0.28, 0, 1.73), "white")
    else:
        prism(0.5, length / 2 - 0.13, width * 0.46, 1.0, 2.28, 0.65, length / 2 - 0.36, "white")
        box((0.05, width * 0.75, 0.7), (length / 2 - 0.27, 0, 1.86), "glass", rotation=(0, -0.18, 0))
        box((length * 0.56, width * 0.98, 1.48), (-length * 0.18, 0, 1.69), body_color, 0.07)
    for side in (-1, 1):
        box((length * 0.91, 0.024, 0.17), (0, side * width * 0.505, 0.88), "blue" if kind == "police" else "red")
        box((0.33, 0.07, 0.2), (0.55, side * (width / 2 + 0.08), 1.5), "metal")
        box((0.08, 0.45, 0.14), (length / 2 + 0.02, side * width * 0.3, 0.85), "yellow")
        box((0.07, 0.3, 0.12), (-length / 2 - 0.02, side * width * 0.33, 0.85), "red")
    box((0.08, width * 0.45, 0.25), (length / 2 + 0.04, 0, 0.66), "black")
    bar_z = 1.87 if kind == "police" else 2.51
    for side in (-1, 1):
        box((0.22, 0.38, 0.13), (0.5, side * 0.28, bar_z), "red" if side < 0 else "blue")
    if kind == "ambulance":
        for side in (-1, 1):
            box((0.14, 0.025, 0.62), (-0.7, side * 1.05, 1.78), "red")
            box((0.62, 0.025, 0.14), (-0.7, side * 1.06, 1.78), "red")
    if kind == "fire":
        for side in (-1, 1):
            box((2.9, 0.05, 0.76), (-0.85, side * 1.19, 1.63), "metal")
            rod((-2.7, side * 0.38, 2.65), (1.2, side * 0.38, 2.65), 0.045, "metal")
        for x in range(12):
            rod((-2.6 + x * 0.32, -0.38, 2.65), (-2.6 + x * 0.32, 0.38, 2.65), 0.035, "metal")
    wheels(length, width, 0.42 if kind == "fire" else 0.34)
    return finish(name)


def rowboat():
    # Các vòng thân tạo mạn cong, đáy kín và khoang mở; không dùng khối hộp đặc.
    rings = [(-1.9, 0.02), (-1.4, 0.55), (-0.6, 0.72), (0.6, 0.7), (1.45, 0.42), (1.9, 0.02)]
    vertices = []
    for x, width in rings:
        vertices.extend([(x, -width, 0.7), (x, -width * 0.52, 0.12),
                         (x, width * 0.52, 0.12), (x, width, 0.7)])
    faces = []
    for ring in range(len(rings) - 1):
        for side in range(3):
            a = ring * 4 + side
            faces.append((a, a + 1, a + 5, a + 4))
    faces.extend([(0, 1, 2, 3), (20, 23, 22, 21)])
    hull = mesh(vertices, faces, "wood")
    modifier = hull.modifiers.new("HullThickness", "SOLIDIFY")
    modifier.thickness = 0.055
    import bpy
    bpy.context.view_layer.objects.active = hull
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    box((2.6, 0.6, 0.07), (0, 0, 0.18), "wood")
    for x in (-0.65, 0.7):
        box((0.29, 1.23, 0.07), (x, 0, 0.49), "white")
    for side in (-1, 1):
        rod((-0.5, side * 0.1, 0.61), (0.55, side * 1.2, 0.65), 0.024, "wood")
        box((0.46, 0.13, 0.04), (0.7, side * 1.29, 0.66), "wood", rotation=(0, 0, side * 0.7))
    return finish("Rowboat")


def aircraft(helicopter=False):
    if helicopter:
        ellipsoid((2.1, 0.92, 0.88), (0.4, 0, 1.4), "white")
        ellipsoid((0.92, 0.88, 0.68), (1.54, 0, 1.48), "glass")
        rod((-1.05, 0, 1.5), (-4.6, 0, 2.02), 0.15, "blue")
        box((0.8, 0.09, 1.35), (-4.4, 0, 2.41), "blue")
        cylinder(0.14, 0.5, (0, 0, 2.5), "metal")
        for angle in (0, math.pi / 2):
            box((8.5, 0.18, 0.045), (0, 0, 2.78), "black", rotation=(0, 0, angle))
        box((0.06, 1.6, 0.11), (-4.45, 0.12, 2.14), "black", rotation=(0.5, 0, 0))
        for side in (-1, 1):
            rod((-1.25, side * 0.95, 0.15), (2.0, side * 0.95, 0.15), 0.075, "metal")
            for x in (-0.8, 1):
                rod((x, side * 0.95, 0.2), (x, side * 0.6, 0.9), 0.055, "metal")
        return finish("Helicopter")
    ellipsoid((8, 0.98, 1.02), (0, 0, 1.8), "white")
    for side in (-1, 1):
        vertices = []
        for height in (1.18, 1.34):
            vertices.extend([(1.0, side * 0.7, height), (-2.5, side * 0.7, height),
                             (-3.7, side * 8.5, height + 0.4), (-2.6, side * 8.5, height + 0.4)])
        mesh(vertices, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], "white")
    box((2.1, 6, 0.12), (-6.1, 0, 2.2), "blue")
    mesh([(-7, 0, 2.1), (-7, 0, 5.15), (-4.85, 0, 2.1),
          (-7, 0.14, 2.1), (-7, 0.14, 5.15), (-4.85, 0.14, 2.1)],
         [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4)], "blue")
    for side in (-1, 1):
        for index in range(12):
            ellipsoid((0.16, 0.03, 0.18), (-4.1 + index * 0.65, side * 0.96, 2), "glass")
        cylinder(0.51, 1.9, (0, side * 3.1, 0.94), "metal", (0, math.pi / 2, 0))
    box((0.12, 1.3, 0.32), (6.6, 0, 2.27), "glass", rotation=(0, -0.22, 0))
    for x, y in ((4, 0), (-1, -1.2), (-1, 1.2)):
        rod((x, y, 0.18), (x, y, 1.2), 0.055, "metal")
        cylinder(0.22, 0.2, (x, y, 0.22), "black", (math.pi / 2, 0, 0))
    return finish("CivilAirplane")


def train():
    box((16, 2.65, 2.5), (0, 0, 2.03), "white", 0.14)
    prism(6.2, 8.5, 1.3, 0.8, 3.25, 6.2, 7.8, "blue")
    for side in (-1, 1):
        box((15.6, 0.03, 0.28), (0, side * 1.34, 1.2), "blue")
        for x in (-6, -4, -1, 1, 4, 6):
            box((1.3, 0.03, 0.85), (x, side * 1.34, 2.38), "glass")
        for x in (-2.5, 2.5):
            box((1.2, 0.03, 1.75), (x, side * 1.355, 1.93), "metal")
            box((0.95, 0.035, 0.7), (x, side * 1.38, 2.48), "glass")
    box((0.055, 2.1, 0.86), (8.18, 0, 2.42), "glass", rotation=(0, -0.27, 0))
    for x in (-5.5, -4.5, 4.5, 5.5):
        cylinder(0.36, 2.8, (x, 0, 0.36), "black", (math.pi / 2, 0, 0))
    return finish("Train")


def build():
    return [service_car("PoliceCar", "police"), service_car("FireEngine", "fire"),
            service_car("Ambulance", "ambulance"), rowboat(), aircraft(True), aircraft(), train()]
