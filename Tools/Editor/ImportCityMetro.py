"""Import original audited metro FBX models with exact bounds, shared materials and LODs."""

import hashlib
import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import create_material
from ImportCityAssets import import_mesh


def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "metro_manifest.json").read_text(encoding="utf-8"))
    required = {"FireEngine", "PassengerTrain", "Helicopter", "CivilianPlane", "Rowboat"}
    assert manifest["schemaVersion"] == 1 and manifest["units"] == "cm"
    assert manifest["upAxis"] == "Z" and manifest["forwardAxis"] == "X"
    assert {item["id"] for item in manifest["meshes"]} == required
    for entry in manifest["meshes"] + manifest["sourceFiles"]:
        assert hashlib.sha256((source / entry["file"]).read_bytes()).hexdigest() == entry["sha256"], entry["file"]
    report = dict(materials=[], meshes=[], visualAccepted=False, gameplayAccepted=False)
    for item in manifest["materials"]:
        report["materials"].append(create_material(item, source))
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    for item in manifest["meshes"]:
        result = import_mesh(item, source)
        mesh = unreal.load_asset(result["asset"])
        bounds = mesh.get_bounding_box()
        actual = [bounds.max.x - bounds.min.x, bounds.max.y - bounds.min.y, bounds.max.z - bounds.min.z]
        assert max(abs(a - b) for a, b in zip(actual, item["boundsCm"]["size"])) < 1, item["id"]
        minimum, maximum = item["boundsCm"]["min"], item["boundsCm"]["max"]
        for corner, expected in ((bounds.min, (minimum[0], -maximum[1], minimum[2])),
                                 (bounds.max, (maximum[0], -minimum[1], maximum[2]))):
            assert max(abs(a - b) for a, b in zip((corner.x, corner.y, corner.z), expected)) < 1, item["id"]
        reductions = [unreal.StaticMeshReductionSettings(percent_triangles=ratio, screen_size=screen)
                      for ratio, screen in ((1, 1), (.5, .35), (.18, .12))]
        editor.set_lods(mesh, unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,
                                                              reduction_settings=reductions))
        assert editor.get_lod_count(mesh) == 3, item["id"]
        if editor.get_simple_collision_count(mesh) == 0:
            editor.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
        assert editor.get_simple_collision_count(mesh) > 0, item["id"]
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh), item["id"]
        result.update(lods=3, collisionPrimitives=editor.get_simple_collision_count(mesh))
        report["meshes"].append(result)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    path = PROJECT / "Saved/QA/CityMetroAssets/import.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_METRO_IMPORT_OK meshes=5")


if __name__ == "__main__":
    main()
