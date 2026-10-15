"""Import audited living sources and record actual imported bounds and LODs."""

import hashlib
import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityLivingDetails import REQUIRED
from CityMaterials import create_material
from ImportCityAssets import import_mesh


def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "living_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1 and manifest["units"] == "cm"
    assert manifest["upAxis"] == "Z" and manifest["forwardAxis"] == "X"
    assert len(manifest["meshes"]) == len(REQUIRED)
    assert {item["id"] for item in manifest["meshes"]} == set(REQUIRED)
    for entry in manifest["meshes"] + manifest["sourceFiles"]:
        actual = hashlib.sha256((source / entry["file"]).read_bytes()).hexdigest()
        assert actual == entry["sha256"], entry["file"]
    report = dict(materials=[], meshes=[], runtimeVerified=False)
    for entry in manifest["materials"]:
        report["materials"].append(create_material(entry, source))
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    for entry in manifest["meshes"]:
        result = import_mesh(entry, source)
        mesh = unreal.load_asset(result["asset"])
        bounds = mesh.get_bounding_box()
        actual = [bounds.max.x - bounds.min.x, bounds.max.y - bounds.min.y, bounds.max.z - bounds.min.z]
        assert max(abs(a - b) for a, b in zip(actual, entry["boundsCm"]["size"])) < 1, entry["id"]
        minimum, maximum = entry["boundsCm"]["min"], entry["boundsCm"]["max"]
        expected_min = (minimum[0], -maximum[1], minimum[2])
        expected_max = (maximum[0], -minimum[1], maximum[2])
        for actual_corner, expected in ((bounds.min, expected_min), (bounds.max, expected_max)):
            coordinates = (actual_corner.x, actual_corner.y, actual_corner.z)
            assert max(abs(a - b) for a, b in zip(coordinates, expected)) < 1, entry["id"]
        recommendation = entry["lodRecommendation"]
        reductions = [unreal.StaticMeshReductionSettings(percent_triangles=ratio, screen_size=screen)
                      for ratio, screen in zip(recommendation["triangleRatios"], recommendation["screenSizes"])]
        options = unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,
                                                   reduction_settings=reductions)
        editor.set_lods(mesh, options)
        assert editor.get_lod_count(mesh) == len(reductions), entry["id"]
        if editor.get_simple_collision_count(mesh) == 0:
            editor.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
        assert editor.get_simple_collision_count(mesh) > 0, entry["id"]
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh), entry["id"]
        result.update(lods=editor.get_lod_count(mesh), simpleCollision=editor.get_simple_collision_count(mesh))
        report["meshes"].append(result)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    path = PROJECT / "Saved/QA/CityLivingAssets/import.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_LIVING_IMPORT_OK meshes={len(report['meshes'])}")


if __name__ == "__main__":
    main()
