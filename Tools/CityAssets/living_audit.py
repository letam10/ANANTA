"""Independently reopen FBXs, verify channels and geometry, optionally CPU render."""
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from finishing_materials import digest, build_materials
from living_build import BASE, OUT, QA, IDS, write_json


def inspect(obj, record):
    bpy.context.view_layer.update()
    data = obj.data
    points = [obj.matrix_world @ vertex.co for vertex in data.vertices]
    low = [min(p[i] for p in points) * 100 for i in range(3)]
    high = [max(p[i] for p in points) * 100 for i in range(3)]
    expected = record["boundsCm"]["min"] + record["boundsCm"]["max"]
    error = max(abs(a - b) for a, b in zip(low + high, expected))
    data.calc_loop_triangles()
    uv = data.uv_layers.active
    assert uv is not None
    zero_area = 0
    for tri in data.loop_triangles:
        a, b, c = [uv.data[index].uv.copy() for index in tri.loops]
        zero_area += abs((b - a).cross(c - a)) < 1e-14
    degenerate = 0
    for tri in data.loop_triangles:
        a, b, c = [data.vertices[index].co for index in tri.vertices]
        degenerate += (b - a).cross(c - a).length < 1e-12
    topology = bmesh.new()
    topology.from_mesh(data)
    boundary_edges = sum(edge.is_boundary for edge in topology.edges)
    nonmanifold_edges = sum(not edge.is_manifold for edge in topology.edges)
    topology.free()
    report = dict(id=record["id"], triangles=len(data.loop_triangles), boundsMaxErrorCm=error,
                  materialSlots=[mat.name for mat in data.materials], zeroAreaUvTriangles=zero_area,
                  degenerateTriangles=degenerate, allFacesTriangulated=all(len(p.vertices) == 3 for p in data.polygons),
                  finiteVertices=all(math.isfinite(v) for p in points for v in p),
                  finiteNormals=all(math.isfinite(v) for n in data.corner_normals for v in n.vector),
                  finiteUvs=all(math.isfinite(v) for p in uv.data for v in p.uv),
                  boundaryEdges=boundary_edges, nonmanifoldEdges=nonmanifold_edges,
                  validateChanged=data.validate(verbose=False))
    assert error < .02 and degenerate == 0 and zero_area == 0, report
    assert report["triangles"] == record["triangles"] <= record["triangleBudget"], report
    assert report["materialSlots"] == record["materialSlots"] and len(data.materials) <= 5, report
    assert all(report[key] for key in ("finiteVertices", "finiteNormals", "finiteUvs", "allFacesTriangulated"))
    assert not report["validateChanged"] and obj.location.length < .00001, report
    assert boundary_edges == nonmanifold_edges == 0, report
    if record["id"] == "CeilingFan":
        assert abs(high[2]) < .02, report
    else:
        assert abs(low[2]) < .02, report
    return report


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render(obj, record):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.resolution_x = 600
    scene.render.resolution_y = 400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("Living QA neutral world")
    scene.world.color = (.28, .28, .28)
    dimensions = [v / 100 for v in record["boundsCm"]["size"]]
    extent = max(dimensions)
    bottom = record["boundsCm"]["min"][2] / 100
    height = dimensions[2]
    target = Vector((0, 0, bottom + height * .48))
    bpy.ops.mesh.primitive_plane_add(size=extent * 200, location=(0, 0, bottom - .018))
    floor = bpy.context.object
    mat = bpy.data.materials.new("QA floor")
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.13, .15, .18, 1)
    floor.data.materials.append(mat)
    for index, (position, energy) in enumerate([((.2, -.65, 1.1), 90), ((-.5, .4, .8), 70)]):
        data = bpy.data.lights.new("Softbox" + str(index), "AREA")
        data.energy = extent * extent * energy
        data.size = extent * .8
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = Vector(position) * extent + target
        aim(light, target)
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(dimensions[0] * 1.18, dimensions[2] * 1.8, dimensions[1] * 1.8)
    camera.location = target + Vector((.78, -1.3, .70)) * extent
    aim(camera, target)
    scene.camera = camera
    path = QA / (record["id"] + "_threequarter.png")
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def main():
    manifest = json.loads((BASE / "living_manifest.json").read_text(encoding="utf-8"))
    assert set(e["id"] for e in manifest["meshes"]) == set(IDS)
    reports = []
    for record in manifest["meshes"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path = BASE / record["file"]
        assert digest(path) == record["sha256"]
        bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
        assert len(meshes) == 1
        obj = meshes[0]
        report = inspect(obj, record)
        if "--render" in sys.argv:
            build_materials(manifest["materials"], BASE)
            report["cpuRender"] = render(obj, record)
        reports.append(report)
        print("AUDIT", record["id"], report["triangles"], flush=True)
    for source in manifest["sourceFiles"]:
        assert digest(BASE / source["file"]) == source["sha256"], source["file"]
    textures = []
    for item in manifest["materials"]:
        for role in ("baseColor", "normal", "roughness"):
            if item[role]:
                image = bpy.data.images.load(str(BASE / item[role]), check_existing=True)
                assert tuple(image.size) == (1024, 1024)
                textures.append(dict(material=item["id"], role=role, resolution=list(image.size)))
    result = dict(status="PASS", meshes=reports, textures=textures,
                  sourceHashesVerified=len(manifest["sourceFiles"]), textureProvenance="Original deterministic pixels",
                  runtime="Not tested by asset audit; root owns Unreal integration and runtime images")
    write_json(QA / "audit.json", result)
    print("RESULT " + json.dumps(dict(status="PASS", assets=len(reports), textures=len(textures))))


if __name__ == "__main__":
    main()
