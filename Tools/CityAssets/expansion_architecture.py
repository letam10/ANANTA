"""Distinct 4 x 3.2 metre facade modules, street-facing side is negative Y."""
import math
import bpy
from geometry import box, combine, finish


def prism(name, points, front, back, material):
    vertices = [(x, y, z) for y in (front, back) for x, z in points]
    n = len(points)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    return finish(obj, material, 0.004)


def border(material="Stone"):
    for x in (-1.88, 1.88):
        box("Edge pier", (x, 0.08, 1.60), (0.24, 0.36, 2.96), material)
    box("Lower course", (0, -0.02, 0.12), (4, 0.48, 0.24), "Stone")
    box("Upper course", (0, -0.02, 3.11), (4, 0.48, 0.18), "Stone")


def glazing(x, y, z, width, height, material="Dark"):
    box("Recessed pane", (x, y + 0.075, z), (width, 0.035, height), "Glass")
    for side in (-1, 1):
        box("Window jamb", (x + side * width / 2, y, z), (0.055, 0.18, height + 0.1), material)
        box("Window rail", (x, y, z + side * height / 2), (width + 0.06, 0.18, 0.06), material)
    box("Window mullion", (x, y - 0.02, z), (0.035, 0.10, height), material)


def brick_arch():
    border("Brick")
    box("Brick centre pier", (0, 0.08, 1.59), (0.22, 0.36, 2.74), "Brick")
    box("Brick upper panel", (0, 0.10, 2.95), (3.52, 0.32, 0.22), "Brick")
    for x in (-0.94, 0.94):
        r, spring = 0.71, 2.02
        outer = r + 0.16
        infill = [(x - outer, 2.99), (x + outer, 2.99)]
        infill += [(x + outer * math.cos(i * math.pi / 12), spring + outer * math.sin(i * math.pi / 12))
                   for i in range(13)]
        prism("Brick arch spandrel", infill, -0.05, 0.26, "Brick")
        outline = [(x - r, 0.55), (x + r, 0.55)]
        outline += [(x + r * math.cos(i * math.pi / 12), spring + r * math.sin(i * math.pi / 12))
                    for i in range(13)]
        prism("Arched glazing", outline, 0.02, 0.055, "Glass")
        for i in range(12):
            a, b = i * math.pi / 12, (i + 1) * math.pi / 12
            points = [(x + radius * math.cos(t), spring + radius * math.sin(t))
                      for radius, t in ((r, a), (r + 0.16, a), (r + 0.16, b), (r, b))]
            prism("Arch voussoir", points, -0.19, 0.19, "Stone")
        for dx in (-r - 0.075, r + 0.075):
            box("Arch upright", (x + dx, -0.06, 1.285), (0.15, 0.36, 1.47), "Brick")
        box("Deep sill", (x, -0.18, 0.49), (1.7, 0.52, 0.12), "Stone")
        box("Arch transom", (x, -0.04, spring), (1.42, 0.1, 0.055), "Dark")
        box("Arch mullion", (x, -0.04, 1.53), (0.045, 0.1, 1.96), "Dark")
        box("Brick apron", (x, 0.06, 0.34), (1.62, 0.36, 0.25), "Brick")
    return combine("FacadeBrickArch")


def bay():
    border("Plaster")
    for x in (-1.53, 1.53):
        box("Plaster shoulder", (x, 0.09, 1.6), (0.46, 0.34, 2.96), "Plaster")
    for z, h in ((0.48, 0.50), (2.85, 0.32)):
        box("Bay front apron", (0, -0.68, z), (1.92, 0.18, h), "Plaster")
        for side in (-1, 1):
            panel = box("Angled apron", (side * 1.08, -0.41, z), (0.66, 0.18, h), "Plaster")
            panel.rotation_euler.z = side * math.radians(48)
    glazing(0, -0.73, 1.69, 1.72, 1.75, "Wood")
    for side in (-1, 1):
        before = set(bpy.data.objects)
        glazing(0, 0, 1.69, 0.67, 1.75, "Wood")
        for obj in set(bpy.data.objects) - before:
            obj.rotation_euler.z = side * math.radians(48)
            x, y = obj.location.x, obj.location.y
            a = side * math.radians(48)
            obj.location.x = side * 1.11 + x * math.cos(a) - y * math.sin(a)
            obj.location.y = -0.43 + x * math.sin(a) + y * math.cos(a)
    box("Bay canopy", (0, -0.38, 2.71), (2.84, 1.06, 0.12), "Stone")
    box("Bay base ledge", (0, -0.38, 0.75), (2.84, 1.06, 0.12), "Stone")
    return combine("FacadeBay")


def art_deco():
    border("Stone")
    box("Apron", (0, 0.06, 0.47), (3.52, 0.34, 0.5), "Plaster")
    for x in (-1.08, 0, 1.08):
        glazing(x, -0.03, 1.65, 0.88, 1.76, "Brass")
    for x in (-1.63, -0.54, 0.54, 1.63):
        box("Deco pilaster", (x, -0.14, 1.65), (0.16, 0.36, 2.8), "Stone")
        box("Golden flute", (x, -0.335, 1.73), (0.035, 0.03, 2.28), "Brass", 0.002)
    for width, z in ((3.52, 2.67), (2.85, 2.80), (2.17, 2.93)):
        box("Stepped crown", (0, -0.20, z), (width, 0.46, 0.12), "Stone")
    for x in (-1.08, 0, 1.08):
        prism("Deco diamond", [(x, 0.29), (x + 0.13, 0.47), (x, 0.65), (x - 0.13, 0.47)],
              -0.13, -0.09, "Brass")
    return combine("FacadeArtDeco")


def industrial():
    border("Brick")
    for z in (0.43, 2.86):
        box("Brick spandrel", (0, 0.08, z), (3.52, 0.36, 0.36), "Brick")
    glazing(0, -0.05, 1.64, 3.25, 1.97)
    for x in (-1.08, -0.54, 0.54, 1.08):
        box("Factory mullion", (x, -0.095, 1.64), (0.04, 0.1, 1.97), "Dark")
    for z in (1.15, 1.65, 2.15):
        box("Factory transom", (0, -0.10, z), (3.25, 0.1, 0.04), "Dark")
    for x in (-1.70, 1.70):
        box("Steel vertical web", (x, -0.23, 1.6), (0.07, 0.40, 2.94), "Dark")
        box("Steel flange", (x, -0.42, 1.6), (0.22, 0.05, 2.94), "Aluminium")
    box("Rain hood", (0, -0.29, 2.71), (3.55, 0.77, 0.07), "Aluminium")
    box("Factory sill", (0, -0.13, 0.61), (3.53, 0.46, 0.13), "Stone")
    return combine("FacadeIndustrial")
