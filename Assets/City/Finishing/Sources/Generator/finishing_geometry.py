"""Original rug and pleated curtains in metres, with portable surface UVs."""
import math

import bpy
from geometry import MATERIALS, PARTS, box, combine, cylinder, finish


def rug():
    box("Woven foundation", (0, 0, 0.006), (2.92, 2, 0.012), "Finish_Woven", 0.003)
    for y in (-0.956, 0.956):
        box("Bound long edge", (0, y, 0.009), (2.90, 0.072, 0.012), "Finish_Binding", 0.002)
        box("Inset woven stripe", (0, y * 0.89, 0.011), (2.72, 0.018, 0.006), "Finish_Binding", 0)
    for x in (-1.408, 1.408):
        box("Bound short edge", (x, 0, 0.009), (0.072, 1.84, 0.012), "Finish_Binding", 0.002)
        box("Inset woven stripe", (x * 0.917, 0, 0.011), (0.018, 1.70, 0.006), "Finish_Binding", 0)
    for side in (-1, 1):
        for index in range(45):
            y = -0.94 + index * 1.88 / 44
            box("Short knotted fringe", (side * 1.473, y, 0.007),
                (0.054, 0.012, 0.007), "Finish_Woven", 0)
    obj = combine("InteriorWovenRug")
    for uv in obj.data.uv_layers.active.data:
        uv.uv *= 4
    return obj


def curtain_panel(x0, x1):
    columns = 48
    levels = (0, 0.055, 0.09, 0.45, 0.9, 1.4, 1.95, 2.29, 2.37, 2.42)
    vertices = []
    faces = []
    for z in levels:
        for col in range(columns + 1):
            t = col / columns
            x = x0 + (x1 - x0) * t
            # Nep vai co bien do nhe o chan, giu phan dau rem deu nhau.
            y = -0.044 + 0.074 * math.cos(t * math.tau * 6)
            y += 0.006 * math.sin(z * 2.4 + t * 5) * math.sin(z / 2.42 * math.pi)
            vertices.append((x, y, z))
    for row in range(len(levels) - 1):
        for col in range(columns):
            a = row * (columns + 1) + col
            faces.append((a, a + 1, a + columns + 2, a + columns + 1))
    mesh = bpy.data.meshes.new("Tailored pleats")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Linen panel", mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(MATERIALS["Finish_Linen"])
    mesh.materials.append(MATERIALS["Finish_Hem"])
    uv = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        row = poly.index // columns
        poly.material_index = 1 if row in (0, 1, 7, 8) else 0
        poly.use_smooth = True
        for index in poly.loop_indices:
            vi = mesh.loops[index].vertex_index
            co = mesh.vertices[vi].co
            uv.data[index].uv = ((vi % (columns + 1)) / columns * 2.1, co.z * 1.5)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("Woven cloth thickness", "SOLIDIFY")
    mod.thickness = 0.002
    mod.offset = 0
    bpy.ops.object.modifier_apply(modifier=mod.name)
    PARTS.append(obj)


def curtain():
    curtain_panel(-1.10, -0.026)
    curtain_panel(0.026, 1.10)
    cylinder("Curtain rod", (0, 0, 2.545), 0.022, 2.29, "Finish_Brass", "X", 20)
    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6,
                                            radius=0.055, location=(side * 1.145, 0, 2.545))
        obj = finish(bpy.context.object, "Finish_Brass")
        for poly in obj.data.polygons:
            poly.use_smooth = True
        box("Wall rod bracket", (side * 0.98, 0.06, 2.515),
            (0.035, 0.12, 0.045), "Finish_Brass", 0.005)
        cylinder("Wall rosette", (side * 0.98, 0.115, 2.515),
                 0.047, 0.01, "Finish_Brass", "Y", 16)
        for index in range(7):
            x = side * (0.058 + index * 1.012 / 6)
            bpy.ops.mesh.primitive_torus_add(major_segments=12, minor_segments=4,
                                            location=(x, 0, 2.49), rotation=(0, math.pi / 2, 0),
                                            major_radius=0.047, minor_radius=0.006)
            ring = finish(bpy.context.object, "Finish_Brass")
            for poly in ring.data.polygons:
                poly.use_smooth = True
            box("Sewn hanging tab", (x, 0.016, 2.419), (0.028, 0.007, 0.042), "Finish_Hem", 0)
    obj = combine("InteriorLinenCurtain", tile_uv=False)
    minimum = min(vertex.co.y for vertex in obj.data.vertices)
    maximum = max(vertex.co.y for vertex in obj.data.vertices)
    for vertex in obj.data.vertices:
        vertex.co.y = (vertex.co.y - (minimum + maximum) / 2) * 0.24 / (maximum - minimum)
    # Bo sung UV cho kim loai; cac tam vai giu UV doc nep va khong bi keo ngang.
    uv = obj.data.uv_layers.active
    for poly in obj.data.polygons:
        name = obj.material_slots[poly.material_index].material.name
        if name == "Finish_Brass":
            for index in poly.loop_indices:
                co = obj.data.vertices[obj.data.loops[index].vertex_index].co
                uv.data[index].uv = (co.x, co.z)
    return obj
