"""Small metre based mesh helpers; all exports receive applied transforms."""
import math
import bpy
import bmesh
from mathutils import Vector

PARTS = []
MATERIALS = {}


def finish(obj, mat, bevel=0):
    obj.data.materials.append(MATERIALS[mat])
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Manufactured edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    clean_mesh(obj, weld=True)
    PARTS.append(obj)
    return obj


def box(name, loc, size, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    return finish(obj, mat, bevel)


def cylinder(name, loc, radius, depth, mat, axis="Z", vertices=24):
    rotation = {"X": (0, math.pi / 2, 0), "Y": (math.pi / 2, 0, 0), "Z": (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                      location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    finish(obj, mat, min(radius * 0.12, 0.01))
    for poly in obj.data.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    return obj


def beam(name, start, end, radius, mat):
    delta = Vector(end) - Vector(start)
    obj = cylinder(name, (Vector(start) + Vector(end)) / 2, radius, delta.length, mat)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    return obj


def leaf(loc, scale, angle):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, location=loc)
    obj = bpy.context.object
    obj.name = "Oval leaf"
    obj.scale = scale
    finish(obj, "Foliage")
    obj.rotation_euler.y = angle
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def wheel_arches(body):
    for x in [-1.40, 1.38]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.37, depth=3,
                                          location=(x, 0, 0.34), rotation=(math.pi / 2, 0, 0))
        cutter = bpy.context.object
        bpy.context.view_layer.objects.active = body
        mod = body.modifiers.new("Wheel arch", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
    edge = body.modifiers.new("Arch edge highlight", "BEVEL")
    edge.width = 0.008
    edge.segments = 2
    bpy.ops.object.modifier_apply(modifier=edge.name)


def clean_mesh(obj, weld=False):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if weld:
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    degenerate = [face for face in bm.faces if face.calc_area() < 1e-10]
    if degenerate:
        bmesh.ops.delete(bm, geom=degenerate, context="FACES")
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    degenerate = [face for face in bm.faces if face.calc_area() < 1e-10]
    if degenerate:
        bmesh.ops.delete(bm, geom=degenerate, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.validate(verbose=False)
    obj.data.update()


def profile(name, sections, mat, bevel=0.015):
    verts = []
    for x, half_width, bottom, top in sections:
        verts.extend([(x, -half_width, bottom), (x, half_width, bottom),
                      (x, half_width, top), (x, -half_width, top)])
    faces = [(3, 2, 1, 0)]
    for i in range(len(sections) - 1):
        for j in range(4):
            faces.append((4 * i + j, 4 * i + (j + 1) % 4,
                          4 * (i + 1) + (j + 1) % 4, 4 * (i + 1) + j))
    faces.append(tuple(4 * (len(sections) - 1) + j for j in range(4)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    return finish(obj, mat, bevel)


def combine(identifier, objects=None, tile_uv=True):
    objects = list(objects if objects is not None else PARTS)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = identifier
    for slot in obj.material_slots:
        if slot.material is None:
            slot.material = MATERIALS["CarPaint" if identifier == "CarBody" else "Dark"]
    bpy.ops.object.material_slot_remove_unused()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    if tile_uv:
        # UV theo kich thuoc that: moi tile la 2 met, khong keo gian gach cua cot.
        uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
        for poly in obj.data.polygons:
            normal = poly.normal
            axis = max(range(3), key=lambda i: abs(normal[i]))
            for loop in poly.loop_indices:
                co = obj.data.vertices[obj.data.loops[loop].vertex_index].co
                pair = (co.y, co.z) if axis == 0 else (co.x, co.z) if axis == 1 else (co.x, co.y)
                uv.data[loop].uv = (pair[0] / 2, pair[1] / 2)
    clean_mesh(obj)
    PARTS.clear()
    return obj
