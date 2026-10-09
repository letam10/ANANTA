"""Build five portable static transit assets and audit every exported FBX."""
import json
import math
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Matrix

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from finishing_materials import build_materials, digest
from metro_road import fire_engine, passenger_train
from metro_air import helicopter, civilian_plane
from metro_boat import rowboat

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "MetroDetails"
QA = ROOT / "Saved/QA/CityMetroAssets"
BUDGETS = dict(FireEngine=18000, PassengerTrain=22000, Helicopter=16000, CivilianPlane=22000, Rowboat=5000)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def bounds(obj):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    low = [round(min(v[i] for v in points) * 100, 4) for i in range(3)]
    high = [round(max(v[i] for v in points) * 100, 4) for i in range(3)]
    return dict(min=low, max=high, size=[round(high[i] - low[i], 4) for i in range(3)])


def mesh_audit(obj):
    obj.data.calc_loop_triangles()
    uv = obj.data.uv_layers.active
    assert uv and len(uv.data) == len(obj.data.loops), obj.name
    assert all(math.isfinite(v) for p in uv.data for v in p.uv), obj.name
    flat_uv = 0
    for tri in obj.data.loop_triangles:
        a, b, c = [uv.data[i].uv for i in tri.loops]
        flat_uv += abs((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)) < 1e-12
    assert flat_uv == 0, (obj.name, flat_uv)
    assert all(face.area > 1e-10 for face in obj.data.polygons), obj.name
    return dict(triangles=len(obj.data.loop_triangles), uvLayers=len(obj.data.uv_layers),
                uvLoops=len(uv.data), degenerateUvTriangles=flat_uv,
                materialSlots=[m.name for m in obj.data.materials])


def export(obj):
    audit = mesh_audit(obj)
    record = dict(id=obj.name, file=f"MetroDetails/Meshes/{obj.name}.fbx", boundsCm=bounds(obj),
                  triangles=audit["triangles"], materialSlots=audit["materialSlots"],
                  triangleBudget=BUDGETS[obj.name], forwardAxis="X", origin="base center",
                  source="Original ANANTA dimensioned static transport geometry", license="Original project asset",
                  lodRecommendation=dict(screenSizes=[1, .4, .16], triangleRatios=[1, .5, .2]),
                  usage="Static scenery only; no rail, flight, rotor or rowing gameplay")
    assert record["triangles"] <= BUDGETS[obj.name], record
    assert len(record["materialSlots"]) <= 5, record
    assert abs(record["boundsCm"]["min"][2]) < .01, record
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
    return record, audit


def main():
    assert bpy.app.version >= (5, 2, 0)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for path in [OUT / "Meshes", OUT / "Sources/Generator", QA]:
        path.mkdir(parents=True, exist_ok=True)
    living = json.loads((BASE / "living_manifest.json").read_text(encoding="utf-8"))
    materials = [m for m in living["materials"] if m["id"] in ["Living_Enamel", "Living_Steel", "Living_Dark"]]
    build_materials(materials, BASE)
    records = []
    audits = {}
    for builder in [fire_engine, passenger_train, helicopter, civilian_plane, rowboat]:
        record, audit = export(builder())
        records.append(record)
        audits[record["id"]] = audit
    provenance = dict(source="Original procedural authored geometry with dimensioned functional components",
                      materials="Reuses existing Living Enamel, Steel and Dark PBR maps without modifying them",
                      license="Original project asset", thirdPartyAssets=[],
                      authoring="Blender 5.2 metres; FBX centimetres, +X front, +Z up, origin bottom centre",
                      limitations="Static meshes only. Recommended LOD ratios are not generated LODs.")
    write_json(OUT / "Sources/Provenance.json", provenance)
    dependencies = ["geometry.py", "living_geometry.py", "finishing_materials.py"]
    for source in list(HERE.glob("metro_*.py")) + [HERE / name for name in dependencies]:
        shutil.copy2(source, OUT / "Sources/Generator" / source.name)
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "MetroDetails.blend"))
    source_files = [dict(file=p.relative_to(BASE).as_posix(), sha256=digest(p),
                         source="Original ANANTA transit source", license="Original project asset")
                    for p in sorted(OUT.rglob("*")) if p.is_file() and "Meshes" not in p.parts]
    for material in materials:
        for key in ["baseColor", "normal", "roughness"]:
            path = BASE / material[key]
            source_files.append(dict(file=material[key], sha256=digest(path),
                                     source="Existing shared ANANTA PBR texture", license="Original project asset"))
    manifest = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=records,
                    materials=materials, sourceFiles=source_files)
    write_json(BASE / "metro_manifest.json", manifest)
    # FBX reimport kiem chung don vi va kich thuoc that sau export.
    for record in records:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(BASE / record["file"]), use_custom_normals=True)
        obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
        actual = bounds(obj)
        assert max(abs(a - b) for a, b in zip(actual["size"], record["boundsCm"]["size"])) < .03
        audits[record["id"]]["fbxRoundTripBoundsCm"] = actual
        assert mesh_audit(obj)["triangles"] == record["triangles"]
    assert len(list((OUT / "Meshes").glob("*.fbx"))) == 5
    write_json(QA / "build_audit.json", dict(status="PASS", blender=bpy.app.version_string,
                                             count=5, meshes=audits, hashesVerified=True))
    print("METRO_BUILD_PASS", json.dumps({r["id"]: r["triangles"] for r in records}))


if __name__ == "__main__":
    main()
