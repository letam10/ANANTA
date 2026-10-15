"""Metric mesh helpers: local +X is forward, +Z is up, pivot is ground level."""

import math

import bpy
from mathutils import Vector


COLORS = {
    "white": (0.78, 0.82, 0.8, 0.55),
    "blue": (0.035, 0.18, 0.38, 0.32),
    "red": (0.55, 0.035, 0.025, 0.36),
    "yellow": (0.85, 0.5, 0.055, 0.5),
    "metal": (0.22, 0.27, 0.29, 0.38),
    "black": (0.018, 0.022, 0.027, 0.78),
    "glass": (0.025, 0.085, 0.12, 0.12),
    "wood": (0.34, 0.16, 0.065, 0.68),
    "fabric": (0.17, 0.34, 0.3, 0.85),
    "stone": (0.47, 0.49, 0.45, 0.75),
    "green": (0.12, 0.34, 0.09, 0.8),
    "pink": (0.7, 0.23, 0.34, 0.5),
}
PARTS = []


def colorize(obj, color):
    if isinstance(color, str):
        color = COLORS[color]
    attribute = obj.data.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="CORNER")
    for value in attribute.data:
        value.color = color
    obj.data.materials.append(bpy.data.materials["CoastalSurface"])
    PARTS.append(obj)
    return obj


def box(size, position, color, bevel=0.025, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position, rotation=rotation)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("RoundedEdges", "BEVEL")
        modifier.width = min(bevel, min(size) * 0.2)
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return colorize(obj, color)


def cylinder(radius, depth, position, color, rotation=(0, 0, 0), vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=position, rotation=rotation
    )
    obj = bpy.context.object
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return colorize(obj, color)


def ellipsoid(size, position, color):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=1, location=position)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for face in obj.data.polygons:
        face.use_smooth = True
    return colorize(obj, color)


def mesh(vertices, faces, color):
    data = bpy.data.meshes.new("SculptedSurface")
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new("SculptedSurface", data)
    bpy.context.collection.objects.link(obj)
    return colorize(obj, color)


def prism(x_min, x_max, y_half, bottom, top, roof_min=None, roof_max=None, color="blue"):
    roof_min = x_min if roof_min is None else roof_min
    roof_max = x_max if roof_max is None else roof_max
    vertices = []
    for z, low, high, width in (
        (bottom, x_min, x_max, y_half),
        (top, roof_min, roof_max, y_half * 0.86),
    ):
        vertices.extend([(low, -width, z), (high, -width, z), (high, width, z), (low, width, z)])
    return mesh(vertices, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                           (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], color)


def rod(start, end, radius, color):
    direction = Vector(end) - Vector(start)
    obj = cylinder(radius, direction.length, (Vector(start) + Vector(end)) * 0.5, color, vertices=12)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return obj


def lathe(profile, color, vertices=24):
    points = []
    for radius, height in profile:
        for index in range(vertices):
            angle = index * math.tau / vertices
            points.append((radius * math.cos(angle), radius * math.sin(angle), height))
    faces = []
    for row in range(len(profile) - 1):
        for index in range(vertices):
            a = row * vertices + index
            b = row * vertices + (index + 1) % vertices
            faces.append((a, b, b + vertices, a + vertices))
    faces.append(tuple(reversed(range(vertices))))
    faces.append(tuple(range((len(profile) - 1) * vertices, len(profile) * vertices)))
    obj = mesh(points, faces, color)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def finish(name):
    for obj in PARTS:
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Bake hướng của phần đầu tiên sau join để mọi model dùng đúng +X / +Z.
    PARTS.clear()
    return obj
