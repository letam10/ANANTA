"""Original workshop geometry in metres, with material-safe UV coordinates."""
import math
import bpy
from mathutils import Vector
import geometry as g


def finish(obj, mat, bevel=0):
    obj.data.materials.append(g.MATERIALS[mat])
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Edge chamfers", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    g.clean_mesh(obj, weld=True)
    g.PARTS.append(obj)
    return obj


def box(name, loc, size, mat, bevel=0.002):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    return finish(obj, mat, bevel)


def cylinder(name, loc, radius, depth, mat, axis="Z", vertices=12):
    rotation = {"X": (0, math.pi / 2, 0), "Y": (math.pi / 2, 0, 0), "Z": (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                      location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    return finish(obj, mat, min(radius * .12, .003))


def profile(name, points, y, depth, mat, bevel=0.001):
    verts = [(x, y + offset, z) for offset in (-depth / 2, depth / 2) for x, z in points]
    n = len(points)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    return finish(obj, mat, bevel)


def ring(name, loc, radius, inner, depth, mat, segments=12):
    verts = []
    for y in (-depth / 2, depth / 2):
        for r in (radius, inner):
            verts += [(loc[0] + math.cos(i * math.tau / segments) * r,
                       loc[1] + y, loc[2] + math.sin(i * math.tau / segments) * r)
                      for i in range(segments)]
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        for a, b in ((0, segments), (segments * 2, 0),
                     (segments, segments * 3), (segments * 3, segments * 2)):
            faces.append((a + i, a + j, b + j, b + i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    return finish(obj, mat)


def peg_panel():
    # Lo vuong that tren tam thep; cac o dung chung canh va duoc han lai.
    verts, faces = [], []
    cols, rows = 15, 7
    width, height = 2.70, 1.25
    for row in range(rows):
        for col in range(cols):
            cx = -width / 2 + (col + 0.5) * width / cols
            cz = 0.055 + (row + 0.5) * height / rows
            outer = [(cx - width / cols / 2, cz - height / rows / 2),
                     (cx + width / cols / 2, cz - height / rows / 2),
                     (cx + width / cols / 2, cz + height / rows / 2),
                     (cx - width / cols / 2, cz + height / rows / 2)]
            inner = [(cx - .006, cz - .006), (cx + .006, cz - .006),
                     (cx + .006, cz + .006), (cx - .006, cz + .006)]
            k = len(verts)
            for y in (.015, .025):
                verts += [(x, y, z) for x, z in outer + inner]
            for i in range(4):
                j = (i + 1) % 4
                faces += [(k + i, k + j, k + 4 + j, k + 4 + i),
                          (k + 8 + j, k + 8 + i, k + 12 + i, k + 12 + j),
                          (k + 4 + i, k + 4 + j, k + 12 + j, k + 12 + i)]
                boundary = (i == 0 and row == 0) or (i == 2 and row == rows - 1)
                boundary |= (i == 3 and col == 0) or (i == 1 and col == cols - 1)
                if boundary:
                    faces.append((k + j, k + i, k + 8 + i, k + 8 + j))
    mesh = bpy.data.meshes.new("Punched steel sheet")
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(mesh.name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    finish(obj, "Workshop_Panel")


def spanner(x, length):
    z = 1.12
    scale = length / .52
    outline = [(-.040, -.068), (-.067, -.025), (-.057, .020), (-.026, .042),
               (-.033, .001), (-.016, -.023), (.018, -.023), (.036, .002),
               (.030, .043), (.065, .022), (.069, -.026), (.037, -.075)]
    points = [(x + px * scale, z + pz * scale) for px, pz in outline]
    profile("Open jaw spanner", points, -.025, .018, "Workshop_Steel", .0015)
    box("Forged shank", (x, -.025, z - length / 2 - .02 * scale), (.028 * scale, .015, length - .08 * scale),
        "Workshop_Steel", .004)
    ring("Box end", (x, -.025, z - length), .036 * scale, .023 * scale, .018,
         "Workshop_Steel")
    cylinder("Peg hook", (x, -.005, z - length + .02), .004, .045, "Workshop_Steel", "Y", 8)


def label(name, x, y, z, width, height, region):
    obj = profile(name, [(x - width / 2, z - height / 2), (x + width / 2, z - height / 2),
                        (x + width / 2, z + height / 2), (x - width / 2, z + height / 2)],
                  y, .001, "Workshop_Markings", 0)
    obj["label_region"] = region
    return obj


def toolboard():
    peg_panel()
    for x in (-1.375, 1.375):
        box("Folded panel rim", (x, .035, .7), (.05, .07, 1.4), "Workshop_Panel", .003)
    for z in (.025, 1.375):
        box("Folded panel rim", (0, .035, z), (2.7, .07, .05), "Workshop_Panel", .003)
    for x, length in zip((-1.13, -.89, -.65, -.41, -.17), (.54, .48, .42, .36, .30)):
        spanner(x, length)
    for i, x in enumerate((.23, .43, .63, .83)):
        z = .70 - .035 * i
        cylinder("Driver shaft", (x, -.033, z + .1), .005, .28, "Workshop_Steel")
        box("Flat screwdriver tip", (x, -.033, z + .243), (.012, .005, .025), "Workshop_Steel", .001)
        cylinder("Driver collar", (x, -.033, z - .04), .015, .02, "Workshop_Steel")
        cylinder("Fluted resin grip", (x, -.033, z - .13), .026, .16, "Workshop_Grip", vertices=8)
        cylinder("Grip end cap", (x, -.033, z - .216), .024, .016, "Workshop_Panel")
    box("Hammer hickory handle", (1.13, -.02, .78), (.035, .035, .42), "Workshop_Grip", .006)
    box("Machinist hammer head", (1.13, -.023, 1.0), (.20, .055, .073), "Workshop_Steel", .005)
    box("Socket organizer rail", (-.39, -.005, .245), (1.72, .04, .035), "Workshop_Steel", .003)
    for i in range(10):
        radius = .022 + .0015 * i
        ring("Hex socket", (-1.12 + i * .16, -.041, .275), radius, radius * .57,
             .058, "Workshop_Steel", 8)
    for x in (-1.365, 1.365):
        for z in (.11, 1.28):
            cylinder("Panel screw", (x, -.004, z), .009, .008, "Workshop_Steel", "Y", 8)
    label("Tool board title", 0, -.007, 1.325, 2.5, .082, "title")
    label("Socket sizes", -.39, -.035, .16, 1.76, .055, "sizes")
    return combine("WorkshopToolBoard")


def crate():
    for x in (-.53, .53):
        box("Pallet runner", (x, 0, .045), (.17, 1.02, .09), "Workshop_Wood", .005)
    for i in range(5):
        z = .155 + i * .103
        for y in (-.519, .519):
            box("Horizontal side slat", (0, y, z), (1.34, .044, .094), "Workshop_Wood", .0025)
        for x in (-.647, .647):
            box("End slat", (x, 0, z), (.044, 1.0, .094), "Workshop_Wood", .0025)
    for x in (-.646, .646):
        for y in (-.516, .516):
            box("Corner post", (x, y, .372), (.064, .064, .565), "Workshop_Wood", .004)
            box("Folded corner iron", (x + (.024 if x > 0 else -.024), y, .37),
                (.012, .068, .56), "Workshop_Steel", .0015)
            box("Corner iron return", (x, y + (.022 if y > 0 else -.022), .37),
                (.064, .012, .56), "Workshop_Steel", .0015)
    for i in range(7):
        box("Lid slat", (-.59 + i * .197, 0, .666), (.188, 1.07, .044), "Workshop_Wood", .003)
    for x in (-.49, .49):
        box("Lid cross brace", (x, 0, .688), (.074, 1.1, .024), "Workshop_Steel", .002)
    for x in (-.68, .68):
        box("Crate corner edge", (x, 0, .372), (.04, 1.04, .038), "Workshop_Steel", .002)
    for x in (-.646, .646):
        for z in (.17, .37, .57):
            for y in (-.548, .548):
                cylinder("Carriage bolt", (x, y, z), .010, .004, "Workshop_Steel", "Y", 8)
    label("Original crate shipping label", -.1, -.544, .365, .71, .27, "crate")
    return combine("WorkshopPartsCrate")


def combine(name):
    labels = [obj for obj in g.PARTS if "label_region" in obj]
    for obj in g.PARTS:
        uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
        bpy.context.view_layer.update()
        for face in obj.data.polygons:
            axis = max(range(3), key=lambda i: abs(face.normal[i]))
            for index in face.loop_indices:
                co = obj.data.vertices[obj.data.loops[index].vertex_index].co
                pair = (co.y, co.z) if axis == 0 else (co.x, co.z) if axis == 1 else (co.x, co.y)
                uv.data[index].uv = (pair[1] * 1.3, pair[0] * .65)
        if obj in labels:
            coords = [v.co for v in obj.data.vertices]
            lo_x, hi_x = min(v.x for v in coords), max(v.x for v in coords)
            lo_z, hi_z = min(v.z for v in coords), max(v.z for v in coords)
            regions = {"crate": (0, .5), "title": (.75, 1), "sizes": (.5, .75)}
            low, high = regions[obj["label_region"]]
            for face in obj.data.polygons:
                if abs(face.normal.y) > .9:
                    for index in face.loop_indices:
                        co = obj.data.vertices[obj.data.loops[index].vertex_index].co
                        uv.data[index].uv = ((co.x - lo_x) / (hi_x - lo_x),
                                                low + (co.z - lo_z) / (hi_z - lo_z) * (high - low))
    obj = g.combine(name, tile_uv=False)
    return obj
