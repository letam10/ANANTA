"""Small original manufactured components, metres and front +X."""
import math
import bpy
from mathutils import Vector
import geometry as g

COLORS = dict(white=0, cream=1, teal=2, red=3, blue=4, yellow=5, orange=6, black=7,
              wood=8, green=9, screen=10, lamp=11, pink=12, gray=13, navy=14, bronze=15)


def uv(obj, color=None):
    obj.data.update()
    layer = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for face in obj.data.polygons:
        axis = max(range(3), key=lambda i: abs(face.normal[i]))
        for index in face.loop_indices:
            co = obj.data.vertices[obj.data.loops[index].vertex_index].co
            pair = (co.y, co.z) if axis == 0 else (co.x, co.z) if axis == 1 else (co.x, co.y)
            if color is None:
                layer.data[index].uv = pair
            else:
                swatch = COLORS[color]
                layer.data[index].uv = ((swatch % 4 + .45 + pair[0] * .025) / 4,
                                       (swatch // 4 + .45 + pair[1] * .025) / 4)
    return obj


def box(name, loc, size, color="white", bevel=.005, mat=None):
    return uv(g.box(name, loc, size, mat or "Living_Enamel", bevel), None if mat else color)


def cylinder(name, loc, radius, depth, color="white", axis="Z", mat=None, vertices=24):
    return uv(g.cylinder(name, loc, radius, depth, mat or "Living_Enamel", axis, vertices),
              None if mat else color)


def beam(name, a, b, radius=.015, mat="Living_Steel", color=None):
    delta = Vector(b) - Vector(a)
    obj = cylinder(name, (Vector(a) + Vector(b)) / 2, radius, delta.length,
                   color=color or "white", mat=mat, vertices=12)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    if color is not None:
        uv(obj, color)
    return obj


def mesh(name, points, faces, color="white", mat=None, bevel=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(points, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    g.finish(obj, mat or "Living_Enamel", bevel)
    return uv(obj, None if mat else color)


def lathe(name, profile, loc=(0, 0, 0), color="white", mat=None, segments=32):
    # Profil khep kin tao vat rong nhu chup den, khong dung mat phang hai chieu.
    points = []
    for radius, height in profile:
        points.extend((loc[0] + radius * math.cos(i * math.tau / segments),
                       loc[1] + radius * math.sin(i * math.tau / segments), loc[2] + height)
                      for i in range(segments))
    faces = []
    for row in range(len(profile)):
        next_row = (row + 1) % len(profile)
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((row * segments + i, row * segments + j,
                          next_row * segments + j, next_row * segments + i))
    obj = mesh(name, points, faces, color, mat)
    for poly in obj.data.polygons:
        poly.use_smooth = abs(poly.normal.z) < .98
    return obj


def torus(name, loc, major, minor, mat="Living_Steel", rotation=(0, 0, 0), segments=24, sides=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                   major_segments=segments, minor_segments=sides, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    g.finish(obj, mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return uv(obj)


def tube(name, path, radius=.012, mat="Living_Steel"):
    for a, b in zip(path, path[1:]):
        beam(name, a, b, radius, mat)


def finish(name):
    obj = g.combine(name, tile_uv=False)
    obj["authoring_units"] = "metres; front +X; up Z"
    return obj
