"""Low poly branching trees with individual folded leaves; deterministic seeds."""
import math
import random
import bpy
from mathutils import Vector
from geometry import MATERIALS, PARTS, finish, combine


def beam(name, start, end, radius, material):
    delta = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=radius, radius2=radius * 0.72,
                                    depth=delta.length, location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.name = name
    finish(obj, material)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    return obj


def leaf_cluster(center, radius, count, rng, vertices, faces):
    # Lá riêng có sống gấp và độ dày nhỏ, tránh tán cây là các khối cầu đặc.
    for _ in range(count):
        point = Vector(center)
        direction = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.8, 0.8))).normalized()
        point += direction * radius * rng.random() ** (1 / 3)
        axis = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.65, 0.65))).normalized()
        cross = axis.cross(Vector((0, 0, 1))).normalized()
        length = rng.uniform(0.19, 0.32)
        width = length * rng.uniform(0.38, 0.55)
        points = [point - axis * length, point + cross * width,
                  point + axis * length, point - cross * width,
                  point + Vector((0, 0, 0.045)), point - Vector((0, 0, 0.015))]
        n = len(vertices)
        vertices.extend(points)
        for i in range(4):
            faces.append((n + i, n + (i + 1) % 4, n + 4))
            faces.append((n + (i + 1) % 4, n + i, n + 5))


def tree(columnar=False):
    rng = random.Random(835 if columnar else 241)
    height = 8.25 if columnar else 6.9
    trunk = [(0, 0, 0), (0.10, -0.07, 1.9), (-0.05, 0.08, 3.6), (0.10, 0, 5.2), (0, 0, height - 0.45)]
    for i in range(4):
        beam("Tapered trunk", trunk[i], trunk[i + 1], 0.19 - i * 0.037, "Wood")
    for angle in range(0, 360, 72):
        a = math.radians(angle)
        beam("Root flare", (0, 0, 0.38), (0.36 * math.cos(a), 0.36 * math.sin(a), 0.06), 0.075, "Wood")
    vertices, faces = [], []
    count = 17 if columnar else 13
    for i in range(count):
        angle = i * 2.39996
        if columnar:
            z = 3.45 + i * 0.24
            reach = 1.11 * (1 - 0.46 * i / count)
            cluster_radius = 0.68 - 0.18 * i / count
        else:
            z = 3.65 + (i % 4) * 0.55
            reach = 1.56 + rng.uniform(-0.27, 0.20)
            cluster_radius = 0.74
        end = Vector((reach * math.cos(angle), reach * math.sin(angle), z + 0.58))
        start = Vector((0, 0, z - 0.8))
        middle = start.lerp(end, 0.54) + Vector((0, 0, -0.12))
        beam("Primary branch", start, middle, 0.068, "Wood")
        beam("Branch tip", middle, end, 0.035, "Wood")
        leaf_cluster(end, cluster_radius, 66, rng, vertices, faces)
    leaf_cluster((0, 0, height - 0.65), 0.49, 75, rng, vertices, faces)
    mesh = bpy.data.meshes.new("Individual leaves")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(MATERIALS["Foliage"])
    obj = bpy.data.objects.new("Individual leaves", mesh)
    bpy.context.collection.objects.link(obj)
    PARTS.append(obj)
    result = combine("TreeColumnar" if columnar else "TreeBroadleaf")
    bottom = min(v.co.z for v in result.data.vertices)
    for vertex in result.data.vertices:
        vertex.co.z -= bottom
    for poly in result.data.polygons:
        poly.use_smooth = True
    return result
