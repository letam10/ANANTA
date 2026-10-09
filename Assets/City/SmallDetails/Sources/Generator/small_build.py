"""Build eight room props while reusing the existing living PBR texture records."""
import json
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Matrix

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from finishing_materials import digest, build_materials
from small_models import BUILDERS

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "SmallDetails"
QA = ROOT / "Saved/QA/CitySmallAssets"
IDS = ["CookingPot", "Saucepan", "KitchenBowl", "CoffeeMug",
       "MakeupCompact", "ToyBlocks", "RoomVase", "BathroomSoap"]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def export(obj):
    low = [min(v.co[i] for v in obj.data.vertices) for i in range(3)]
    high = [max(v.co[i] for v in obj.data.vertices) for i in range(3)]
    offset = (-(low[0] + high[0]) / 2, -(low[1] + high[1]) / 2, -low[2])
    obj.data.transform(Matrix.Translation(offset))
    low = [round((low[i] + offset[i]) * 100, 4) for i in range(3)]
    high = [round((high[i] + offset[i]) * 100, 4) for i in range(3)]
    obj.data.calc_loop_triangles()
    record = dict(id=obj.name, file=f"SmallDetails/Meshes/{obj.name}.fbx",
                  boundsCm=dict(min=low, max=high, size=[round(high[i] - low[i], 4) for i in range(3)]),
                  triangles=len(obj.data.loop_triangles), materialSlots=[m.name for m in obj.data.materials],
                  source="Original ANANTA dimensioned room prop geometry", license="Original project asset",
                  lodRecommendation=dict(screenSizes=[1, .35, .12], triangleRatios=[1, .5, .25]),
                  triangleBudget=1999, forwardAxis="X", origin="base center")
    assert record["triangles"] < 2000 and len(record["materialSlots"]) <= 3, record
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
    for path in (OUT / "Meshes", OUT / "Sources/Generator", QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    living = json.loads((BASE / "living_manifest.json").read_text(encoding="utf-8"))
    materials = [m for m in living["materials"] if m["id"] in ("Living_Enamel", "Living_Steel", "Living_Dark")]
    build_materials(materials, BASE)
    records = [export(builder()) for builder in BUILDERS]
    provenance = dict(geometry="Original simple low polygon hollow vessels and functional room silhouettes",
                      textures="Reused unchanged living_manifest.json 1K PBR channels; no duplicate textures",
                      license="Original project asset", thirdPartyAssets=[],
                      authoring="Blender 5.2 metres; FBX centimetres, +X front, +Z up, base centered origin",
                      lods="Recommendations only; engine reduction must generate lower LOD meshes",
                      status="Static room decorations; no interactive cooking or cosmetics gameplay")
    write_json(OUT / "Sources/Provenance.json", provenance)
    dependencies = ["geometry.py", "living_geometry.py", "finishing_materials.py"]
    for source in list(HERE.glob("small_*.py")) + [HERE / name for name in dependencies]:
        shutil.copy2(source, OUT / "Sources/Generator" / source.name)
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "SmallDetails.blend"))
    sources = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and "Meshes" not in path.parts:
            sources.append(dict(file=path.relative_to(BASE).as_posix(), sha256=digest(path),
                                source="Original ANANTA small room prop source", license="Original project asset"))
    texture_paths = {m[role] for m in materials for role in ("baseColor", "normal", "roughness") if m[role]}
    sources.extend(item for item in living["sourceFiles"] if item["file"] in texture_paths)
    manifest = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=records,
                    materials=materials, sourceFiles=sources)
    write_json(BASE / "small_manifest.json", manifest)
    write_json(QA / "build.json", dict(status="PASS", blender=bpy.app.version_string, meshes=records))
    print("RESULT " + json.dumps(dict(status="PASS", meshes=len(records),
                                      triangles={r["id"]: r["triangles"] for r in records})))


if __name__ == "__main__":
    main()
