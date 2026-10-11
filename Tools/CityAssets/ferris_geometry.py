"""Original metre-scale Ferris wheel parts; manufactured solids and explicit UVs."""
import math
import bpy
import bmesh
from mathutils import Vector

PARTS = []


def finish(obj, name, material, bevel=0, smooth=False):
    obj.name = name
    obj.data.materials.append(bpy.data.materials['Ferris_' + material])
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for face in obj.data.polygons:
        face.use_smooth = smooth and len(face.vertices) == 4
    if bevel:
        mod = obj.modifiers.new('Edge highlights', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    PARTS.append(obj)
    return obj


def box(name, loc, size, material='Ivory', bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.scale = size
    return finish(obj, name, material, bevel)


def cylinder(name, loc, radius, depth, material='Steel', axis='Z', vertices=20):
    rotation = {'X': (0, math.pi / 2, 0), 'Z': (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                      location=loc, rotation=rotation)
    return finish(bpy.context.object, name, material, 0, vertices > 8)


def beam(name, start, end, radius, material='Ivory', vertices=12):
    delta = Vector(end) - Vector(start)
    obj = cylinder(name, (Vector(start) + Vector(end)) / 2, radius, delta.length,
                   material, vertices=vertices)
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return obj


def ring(name, x, radius, thickness, material='Ivory', segments=128):
    # Vanh lien tuc 128 doan, tiet dien tron; khong ghep cac khoi hop thanh da giac.
    bpy.ops.mesh.primitive_torus_add(major_segments=segments, minor_segments=8,
                                     location=(x, 0, 18.35), rotation=(0, math.pi / 2, 0),
                                     major_radius=radius, minor_radius=thickness)
    obj = finish(bpy.context.object, name, material)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def slab(name, loc, corners, depth, material):
    vertices = [(loc[0] + x, loc[1] + y, loc[2] + z)
                for z in (-depth / 2, depth / 2) for x, y in corners]
    n = len(corners)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    return finish(obj, name, material, .025)


def triangulate(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def combine():
    source = bpy.data.collections.new('Editable manufactured components')
    bpy.context.scene.collection.children.link(source)
    source.hide_render = True
    source.hide_viewport = True
    for obj in PARTS:
        copy = obj.copy()
        copy.data = obj.data.copy()
        source.objects.link(copy)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = 'FerrisWheel'
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.material_slot_remove_unused()
    triangulate(obj)
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name='UVMap')
    uv.name = 'UVMap'
    for face in obj.data.polygons:
        axis = max(range(3), key=lambda i: abs(face.normal[i]))
        for loop in face.loop_indices:
            co = obj.data.vertices[obj.data.loops[loop].vertex_index].co
            pair = (co.y, co.z) if axis == 0 else (co.x, co.z) if axis == 1 else (co.x, co.y)
            uv.data[loop].uv = (pair[0] / 2, pair[1] / 2)
    PARTS.clear()
    return obj
