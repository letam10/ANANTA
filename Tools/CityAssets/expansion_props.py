"""Human-scale street furniture with functional gaps and separate materials."""
import math
import bpy
from mathutils import Vector
from geometry import box, cylinder, combine, finish


def bus_shelter():
    for x in (-1.8, 1.8):
        for y in (-0.63, 0.63):
            box("Shelter post", (x, y, 1.24), (0.075, 0.075, 2.48), "Dark")
            box("Post foot", (x, y, 0.035), (0.19, 0.19, 0.07), "Aluminium")
    box("Shelter roof", (0, 0, 2.48), (4.0, 1.65, 0.14), "Teal", 0.025)
    box("Roof underside", (0, 0, 2.39), (3.83, 1.48, 0.04), "Aluminium")
    for x in (-1.19, 0, 1.19):
        box("Back glazing", (x, 0.63, 1.32), (1.10, 0.025, 1.94), "Glass")
    for x in (-0.60, 0.60):
        box("Glazing division", (x, 0.63, 1.25), (0.045, 0.07, 2.26), "Aluminium")
    for z in (0.31, 2.32):
        box("Back rail", (0, 0.63, z), (3.65, 0.07, 0.06), "Aluminium")
    box("Side glazing", (-1.8, 0.06, 1.32), (0.025, 1.03, 1.94), "Glass")
    for x in (-0.94, 0.94):
        box("Bench support", (x, 0.25, 0.23), (0.075, 0.36, 0.46), "Dark")
    for y in (0.10, 0.24, 0.38):
        box("Seat slat", (0, y, 0.48), (2.85, 0.115, 0.065), "Wood")
    for z in (0.69, 0.85):
        box("Backrest slat", (0, 0.46, z), (2.85, 0.065, 0.12), "Wood")
    box("Timetable backing", (1.32, 0.59, 1.70), (0.50, 0.04, 0.73), "Light")
    for z in (1.49, 1.62, 1.75, 1.88):
        box("Timetable line", (1.32, 0.56, z), (0.39, 0.01, 0.017), "Teal", 0)
    return combine("BusShelter")


def market_stall():
    for x in (-1.12, 1.12):
        for y in (-0.54, 0.54):
            box("Stall post", (x, y, 1.16), (0.07, 0.07, 2.32), "Wood")
    for side in (-1, 1):
        for i in range(8):
            canopy = box("Striped canvas", (-1.18 + i * 0.337, side * 0.39, 2.44),
                         (0.337, 0.84, 0.035), "Linen" if i % 2 else "Teal", 0.004)
            canopy.rotation_euler.x = -side * math.radians(16)
        box("Canopy valance", (0, side * 0.80, 2.24), (2.70, 0.035, 0.24), "Teal")
    box("Stall counter", (0, -0.37, 0.98), (2.50, 0.77, 0.10), "Wood", 0.015)
    box("Counter front", (0, -0.70, 0.51), (2.35, 0.075, 0.86), "Wood")
    for x in (-0.78, 0, 0.78):
        box("Produce crate", (x, -0.37, 1.11), (0.68, 0.57, 0.17), "Wood")
        for n in range(3):
            cylinder("Produce", (x - 0.19 + n * 0.19, -0.4, 1.235), 0.08, 0.11, "Red", vertices=8)
    return combine("MarketStall")


def trash_bin():
    cylinder("Bin base", (0, 0, 0.06), 0.29, 0.12, "Dark")
    cylinder("Inner bin", (0, 0, 0.43), 0.25, 0.67, "Dark")
    for i in range(14):
        a = i * math.tau / 14
        slat = box("Timber bin slat", (0.27 * math.cos(a), 0.27 * math.sin(a), 0.43),
                   (0.068, 0.045, 0.64), "Wood", 0.004)
        slat.rotation_euler.z = a + math.pi / 2
    for x in (-0.21, 0.21):
        box("Lid support", (x, 0.10, 0.83), (0.04, 0.05, 0.25), "Dark")
    cylinder("Rain lid", (0, 0, 0.97), 0.32, 0.06, "Teal")
    return combine("TrashBin")


def bike_rack():
    for x in (-0.62, 0.62):
        for y in (-0.52, 0.52):
            cylinder("Rack foot", (x, y, 0.025), 0.095, 0.05, "Aluminium")
        points = [Vector((x, 0.52, 0.05))]
        points += [Vector((x, 0.52 * math.cos(i * math.pi / 16), 0.69 + 0.20 * math.sin(i * math.pi / 16)))
                   for i in range(17)]
        points.append(Vector((x, -0.52, 0.05)))
        vertices, faces = [], []
        # Các vòng đỉnh nối liền tạo ống cong, không để lộ đầu các đoạn trụ.
        for i, point in enumerate(points):
            tangent = points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]
            cross = tangent.normalized().cross(Vector((1, 0, 0)))
            for j in range(12):
                angle = j * math.tau / 12
                vertices.append(point + 0.035 * (Vector((math.cos(angle), 0, 0)) + cross * math.sin(angle)))
            if i:
                for j in range(12):
                    k = (j + 1) % 12
                    faces.append(((i - 1) * 12 + j, (i - 1) * 12 + k, i * 12 + k, i * 12 + j))
        faces.append(tuple(reversed(range(12))))
        faces.append(tuple((len(points) - 1) * 12 + j for j in range(12)))
        mesh = bpy.data.meshes.new("Continuous bent tube")
        mesh.from_pydata(vertices, [], faces)
        obj = bpy.data.objects.new("Continuous bent tube", mesh)
        bpy.context.collection.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        finish(obj, "Aluminium")
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return combine("BikeRack")


def street_sign():
    cylinder("Sign footing", (0, 0, 0.035), 0.15, 0.07, "Dark")
    cylinder("Sign pole", (0, 0, 1.40), 0.035, 2.8, "Aluminium")
    for z, width in ((2.42, 1.06), (2.72, 0.86)):
        box("Direction sign", (0, -0.075, z), (width, 0.06, 0.22), "Teal")
        for edge in (-1, 1):
            box("Sign edge", (0, -0.11, z + edge * 0.086), (width - 0.04, 0.01, 0.014), "Light", 0)
        box("Street marker", (-0.05, -0.11, z), (width * 0.55, 0.01, 0.025), "Light", 0)
    return combine("StreetSign")
