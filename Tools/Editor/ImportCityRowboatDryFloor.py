"""Replace only the audited rowboat FBX and verify the resulting Unreal geometry."""

import hashlib
import json
from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import ROOT, create_material
from ImportCityAssets import import_mesh


def reimport_rowboat(item, source):
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
    task.filename = str(source / item["file"])
    task.destination_path = f"{ROOT}/Meshes"
    task.destination_name = "SM_Rowboat"
    task.automated = True
    # Import cu chi tai su dung mesh; buoc nay thay that geometry cua FBX da sua.
    task.replace_existing = True
    task.replace_existing_settings = True
    task.options = options
    task.factory = unreal.FbxFactory()
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return import_mesh(item, source)


def verify_bounds(mesh, expected):
    box = mesh.get_bounding_box()
    minimum = expected["min"]
    maximum = expected["max"]
    corners = (
        (box.min, (minimum[0], -maximum[1], minimum[2])),
        (box.max, (maximum[0], -minimum[1], maximum[2])),
    )
    for corner, target in corners:
        actual = (corner.x, corner.y, corner.z)
        assert max(abs(a - b) for a, b in zip(actual, target)) < 1, (actual, target)


def bind_materials(mesh, expected):
    names = [str(slot.material_slot_name) for slot in mesh.static_materials]
    assert len(names) == len(expected) and set(names) == set(expected), names
    bindings = []
    # Reimport giu thu tu slot cu; gan theo ten, khong theo index trong FBX moi.
    for index, name in enumerate(names):
        path = f"{ROOT}/Materials/M_{name}"
        material = unreal.load_asset(path)
        assert material, path
        mesh.set_material(index, material)
        bindings.append(dict(index=index, name=name, material=material.get_path_name()))
    return bindings


def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "metro_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1 and manifest["units"] == "cm"
    assert manifest["upAxis"] == "Z" and manifest["forwardAxis"] == "X"
    for entry in manifest["meshes"] + manifest["sourceFiles"]:
        digest = hashlib.sha256((source / entry["file"]).read_bytes()).hexdigest()
        assert digest == entry["sha256"], entry["file"]
    item = next(entry for entry in manifest["meshes"] if entry["id"] == "Rowboat")
    assert item["triangles"] == 4120
    assert item["materialSlots"] == ["City_wood_floor", "Living_Enamel", "Living_Steel"]
    materials = {entry["id"]: entry for entry in manifest["materials"]}
    created = []
    for slot in item["materialSlots"]:
        if not unreal.load_asset(f"{ROOT}/Materials/M_{slot}"):
            created.append(create_material(materials[slot], source))
    result = reimport_rowboat(item, source)
    mesh = unreal.load_asset(result["asset"])
    assert mesh
    # GetNumTriangles doc render LOD fallback; geometry Nanite co bo dem rieng.
    nanite_triangles = mesh.get_num_nanite_triangles()
    assert nanite_triangles == item["triangles"], (nanite_triangles, item["triangles"])
    assert len(mesh.static_materials) == len(item["materialSlots"])
    bindings = bind_materials(mesh, item["materialSlots"])
    verify_bounds(mesh, item["boundsCm"])
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    assert editor
    reductions = [
        unreal.StaticMeshReductionSettings(percent_triangles=ratio, screen_size=screen)
        for ratio, screen in ((1, 1), (.5, .35), (.18, .12))
    ]
    editor.set_lods(mesh, unreal.StaticMeshReductionOptions(
        auto_compute_lod_screen_size=False,
        reduction_settings=reductions,
    ))
    assert editor.get_lod_count(mesh) == 3
    if editor.get_simple_collision_count(mesh) == 0:
        editor.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
    assert editor.get_simple_collision_count(mesh) > 0
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    assert mesh.get_num_nanite_triangles() == item["triangles"]
    result.update(
        triangles=mesh.get_num_nanite_triangles(),
        triangleRepresentation="Nanite",
        fallbackTriangles=mesh.get_num_triangles(0),
        lods=editor.get_lod_count(mesh),
        collisionPrimitives=editor.get_simple_collision_count(mesh),
        materialAssets=[slot.material_interface.get_path_name() for slot in mesh.static_materials],
        slotBindings=bindings,
        sourceSha256=item["sha256"],
    )
    report = dict(
        passed=True,
        importedGeometry=True,
        mesh=result,
        createdMaterials=created,
        visualAccepted=False,
        gameplayAccepted=False,
    )
    path = PROJECT / "Saved/QA/CityMetroAssets/rowboat_dry_floor_import.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_ROWBOAT_DRY_FLOOR_IMPORT_OK triangles=4120 lods=3")


if __name__ == "__main__":
    main()
