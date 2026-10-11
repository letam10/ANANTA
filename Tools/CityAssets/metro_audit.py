"""Independent manifest and FBX roundtrip audit of all five transit assets."""
import json
import sys
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from metro_build import BASE, QA, BUDGETS, bounds, mesh_audit, write_json
from finishing_materials import digest


def main():
    manifest = json.loads((BASE / "metro_manifest.json").read_text(encoding="utf-8"))
    assert manifest["units"] == "cm"
    assert (manifest["forwardAxis"], manifest["upAxis"]) == ("X", "Z")
    assert {m["id"] for m in manifest["meshes"]} == set(BUDGETS)
    assert len(manifest["meshes"]) == 5
    for record in manifest["meshes"] + manifest["sourceFiles"]:
        assert digest(BASE / record["file"]) == record["sha256"], record["file"]
        if Path(record["file"]).parent.name == "Generator":
            assert digest(HERE / Path(record["file"]).name) == record["sha256"], record["file"]
    materials = {m["id"] for m in manifest["materials"]}
    results = {}
    for record in manifest["meshes"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(BASE / record["file"]), use_custom_normals=True)
        objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        assert len(objects) == 1, record["id"]
        obj = objects[0]
        assert obj.name == record["id"]
        actual = bounds(obj)
        audit = mesh_audit(obj)
        assert audit["triangles"] == record["triangles"] <= BUDGETS[record["id"]]
        assert audit["materialSlots"] == record["materialSlots"]
        assert set(audit["materialSlots"]) <= materials
        assert len(audit["materialSlots"]) <= 5
        assert all(p.material_index < len(obj.material_slots) for p in obj.data.polygons)
        for key in ("min", "max", "size"):
            assert max(abs(a - b) for a, b in zip(actual[key], record["boundsCm"][key])) < .03
        assert abs(actual["min"][2]) < .01
        assert max(abs(actual["min"][i] + actual["max"][i]) for i in (0, 1)) < .03
        results[record["id"]] = dict(audit, boundsCm=actual, sha256=digest(BASE / record["file"]))
    write_json(QA / "fbx_audit.json", dict(status="PASS", count=5, meshes=results,
                                         allManifestHashesVerified=True))
    print("METRO_AUDIT_PASS 5 FBX: bounds, UVs, triangles, materials, origin and hashes")


if __name__ == "__main__":
    main()
