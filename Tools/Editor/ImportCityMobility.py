"""Import audited transport sources, generate LODs and preserve existing content."""

import hashlib
import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import create_material
from ImportCityAssets import import_mesh
from CityDistrictMaterials import create as create_district_materials


def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "mobility_manifest.json").read_text(encoding="utf-8"))
    assert manifest["units"] == "cm" and len(manifest["meshes"]) == 17
    for entry in manifest["meshes"]:
        actual = hashlib.sha256((source / entry["file"]).read_bytes()).hexdigest()
        assert actual == entry["sha256"], entry["id"]
    report = dict(materials=[], meshes=[], runtimeVerified=False)
    for entry in manifest["materials"]:
        report["materials"].append(create_material(entry, source))
    create_district_materials()
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    for entry in manifest["meshes"]:
        result = import_mesh(entry, source)
        mesh = unreal.load_asset(result["asset"])
        box = mesh.get_bounding_box()
        actual = [box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z]
        assert max(abs(a - b) for a, b in zip(actual, entry["boundsCm"]["size"])) < 1, entry["id"]
        recommendation = entry["lodRecommendation"]
        reductions = [unreal.StaticMeshReductionSettings(percent_triangles=ratio, screen_size=screen)
                      for ratio, screen in zip(recommendation["triangleRatios"], recommendation["screenSizes"])]
        options = unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,
                                                   reduction_settings=reductions)
        editor.set_lods(mesh, options)
        assert editor.get_lod_count(mesh) == len(reductions), entry["id"]
        if editor.get_simple_collision_count(mesh) == 0:
            editor.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        result["lods"] = editor.get_lod_count(mesh)
        result["simpleCollision"] = editor.get_simple_collision_count(mesh)
        report["meshes"].append(result)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    path = PROJECT / "Saved/QA/CityMobilityAssets/import.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_MOBILITY_IMPORT_OK meshes=17")


if __name__ == "__main__":
    main()
