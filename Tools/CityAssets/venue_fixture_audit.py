"""FBX roundtrip, portable channels, print orientation and CPU render verification."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import finishing_materials as materials
from venue_fixture_build import BASE, OUT, QA, TARGETS


def inspect(obj, entry):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    low = [min(p[i] for p in points) * 100 for i in range(3)]
    high = [max(p[i] for p in points) * 100 for i in range(3)]
    target, budget = TARGETS[entry["id"]]
    expected_low = [-target[0] / 2, -target[1] / 2, 0]
    expected_high = [target[0] / 2, target[1] / 2, target[2]]
    error = max(abs(a - b) for a, b in zip(low + high, expected_low + expected_high))
    mesh = obj.data
    mesh.calc_loop_triangles()
    layer = mesh.uv_layers.active
    assert layer is not None
    degenerate = sum(face.area < 1e-10 for face in mesh.polygons)
    degenerate_triangles = 0
    for tri in mesh.loop_triangles:
        a, b, c = [mesh.vertices[index].co for index in tri.vertices]
        degenerate_triangles += (b - a).cross(c - a).length < 1e-12
    zero_uv = 0
    for face in mesh.polygons:
        coords = [layer.data[index].uv.copy() for index in face.loop_indices]
        area = abs(sum(coords[i].cross(coords[(i + 1) % len(coords)]) for i in range(len(coords))))
        zero_uv += area < 1e-12
    slots = [slot.material.name for slot in obj.material_slots]
    report = dict(id=entry["id"], boundsCm=dict(min=low, max=high), targetMaxErrorCm=error,
                  triangles=len(mesh.loop_triangles), degenerateFaces=degenerate, zeroAreaUvFaces=zero_uv,
                  uvLayers=len(mesh.uv_layers), materialSlots=slots,
                  degenerateTriangles=degenerate_triangles,
                  finiteUvs=all(math.isfinite(value) for loop in layer.data for value in loop.uv),
                  finiteVertices=all(math.isfinite(value) for p in points for value in p),
                  meshValidateChanged=mesh.validate(verbose=False))
    assert error < 0.01 and degenerate == degenerate_triangles == zero_uv == 0, report
    assert report["finiteVertices"] and report["finiteUvs"] and not report["meshValidateChanged"], report
    assert slots == entry["materialSlots"], report
    assert len(mesh.loop_triangles) == entry["triangles"] <= budget, report
    assert obj.location.length < 0.0001, report
    return report


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render(obj):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("Review world")
    scene.world.color = (0.17, 0.17, 0.17)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.01))
    ground = bpy.context.object
    mat = bpy.data.materials.new("Review floor")
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.11, 0.13, 0.14, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.88
    ground.data.materials.append(mat)
    height = TARGETS[obj.name][0][2] / 100
    target = (0, 0, height / 2)
    for index, (location, power, size) in enumerate([
            ((-3, -4, 5), 700, 3), ((4, -2, 2), 400, 2), ((1, 3, 5), 900, 3)]):
        data = bpy.data.lights.new("Review area " + str(index), "AREA")
        data.energy = power
        data.size = size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, target)
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(TARGETS[obj.name][0][0], TARGETS[obj.name][0][2]) / 100 * 1.35
    scene.camera = camera
    paths = []
    for view, position in (("front", (0, -5, height / 2 + 0.06)),
                           ("threequarter", (2.6, -5, height / 2 + 1.5))):
        camera.location = position
        aim(camera, target)
        path = QA / f"{obj.name}_{view}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(str(path))
    return paths


def verify_coordinates(manifest):
    sys.path.insert(0, str(HERE.parents[1] / "Tools/Editor"))
    from CityVenueDressing import ROOMS
    guide = manifest["guideVenueCoordinates"]
    assert len(guide["venues"]) == len(ROOMS) == 8
    assert guide["title"] == "NEIGHBORHOOD GUIDE"
    for number, (entry, room) in enumerate(zip(guide["venues"], ROOMS), 1):
        assert entry["number"] == number and entry["id"] == room["id"]
        assert entry["centreCm"] == list(room["centre"])
        x, y = room["centre"]
        origin = guide["originPixel"]
        scale = guide["pixelsPerCm"]
        expected = [round(origin[0] + x * scale, 3), round(origin[1] - y * scale, 3)]
        assert entry["markerPixel"] == expected

def main():
    manifest = json.loads((BASE / "venue_fixture_manifest.json").read_text(encoding="utf-8"))
    verify_coordinates(manifest)
    reports = []
    for entry in manifest["meshes"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path = BASE / entry["file"]
        assert materials.digest(path) == entry["sha256"]
        bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
        assert len(meshes) == 1
        obj = meshes[0]
        report = inspect(obj, entry)
        materials.build_materials(manifest["materials"], BASE)
        report["renders"] = render(obj)
        reports.append(report)
    for item in manifest["materials"]:
        for role in ("baseColor", "normal", "roughness"):
            if item[role]:
                image = bpy.data.images.load(str(BASE / item[role]), check_existing=True)
                assert max(image.size) <= 2048
    for record in manifest["sourceFiles"]:
        assert materials.digest(BASE / record["file"]) == record["sha256"], record
    result = dict(status="PASS", passed=True, blender=bpy.app.version_string, meshes=reports,
                  sourceHashesVerified=len(manifest["sourceFiles"]), renderEngine="Cycles CPU", threads=2,
                  unrealVerified=False,
                  limitations=["Tiled PBR UVs intentionally overlap; generate separate lightmap UVs in Unreal."])
    (QA / "audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(result))


if __name__ == "__main__":
    main()
