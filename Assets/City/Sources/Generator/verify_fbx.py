"""Independent FBX round trip validation in a fresh Blender process."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets/City"
QA = ROOT / "Saved/QA/CityAssets"


def main():
    doc = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    results = []
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for entry in doc["meshes"]:
        bpy.ops.import_scene.fbx(filepath=str(OUT / entry["file"]), use_anim=False)
        meshes = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
        assert len(meshes) == 1, entry["id"]
        obj = meshes[0]
        bpy.context.view_layer.update()
        points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        size = [(max(p[i] for p in points) - min(p[i] for p in points)) * 100 for i in range(3)]
        low = [min(p[i] for p in points) * 100 for i in range(3)]
        size_error = max(abs(size[i] - entry["boundsCm"]["size"][i]) for i in range(3))
        origin_error = max(abs(low[i] - entry["boundsCm"]["min"][i]) for i in range(3))
        obj.data.calc_loop_triangles()
        triangles = len(obj.data.loop_triangles)
        record = dict(id=entry["id"], boundsCm=size, sizeErrorCm=size_error, originErrorCm=origin_error,
                      triangles=triangles, materialSlots=len(obj.material_slots), uvLayers=len(obj.data.uv_layers))
        record["passed"] = (size_error < 0.02 and origin_error < 0.02 and
                            triangles == entry["triangles"] and bool(obj.data.uv_layers))
        results.append(record)
        bpy.ops.object.delete(use_global=False)
    report = dict(passed=all(item["passed"] for item in results), meshes=results)
    (QA / "fbx_roundtrip.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(dict(passed=report["passed"], meshes=len(results))))
    assert report["passed"], [item for item in results if not item["passed"]]


if __name__ == "__main__":
    main()
