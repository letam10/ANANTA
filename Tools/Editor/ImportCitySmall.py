"""Import eight audited props, reusing existing living materials and ordinary LODs."""

import hashlib
import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CitySmallDetails import REQUIRED
from CityScene import material_asset
from ImportCityAssets import import_mesh

def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "small_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1 and manifest["units"] == "cm"
    assert manifest["upAxis"] == "Z" and manifest["forwardAxis"] == "X"
    assert {item["id"] for item in manifest["meshes"]} == set(REQUIRED)
    for item in manifest["meshes"] + manifest["sourceFiles"]:
        assert hashlib.sha256((source / item["file"]).read_bytes()).hexdigest() == item["sha256"]
    for item in manifest["materials"]:
        material_asset(item["id"])
    report = dict(meshes=[], visualAccepted=False, placementAccepted=False)
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    for item in manifest["meshes"]:
        result = import_mesh(item, source)
        mesh = unreal.load_asset(result["asset"])
        bounds = mesh.get_bounding_box()
        minimum, maximum = item["boundsCm"]["min"], item["boundsCm"]["max"]
        for corner, expected in ((bounds.min, (minimum[0], -maximum[1], minimum[2])),
                                 (bounds.max, (maximum[0], -minimum[1], maximum[2]))):
            assert max(abs(a - b) for a, b in zip((corner.x, corner.y, corner.z), expected)) < 1, item["id"]
        settings = mesh.get_editor_property("nanite_settings")
        settings.set_editor_property("enabled", False)
        mesh.set_editor_property("nanite_settings", settings)
        recommendation = item["lodRecommendation"]
        reductions = [unreal.StaticMeshReductionSettings(percent_triangles=ratio, screen_size=screen)
                      for ratio, screen in zip(recommendation["triangleRatios"], recommendation["screenSizes"])]
        editor.set_lods(mesh, unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,
                                                              reduction_settings=reductions))
        assert editor.get_lod_count(mesh) == 3, item["id"]
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh), item["id"]
        result["lods"] = 3
        report["meshes"].append(result)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    path = PROJECT / "Saved/QA/CitySmallAssets/import.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_SMALL_IMPORT_OK meshes=8")

if __name__ == "__main__":
    main()
