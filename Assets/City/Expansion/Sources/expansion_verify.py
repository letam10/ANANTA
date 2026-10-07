"""Fresh FBX import checks plus review renders with the existing studio rig."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from review_assets import measure, point_at

BASE = HERE.parents[1] / "Assets/City"
QA = HERE.parents[1] / "Saved/QA/CityExpansionAssets"


def verify(doc):
    known = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
    materials = {x["id"] for x in known["materials"]}
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    reports = []
    for entry in doc["meshes"]:
        path = BASE / entry["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        assert set(entry["materialSlots"]) <= materials, entry
        bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
        objects = [o for o in bpy.context.selected_objects if o.type == "MESH"]
        assert len(objects) == 1, entry
        obj = objects[0]
        bpy.context.view_layer.update()
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        low = [min(p[i] for p in corners) * 100 for i in range(3)]
        size = [(max(p[i] for p in corners) - min(p[i] for p in corners)) * 100 for i in range(3)]
        report = measure(obj)
        report["id"] = entry["id"]
        report["boundsCm"] = size
        report["sizeErrorCm"] = max(abs(size[i] - entry["boundsCm"]["size"][i]) for i in range(3))
        report["originErrorCm"] = max(abs(low[i] - entry["boundsCm"]["min"][i]) for i in range(3))
        actual_slots = [s.material.name.split(".")[0] for s in obj.material_slots]
        report["materialsMatch"] = actual_slots == entry["materialSlots"]
        uv = obj.data.uv_layers.active
        report["nonzeroUVRange"] = bool(uv) and max(v.uv.length for v in uv.data) > 0
        report["passed"] = (report["sizeErrorCm"] < 0.02 and report["originErrorCm"] < 0.02
                            and report["triangles"] == entry["triangles"] and report["materialsMatch"]
                            and report["nonzeroUVRange"] and report["zeroAreaFaces"] == 0)
        reports.append(report)
        bpy.ops.object.delete(use_global=False)
    for source in doc["sourceFiles"]:
        assert hashlib.sha256((BASE / source["file"]).read_bytes()).hexdigest() == source["sha256"]
    result = dict(passed=all(x["passed"] for x in reports), sourceHashesVerified=True, meshes=reports)
    (QA / "fbx_roundtrip.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    assert result["passed"], [x for x in reports if not x["passed"]]
    print("RESULT " + json.dumps(dict(passed=True, fbxMeshes=len(reports), hashesVerified=True)))


def render(doc):
    bpy.ops.wm.open_mainfile(filepath=str(BASE / "Expansion/CityExpansion.blend"))
    objects = [bpy.data.objects[x["id"]] for x in doc["meshes"]]
    for obj in objects:
        obj.hide_render = True
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.resolution_x = 640
    scene.render.resolution_y = 560
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.use_nodes = True
    world = scene.world.node_tree.nodes.get("Background")
    world.inputs["Color"].default_value = (0.24, 0.27, 0.31, 1)
    world.inputs["Strength"].default_value = 0.65
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 4.1
    for name, loc, energy, size in (("Key", (-3, -4, 6), 1100, 4),
                                     ("Fill", (4, -1, 3), 600, 3), ("Rim", (1, 4, 5), 900, 3)):
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        point_at(light, (0, 0, 1))
    ground = bpy.data.materials.new("Review ground")
    ground.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.12, 0.15, 0.19, 1)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.015))
    bpy.context.object.data.materials.append(ground)
    for obj in objects:
        display = obj.copy()
        display.data = obj.data
        bpy.context.collection.objects.link(display)
        display.hide_render = False
        low = Vector([min(c[i] for c in obj.bound_box) for i in range(3)])
        high = Vector([max(c[i] for c in obj.bound_box) for i in range(3)])
        factor = 2.8 / max(high - low)
        display.scale = (factor,) * 3
        display.location = (-(low.x + high.x) * factor / 2,
                            -(low.y + high.y) * factor / 2, -low.z * factor)
        target = Vector((0, 0, (high.z - low.z) * factor / 2))
        views = (("front", (0, -8, 1.3)), ("quarter", (3.8, -7, 2.8)))
        for label, direction in views:
            camera.location = target + Vector(direction)
            point_at(camera, target)
            scene.render.filepath = str(QA / (obj.name + "_" + label + ".png"))
            bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(display, do_unlink=True)
    print("RESULT " + json.dumps(dict(rendered=len(objects) * 2, engine="Cycles", samples=24)))


if __name__ == "__main__":
    manifest = json.loads((BASE / "expansion_manifest.json").read_text(encoding="utf-8"))
    verify(manifest)
    if "--render" in sys.argv:
        render(manifest)
