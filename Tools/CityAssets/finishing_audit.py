"""Independent factory-startup FBX roundtrip and two-thread CPU previews."""
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
from finishing_build import BASE, OUT, QA, BUDGETS


def numeric(obj, entry):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    low = [min(point[i] for point in points) for i in range(3)]
    high = [max(point[i] for point in points) for i in range(3)]
    size = [(high[i] - low[i]) * 100 for i in range(3)]
    mesh = obj.data
    mesh.calc_loop_triangles()
    degenerate = sum(face.area < 1e-10 for face in mesh.polygons)
    uv = mesh.uv_layers.active
    zero_uv = 0
    for face in mesh.polygons:
        points_uv = [uv.data[index].uv.copy() for index in face.loop_indices]
        area = abs(sum(points_uv[i].cross(points_uv[(i + 1) % len(points_uv)]) for i in range(len(points_uv))))
        zero_uv += area < 1e-12
    slots = [slot.material.name for slot in obj.material_slots]
    error = max(abs(size[i] - entry["boundsCm"]["size"][i]) for i in range(3))
    expected = {"InteriorWovenRug": [300, 200, 1.5], "InteriorLinenCurtain": [240, 24, 260]}
    target_error = max(abs(size[i] - expected[obj.name][i]) for i in range(3)) if obj.name in expected else 0
    report = dict(id=obj.name, dimensionsCm=size, triangles=len(mesh.loop_triangles),
                  degenerateFaces=degenerate, uvLayers=len(mesh.uv_layers), zeroAreaUvFaces=zero_uv,
                  materialSlots=slots, roundtripMaxErrorCm=error, targetMaxErrorCm=target_error,
                  origin=list(obj.location), finiteVertices=all(math.isfinite(v) for p in points for v in p))
    assert error < 0.02 and target_error < 0.1, report
    assert len(mesh.loop_triangles) == entry["triangles"] <= BUDGETS[obj.name], report
    assert slots == entry["materialSlots"] and len(slots) <= 4, report
    assert degenerate == zero_uv == 0 and report["finiteVertices"], report
    assert min(low[2], obj.location.length) > -0.0001 and obj.location.length < 0.0001, report
    return report


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def preview(obj, records):
    for slot in obj.material_slots:
        slot.material = bpy.data.materials[slot.material.name]
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("QA neutral world")
    scene.world.color = (0.12, 0.12, 0.12)
    scene.view_settings.view_transform = "AgX"
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.012))
    ground = bpy.context.object
    ground_mat = bpy.data.materials.new("QA neutral ground")
    ground_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.12, 0.14, 0.17, 1)
    ground_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
    ground.data.materials.append(ground_mat)
    target = (0, 0, 1.25 if "Curtain" in obj.name else 0.25 if "Sofa" in obj.name else 0)
    camera_at = (3.7, -6, 3.1) if "Curtain" in obj.name else (3, -4.5, 2.6)
    if "Rug" in obj.name:
        camera_at = (2.8, -3.6, 4.8)
    bpy.ops.object.camera_add(location=camera_at)
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.5 if "Curtain" in obj.name else 3.7
    aim(camera, target)
    scene.camera = camera
    for index, (location, energy, size) in enumerate([
            ((-3, -4, 6), 850, 4), ((4, -1, 3.5), 450, 3), ((0, 3, 5), 1000, 3)]):
        light_data = bpy.data.lights.new("QA area " + str(index), "AREA")
        light_data.energy = energy
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(light_data.name, light_data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, target)
    path = QA / (obj.name + "_material.png")
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def main():
    manifest = json.loads((BASE / "finishing_manifest.json").read_text(encoding="utf-8"))
    reports = []
    for entry in manifest["meshes"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path = BASE / entry["file"]
        assert materials.digest(path) == entry["sha256"]
        bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)
        obj = next(obj for obj in bpy.context.scene.objects if obj.type == "MESH")
        reports.append(numeric(obj, entry))
        materials.build_materials(manifest["materials"], BASE)
        reports[-1]["preview"] = preview(obj, manifest["materials"])
    for record in manifest["sourceFiles"]:
        assert materials.digest(BASE / record["file"]) == record["sha256"], record
    result = dict(passed=True, meshes=reports, sourcesVerified=len(manifest["sourceFiles"]),
                  blender=bpy.app.version_string, renderEngine="Cycles CPU", threads=2,
                  warnings=["Unreal import and in-game appearance have not been tested.",
                            "Velvet sheen and specular tint approximated with plain metal-rough shading.",
                            "Tiled cloth UVs intentionally overlap; use separate lightmap UV generation."])
    (QA / "audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(result))


if __name__ == "__main__":
    main()
