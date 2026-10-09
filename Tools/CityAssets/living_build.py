"""Build, export and hash original living detail assets using background Blender."""
import json
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Matrix

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from finishing_materials import digest
import living_materials
import living_household as household
import living_civic as civic

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "LivingDetails"
QA = ROOT / "Saved/QA/CityLivingAssets"
IDS = ["CeilingFan", "TableLamp", "WallAirConditioner", "Refrigerator", "Microwave", "KitchenSink",
       "FireExtinguisher", "CivicMonument", "PlaygroundSlide", "PlaygroundSwing", "ArcadeCabinet"]
LARGE = ["CivicMonument", "PlaygroundSlide", "PlaygroundSwing"]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def export(obj):
    if obj.name != "CeilingFan":
        bottom = min(vertex.co.z for vertex in obj.data.vertices)
        obj.data.transform(Matrix.Translation((0, 0, -bottom)))
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    low = [round(min(v[i] for v in points) * 100, 4) for i in range(3)]
    high = [round(max(v[i] for v in points) * 100, 4) for i in range(3)]
    obj.data.calc_loop_triangles()
    record = dict(id=obj.name, file=f"LivingDetails/Meshes/{obj.name}.fbx",
                  boundsCm=dict(min=low, max=high, size=[round(high[i] - low[i], 4) for i in range(3)]),
                  triangles=len(obj.data.loop_triangles), materialSlots=[m.name for m in obj.data.materials],
                  source="Original ANANTA living detail authored geometry", license="Original project asset",
                  lodRecommendation=dict(screenSizes=[1, .40, .16], triangleRatios=[1, .5, .2]),
                  triangleBudget=30000 if obj.name in LARGE else 18000, forwardAxis="X",
                  origin="ceiling mount" if obj.name == "CeilingFan" else "base")
    assert record["triangles"] <= record["triangleBudget"] and len(record["materialSlots"]) <= 5, record
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.data.transform(Matrix.Scale(100, 4))
    bpy.context.scene.unit_settings.scale_length = .01
    path = BASE / record["file"]
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"},
                             axis_forward="X", axis_up="Z", use_space_transform=True,
                             global_scale=1, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             bake_space_transform=False, mesh_smooth_type="FACE", use_tspace=True,
                             add_leaf_bones=False, bake_anim=False, path_mode="STRIP")
    obj.data.transform(Matrix.Scale(.01, 4))
    bpy.context.scene.unit_settings.scale_length = 1
    record["sha256"] = digest(path)
    return record


def main():
    assert bpy.app.version >= (5, 2, 0)
    print("BLENDER_VERSION", bpy.app.version_string)
    for path in (OUT / "Meshes", OUT / "Sources/Generator", QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    materials = living_materials.prepare(BASE, OUT)
    builders = [household.ceiling_fan, household.table_lamp, household.air_conditioner,
                household.refrigerator, household.microwave, household.kitchen_sink,
                civic.extinguisher, civic.monument, civic.slide, civic.swing, civic.arcade]
    records = [export(builder()) for builder in builders]
    provenance = dict(geometry="Original dimensioned functional household, civic and playground components",
                      textures="Original deterministic NumPy enamel palette, metal grain, linen weave and granite",
                      license="Original project asset", thirdPartyAssets=[],
                      houseCatalog="D:/APP/HOUSE/assets/manifest.json checked: no matching requested model",
                      houseNearMatch="Hanging industrial lamp is a pendant, not the requested table lamp",
                      authoring="Blender 5.2 metres; FBX centimetres with unit metadata; front +X",
                      lods="Recommendations only; lower LODs require engine mesh reduction",
                      status="Static decorative equipment; no mechanical animation or gameplay implied")
    write_json(OUT / "Sources/Provenance.json", provenance)
    dependencies = ["geometry.py", "finishing_materials.py", "mobility_materials.py"]
    for source in list(HERE.glob("living_*.py")) + [HERE / name for name in dependencies]:
        shutil.copy2(source, OUT / "Sources/Generator" / source.name)
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "LivingDetails.blend"))
    sources = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and "Meshes" not in path.parts:
            sources.append(dict(file=path.relative_to(BASE).as_posix(), sha256=digest(path),
                                source="Original ANANTA living detail source", license="Original project asset"))
    manifest = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=records,
                    materials=materials, sourceFiles=sources)
    write_json(BASE / "living_manifest.json", manifest)
    write_json(QA / "build.json", dict(status="PASS", blender=bpy.app.version_string, meshes=records))
    print("RESULT " + json.dumps(dict(status="PASS", counts=len(records),
                                      triangles={e["id"]: e["triangles"] for e in records})))


if __name__ == "__main__":
    main()
