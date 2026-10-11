"""Build portable finishing meshes without touching Unreal Content."""
import json
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import build_city_assets as existing
import finishing_geometry as geometry
import finishing_materials as materials
from geometry import MATERIALS, combine

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "Finishing"
QA = ROOT / "Saved/QA/CityFinishingAssets"
BUDGETS = {"House_GlamVelvetSofa": 6000, "InteriorWovenRug": 2500, "InteriorLinenCurtain": 7000}


def sofa():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(OUT / "Sources/HOUSE/GlamVelvetSofa/GlamVelvetSofa.gltf"))
    imported = set(bpy.data.objects) - before
    meshes = [obj for obj in imported if obj.type == "MESH"]
    others = [obj for obj in imported if obj.type != "MESH"]
    for obj in meshes:
        for slot in obj.material_slots:
            name = slot.material.name
            key = "Finish_SofaLegs" if "legs" in name else "Finish_SofaFeet" if "feet" in name else "Finish_VelvetNavy"
            slot.material = MATERIALS[key]
    obj = combine("House_GlamVelvetSofa", meshes, tile_uv=False)
    for other in others:
        if other.name in bpy.data.objects:
            bpy.data.objects.remove(other, do_unlink=True)
    extent = existing.bounds(obj)
    offset = Vector(((extent["min"][0] + extent["max"][0]) / 200,
                     (extent["min"][1] + extent["max"][1]) / 200, extent["min"][2] / 100))
    for vertex in obj.data.vertices:
        vertex.co -= offset
    return obj


def repair_zero_uv(obj):
    """Chi sua UV mat canh mong; giu nguyen UV cua vai va sofa."""
    layer = obj.data.uv_layers.active
    count = 0
    for poly in obj.data.polygons:
        uv = [layer.data[index].uv.copy() for index in poly.loop_indices]
        area = abs(sum(uv[i].cross(uv[(i + 1) % len(uv)]) for i in range(len(uv))))
        if area >= 1e-12:
            continue
        count += 1
        axis = max(range(3), key=lambda i: abs(poly.normal[i]))
        axes = [i for i in range(3) if i != axis]
        for index in poly.loop_indices:
            co = obj.data.vertices[obj.data.loops[index].vertex_index].co
            layer.data[index].uv = (co[axes[0]], co[axes[1]])
    return count


def main():
    assert bpy.app.version >= (5, 2, 0)
    for path in (OUT / "Meshes", OUT / "Sources/Generator", QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = "METRIC"
    records, sources = materials.prepare(BASE, OUT)
    materials.build_materials(records, BASE)
    objects = [sofa(), geometry.rug(), geometry.curtain()]
    existing.OUT = OUT
    meshes = []
    uv_repairs = {}
    for obj in objects:
        uv_repairs[obj.name] = repair_zero_uv(obj)
        source = "GlamVelvetSofa by Eric Chadwick, Wayfair, LLC (2021)"
        if obj.name != "House_GlamVelvetSofa":
            source = "Original ANANTA interior finishing geometry"
        item = existing.export(obj, source, "CC-BY-4.0" if obj.name.startswith("House_") else "Original project asset")
        item["file"] = "Finishing/" + item["file"]
        item.pop("collision")
        item["visibleFront"] = "-Y"
        assert item["triangles"] <= BUDGETS[obj.name], item
        assert len(item["materialSlots"]) <= 4, item
        meshes.append(item)
    for script in sorted(list(HERE.glob("finishing_*.py")) + [HERE / "geometry.py", HERE / "build_city_assets.py"]):
        dest = OUT / "Sources/Generator" / script.name
        shutil.copy2(script, dest)
        sources.append(dict(file=dest.relative_to(BASE).as_posix(), sha256=materials.digest(dest),
                            source="Original project generator", license="Original project asset"))
    doc = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=meshes,
               materials=records, sourceFiles=sources)
    (BASE / "finishing_manifest.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "CityFinishing.blend"))
    result = dict(passed=True, blender=bpy.app.version_string, meshes=meshes, uvEdgeFaceRepairs=uv_repairs)
    (QA / "build.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(result))


if __name__ == "__main__":
    main()
