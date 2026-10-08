"""Import the audited city sources and verify resulting mesh/material packages."""

import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import ROOT, create_material, street_materials


def import_mesh(item, source_root):
    destination = f"{ROOT}/Meshes/SM_{item['id']}"
    mesh = unreal.load_asset(destination)
    if not mesh:
        options = unreal.FbxImportUI()
        options.set_editor_property("import_mesh", True)
        options.set_editor_property("import_as_skeletal", False)
        options.set_editor_property("import_materials", False)
        options.set_editor_property("import_textures", False)
        options.set_editor_property("automated_import_should_detect_type", False)
        options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
        data = options.get_editor_property("static_mesh_import_data")
        data.set_editor_property("combine_meshes", True)
        data.set_editor_property("auto_generate_collision", True)
        data.set_editor_property("import_uniform_scale", 1.0)
        task = unreal.AssetImportTask()
        task.filename = str(source_root / item["file"])
        task.destination_path = f"{ROOT}/Meshes"
        task.destination_name = f"SM_{item['id']}"
        task.automated = True
        task.options = options
        task.factory = unreal.FbxFactory()
        task.save = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        mesh = unreal.load_asset(destination)
    if not mesh:
        raise RuntimeError(f"Mesh import missing: {destination}")
    for index, slot in enumerate(item["materialSlots"]):
        material = unreal.load_asset(f"{ROOT}/Materials/M_{slot}")
        if not material:
            raise RuntimeError(f"Missing material {slot} for {item['id']}")
        mesh.set_material(index, material)
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    if editor.get_lod_count(mesh) < 1:
        raise RuntimeError(f"Mesh has no LOD: {destination}")
    needs_collision = item["id"].startswith("House_") or item["id"] in (
        "CafeCounter", "CafeTable", "ApartmentBed", "Bench", "Bollard", "WorkshopPartsCrate")
    if needs_collision and editor.get_simple_collision_count(mesh) == 0:
        editor.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
        if editor.get_simple_collision_count(mesh) == 0:
            raise RuntimeError(f"Collision generation failed: {destination}")
    if item["id"].startswith("House_") and editor.get_lod_count(mesh) == 1:
        reductions = [unreal.StaticMeshReductionSettings(percent_triangles=ratio, screen_size=screen)
                      for ratio, screen in ((1.0, 1.0), (0.45, 0.35), (0.16, 0.12))]
        options = unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,
                                                   reduction_settings=reductions)
        editor.set_lods(mesh, options)
        if editor.get_lod_count(mesh) != 3:
            raise RuntimeError(f"LOD generation failed: {destination}")
    if not item["id"].startswith("House_"):
        settings = mesh.get_editor_property("nanite_settings")
        settings.set_editor_property("enabled", True)
        mesh.set_editor_property("nanite_settings", settings)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    box = mesh.get_bounding_box()
    bounds = box.max - box.min
    expected = item.get("boundsCm")
    if isinstance(expected, dict):
        expected = expected["size"]
    if isinstance(expected, list) and len(expected) == 3:
        for actual, target in zip((bounds.x, bounds.y, bounds.z), expected):
            if target > 1 and abs(actual - target) / target > 0.1:
                raise RuntimeError(f"Import unit mismatch {item['id']}: {bounds} != {expected}")
    return {"id": item["id"], "asset": destination, "slots": len(mesh.static_materials),
            "boundsCm": [bounds.x, bounds.y, bounds.z],
            "collisionPrimitives": editor.get_simple_collision_count(mesh)}


def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1
    report = {"materials": [], "meshes": []}
    materials = manifest["materials"] + street_materials(manifest["materials"])
    for item in materials:
        report["materials"].append(create_material(item, source))
    for item in manifest["meshes"]:
        report["meshes"].append(import_mesh(item, source))
    path = PROJECT / "Saved/QA/CityImport.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_IMPORT_OK meshes={len(report['meshes'])} materials={len(report['materials'])}")


if __name__ == "__main__":
    main()
