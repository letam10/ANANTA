"""Metre-based transit model components; shared portable PBR palette."""
import math
import bpy
from mathutils import Vector
import living_geometry as g


def hull(name, rings, color="white", segments=32, mat=None):
    # Mat cat elip doc truc X giu than may bay lien tuc, khong ghep cac khoi hop.
    points = []
    for x, width, height, z in rings:
        for index in range(segments):
            angle = 2 * math.pi * index / segments
            points.append((x, width * math.cos(angle), z + height * math.sin(angle)))
    faces = [tuple(reversed(range(segments)))]
    for ring in range(len(rings) - 1):
        for index in range(segments):
            a = ring * segments + index
            b = ring * segments + (index + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    faces.append(tuple((len(rings) - 1) * segments + i for i in range(segments)))
    obj = g.mesh(name, points, faces, color=color, mat=mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def panel(name, outline, thickness=.035, color="white", axis=2, mat=None, bevel=.008):
    points = [tuple(v) for v in outline]
    for point in outline:
        offset = list(point)
        offset[axis] += thickness
        points.append(tuple(offset))
    n = len(outline)
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return g.mesh(name, points, faces, color=color, mat=mat, bevel=bevel)


def curved_glass(name, rings, x_range, angle_range, side):
    # Kinh bam dung tiet dien vo elip, tranh tam phang cat chim vao cabin.
    xs = {x_range[0] + (x_range[1] - x_range[0]) * i / 6 for i in range(7)}
    xs.update(r[0] for r in rings if x_range[0] < r[0] < x_range[1])
    xs = sorted(xs)
    points = []
    columns = 7
    for offset in [.014, .025]:
        for x in xs:
            first, second = next((a, b) for a, b in zip(rings, rings[1:]) if a[0] <= x <= b[0])
            t = (x - first[0]) / (second[0] - first[0])
            width, height, centre = [a + (b - a) * t for a, b in zip(first[1:], second[1:])]
            for j in range(columns):
                angle = angle_range[0] + (angle_range[1] - angle_range[0]) * j / (columns - 1)
                points.append((x, side * (width + offset) * math.cos(angle),
                               centre + (height + offset) * math.sin(angle)))
    count = len(xs) * columns
    faces = []
    for row in range(len(xs) - 1):
        for column in range(columns - 1):
            a = row * columns + column
            face = (a, a + columns, a + columns + 1, a + 1)
            faces.append(face)
            faces.append(tuple(v + count for v in reversed(face)))
    rim = list(range(columns))
    rim += [row * columns + columns - 1 for row in range(1, len(xs))]
    rim += list(range(count - 2, count - columns - 1, -1))
    rim += [row * columns for row in range(len(xs) - 2, 0, -1)]
    for a, b in zip(rim, rim[1:] + rim[:1]):
        faces.append((a, b, b + count, a + count))
    obj = g.mesh(name, points, faces, color="navy")
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def wheel(x, y, z, radius=.48, width=.30):
    g.cylinder("Rubber tire", (x, y, z), radius, width, axis="Y", mat="Living_Dark", vertices=32)
    side = 1 if y > 0 else -1
    hub_y = y + side * (width / 2 + .012)
    g.cylinder("Rim", (x, hub_y, z), radius * .62, .04, axis="Y", mat="Living_Steel")
    g.cylinder("Hub", (x, hub_y + side * .028, z), radius * .24, .065,
               axis="Y", color="gray", vertices=16)
    for i in range(6):
        a = i * math.tau / 6
        location = (x + radius * .39 * math.sin(a), hub_y + side * .03,
                    z + radius * .39 * math.cos(a))
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.018, depth=.025,
                                           location=location, rotation=(math.pi / 2, 0, 0))
        nut = bpy.context.object
        nut.name = "Lug nut"
        g.g.finish(nut, "Living_Steel")
        g.uv(nut)


def slender_beam(name, start, end, radius, color):
    # Thanh nho dung 12 canh, khong bevel nhieu lop lam tang budget thuyen.
    delta = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=delta.length,
                                       location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    g.g.finish(obj, "Living_Enamel")
    for face in obj.data.polygons:
        face.use_smooth = abs(face.normal.z) < .5
    return g.uv(obj, color)


def text(label, location, size, rotation, color="white"):
    curve = bpy.data.curves.new("Service lettering", "FONT")
    curve.body = label
    curve.size = size
    curve.resolution_u = 2
    curve.extrude = .001
    curve.align_x = "CENTER"
    obj = bpy.data.objects.new(label, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    g.g.finish(obj, "Living_Enamel")
    g.uv(obj, color)


def finish(name):
    obj = g.finish(name)
    low = Vector(tuple(min(v.co[i] for v in obj.data.vertices) for i in range(3)))
    high = Vector(tuple(max(v.co[i] for v in obj.data.vertices) for i in range(3)))
    offset = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
    for vertex in obj.data.vertices:
        vertex.co -= offset
    obj.data.update()
    return obj
