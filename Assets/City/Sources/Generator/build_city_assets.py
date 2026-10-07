"""Run with Blender background factory startup; exports only owned city assets."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import architecture
import materials
import props
from geometry import MATERIALS, box, combine, clean_mesh

ROOT = HERE.parents[1]
OUT = ROOT / "Assets/City"
QA = ROOT / "Saved/QA/CityAssets"


def bounds(obj):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    low = [min(p[i] for p in points) for i in range(3)]
    high = [max(p[i] for p in points) for i in range(3)]
    return dict(min=[round(v * 100, 4) for v in low], max=[round(v * 100, 4) for v in high],
                size=[round((high[i] - low[i]) * 100, 4) for i in range(3)])


def export(obj, source="Original ANANTA city kit", license_name="Original project asset"):
    mesh = obj.data
    assert mesh.uv_layers and len(mesh.polygons)
    mesh.calc_loop_triangles()
    path = OUT / "Meshes" / (obj.name + ".fbx")
    record = dict(id=obj.name, file=path.relative_to(OUT).as_posix(), boundsCm=bounds(obj),
                  materialSlots=[slot.material.name for slot in obj.material_slots],
                  triangles=len(mesh.loop_triangles), source=source, license=license_name)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # X/Y/Z duoc giu nguyen; toa do cm va FBX UnitScaleFactor=1.
    mesh.transform(Matrix.Scale(100, 4))
    bpy.context.scene.unit_settings.scale_length = 0.01
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"},
                             axis_forward="X", axis_up="Z", use_space_transform=True,
                             global_scale=1, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             bake_space_transform=False, mesh_smooth_type="FACE", use_tspace=True,
                             add_leaf_bones=False, bake_anim=False, path_mode="STRIP")
    mesh.transform(Matrix.Scale(0.01, 4))
    bpy.context.scene.unit_settings.scale_length = 1
    record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    record["collision"] = "Custom simple boxes; facade windows cosmetic, preserve entry gap"
    record["lodRecommendation"] = {"screenSizes": [1.0, 0.4, 0.15], "triangleRatios": [1, 0.5, 0.2]}
    return record


def import_house(entry):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(OUT / entry["sourceFile"]))
    imported = set(bpy.data.objects) - before
    meshes = sorted((obj for obj in imported if obj.type == "MESH"), key=lambda obj: obj.name)
    other_objects = sorted((obj for obj in imported if obj.type != "MESH"), key=lambda obj: obj.name)
    raw = json.loads((OUT / entry["sourceFile"]).read_text(encoding="utf-8"))
    for obj in meshes:
        matrix = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = matrix
        for slot in obj.material_slots:
            for index, mat in enumerate(raw["materials"]):
                if slot.material.name == mat["name"] or slot.material.name.startswith(mat["name"] + "."):
                    slot.material = MATERIALS[entry["slots"][index]]
                    break
    obj = combine(entry["id"], meshes, tile_uv=False)
    for other in other_objects:
        if other.name in bpy.data.objects:
            bpy.data.objects.remove(other, do_unlink=True)
    extent = bounds(obj)
    offset = Vector(((extent["min"][0] + extent["max"][0]) / 200,
                     (extent["min"][1] + extent["max"][1]) / 200, extent["min"][2] / 100))
    for vertex in obj.data.vertices:
        vertex.co -= offset
    if len(obj.data.polygons) > 35000:
        mod = obj.modifiers.new("Game mesh reduction", "DECIMATE")
        mod.ratio = 35000 / len(obj.data.polygons)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        clean_mesh(obj)
    return obj


def extras():
    box("Counter cabinet", (0, 0, 0.49), (2.8, 0.70, 0.98), "Wood", 0.02)
    box("Counter stone top", (0, 0, 1.01), (2.94, 0.83, 0.08), "Stone", 0.018)
    for x in [-0.93, 0, 0.93]:
        box("Panel seam", (x, -0.357, 0.50), (0.025, 0.02, 0.86), "Dark", 0.003)
    counter = combine("CafeCounter")
    for x in [-0.48, 0.48]:
        for y in [-0.32, 0.32]:
            box("Table leg", (x, y, 0.36), (0.055, 0.055, 0.72), "Dark")
    box("Table top", (0, 0, 0.74), (1.2, 0.84, 0.06), "Wood", 0.025)
    table = combine("CafeTable")
    box("Bed frame", (0, 0, 0.20), (1.70, 2.18, 0.36), "Wood", 0.035)
    box("Mattress", (0, 0, 0.48), (1.60, 2.05, 0.28), "Linen", 0.12)
    box("Headboard", (0, 1.04, 0.69), (1.72, 0.12, 1.12), "Wood", 0.05)
    box("Blanket", (0, -0.31, 0.63), (1.62, 1.42, 0.13), "Denim", 0.06)
    for x in [-0.41, 0.41]:
        box("Pillow", (x, 0.67, 0.68), (0.66, 0.46, 0.17), "Linen", 0.08)
    bed = combine("ApartmentBed")
    return [counter, table, bed]


def main():
    assert bpy.app.version >= (5, 2, 0), bpy.app.version_string
    for folder in [OUT / "Meshes", QA]:
        folder.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = "METRIC"
    catalog = json.loads((OUT / "source_catalog.json").read_text(encoding="utf-8"))
    materials.build(catalog["materials"], OUT)
    objects = [architecture.facade(kind) for kind in ["Residential", "Commercial", "Tower"]]
    objects.extend([architecture.storefront(), architecture.storefront("CafeEntry"),
                    architecture.storefront("ApartmentEntry", True), architecture.cornice(),
                    architecture.balcony(), architecture.roof_equipment(), props.lamp(), props.bench(),
                    props.bollard(), props.planter(), props.car()])
    objects.extend(extras())
    records = [export(obj) for obj in objects]
    for entry in catalog["models"]:
        obj = import_house(entry)
        objects.append(obj)
        records.append(export(obj, entry["source"], entry["license"]))
    for script in sorted(HERE.glob("*.py")):
        target = OUT / "Sources/Generator" / script.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(script.read_bytes())
        catalog["sourceFiles"].append(dict(file=target.relative_to(OUT).as_posix(),
                                           sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                                           source=str(script), license="Original project asset"))
    manifest = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=records,
                    materials=catalog["materials"], sourceFiles=catalog["sourceFiles"])
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "CityKit.blend"))
    print("RESULT " + json.dumps(dict(meshes=len(records), triangles=sum(x["triangles"] for x in records))))


if __name__ == "__main__":
    main()
