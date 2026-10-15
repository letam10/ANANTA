"""Metre scale, +X nose helpers for the original city mobility kit."""
import math
import bpy
from mathutils import Vector
import geometry as g

COLORS = {"white": 0, "yellow": 1, "blue": 2, "red": 3, "teal": 4, "orange": 5,
          "green": 6, "navy": 7, "cream": 8, "wood": 9, "leaf": 10, "soil": 11,
          "lamp": 12, "brake": 13, "amber": 14, "black": 15}


def uv(obj, color=None):
    obj.data.update()
    layer = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for face in obj.data.polygons:
        axis = max(range(3), key=lambda i: abs(face.normal[i]))
        for index in face.loop_indices:
            co = obj.data.vertices[obj.data.loops[index].vertex_index].co
            pair = (co.y, co.z) if axis == 0 else (co.x, co.z) if axis == 1 else (co.x, co.y)
            if color is None:
                layer.data[index].uv = (pair[0], pair[1])
            else:
                swatch = COLORS[color]
                # UV giu dien tich duong, nam trong o mau de tranh lem atlas.
                layer.data[index].uv = ((swatch % 4 + .2 + pair[0] * .014) / 4,
                                       (swatch // 4 + .2 + pair[1] * .014) / 4)
    return obj


def box(name, loc, size, color="white", bevel=.012, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Game manufactured edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 1
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    g.finish(obj, mat or "Mobility_Enamel")
    return uv(obj, None if mat else color)


def cylinder(name, loc, radius, depth, color="white", axis="Z", mat=None, vertices=24):
    obj = g.cylinder(name, loc, radius, depth, mat or "Mobility_Enamel", axis, vertices)
    for face in obj.data.polygons:
        face.use_smooth = abs(face.normal.z) < .99
    return uv(obj, None if mat else color)


def beam(name, a, b, radius=.025, mat="Mobility_Steel", color=None):
    delta = Vector(b) - Vector(a)
    obj = g.cylinder(name, (Vector(a) + Vector(b)) / 2, radius, delta.length, mat, vertices=12)
    for face in obj.data.polygons:
        face.use_smooth = abs(face.normal.z) < .99
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    return uv(obj, color)


def profile(name, sections, color="white", bevel=.025, mat=None):
    return uv(g.profile(name, sections, mat or "Mobility_Enamel", bevel), None if mat else color)


def mesh(name, vertices, faces, color="white", mat=None, bevel=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    g.finish(obj, mat or "Mobility_Enamel", bevel)
    return uv(obj, None if mat else color)


def panel(name, corners, color="white", mat=None, thickness=.018):
    a, b, c, d = [Vector(v) for v in corners]
    normal = (b - a).cross(c - a).normalized() * thickness
    points = [a, b, c, d, a - normal, b - normal, c - normal, d - normal]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return mesh(name, points, faces, color, mat)


def text_label(text, loc, size=.16, rotation=(math.pi / 2, 0, 0), color="white"):
    bpy.ops.object.text_add(location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.data.font = bpy.data.fonts.load("C:/Windows/Fonts/arial.ttf", check_existing=True)
    obj.data.body = text
    obj.data.size = size
    obj.data.align_x = "CENTER"
    obj.data.extrude = .001
    obj.data.resolution_u = 2
    bpy.ops.object.convert(target="MESH")
    obj.data.materials.clear()
    g.finish(obj, "Mobility_Enamel")
    uv(obj, color)
    return obj


def tire(x, side, width, radius=.38, depth=.25):
    y = side * width
    z = radius + .05
    cylinder("Radial tire", (x, y, z), radius, depth, axis="Y", mat="Mobility_Rubber", vertices=32)
    cylinder("Alloy rim", (x, y + side * depth * .51, z), radius * .65, .035,
             axis="Y", mat="Mobility_Steel")
    cylinder("Hub", (x, y + side * depth * .61, z), radius * .21, .05,
             axis="Y", mat="Mobility_Steel")
    for i in range(6):
        angle = i * math.tau / 6
        cylinder("Lug nut", (x + radius * .39 * math.cos(angle), y + side * depth * .60,
                             z + radius * .39 * math.sin(angle)), .028, .025,
                 axis="Y", mat="Mobility_Rubber", vertices=8)
    for i in range(24):
        angle = i * math.tau / 24
        obj = box("Tread rib", (x + radius * .992 * math.sin(angle), y,
                               z + radius * .992 * math.cos(angle)),
                  (.045, depth * .86, .025), bevel=0, mat="Mobility_Rubber")
        obj.rotation_euler.y = angle


def arch(body, axles, radius, width):
    for x in axles:
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius + .055, depth=width * 3,
                                           location=(x, 0, radius + .05), rotation=(math.pi / 2, 0, 0))
        cutter = bpy.context.object
        bpy.context.view_layer.objects.active = body
        modifier = body.modifiers.new("Open wheel housing", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
    g.clean_mesh(body, weld=True)


def seat(x, y, z=.65, scale=1):
    box("Seat cushion", (x, y, z), (.44 * scale, .48 * scale, .12), mat="Mobility_Upholstery")
    box("Seat back", (x - .2 * scale, y, z + .31 * scale),
        (.12, .49 * scale, .62 * scale), mat="Mobility_Upholstery")
    box("Head restraint", (x - .2 * scale, y, z + .70 * scale),
        (.13, .27 * scale, .18 * scale), mat="Mobility_Upholstery")


def end_lights(length, width, z):
    for side in (-1, 1):
        box("LED headlight", (length / 2 + .018, side * width * .32, z),
            (.035, width * .21, .14), "lamp")
        box("Rear stoplight", (-length / 2 - .02, side * width * .38, z),
            (.04, .20, .24), "brake")
    box("Front grille", (length / 2 + .025, 0, z - .05),
        (.03, width * .43, .24), mat="Mobility_Rubber")
    for height in (-.08, 0, .08):
        box("Grille chrome", (length / 2 + .045, 0, z - .05 + height),
            (.018, width * .41, .018), mat="Mobility_Steel")
    for end in (-1, 1):
        box("License plate", (end * (length / 2 + .045), 0, z - .34), (.02, .46, .13), "cream")


def mirrors(x, width, z):
    for side in (-1, 1):
        beam("Mirror stalk", (x, side * width / 2, z), (x, side * (width / 2 + .22), z + .05))
        box("Mirror shell", (x, side * (width / 2 + .25), z + .08),
            (.15, .19, .23), mat="Mobility_Rubber")
        box("Mirror face", (x - .077, side * (width / 2 + .25), z + .08),
            (.015, .15, .18), mat="Mobility_Steel")


def finish(name):
    for part in g.PARTS:
        for slot in part.material_slots:
            if slot.material is None:
                slot.material = g.MATERIALS["Mobility_Enamel"]
    obj = g.combine(name, tile_uv=False)
    obj["authoring_units"] = "metres; +X forward; ground or waterline origin"
    return obj
