"""Import the owned FBX kit with one vertex-color material and three LODs."""

import json
from pathlib import Path

import unreal


ROOT = Path(unreal.Paths.project_dir())
DEST = "/Game/ANANTA/CoastalUpgrade"


def main():
    library = unreal.EditorAssetLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    path = f"{DEST}/M_CoastalSurface"
    surface = library.load_asset(path) if library.does_asset_exist(path) else None
    if not surface:
        surface = tools.create_asset("M_CoastalSurface", DEST, unreal.Material, unreal.MaterialFactoryNew())
        editing = unreal.MaterialEditingLibrary
        vertex = editing.create_material_expression(surface, unreal.MaterialExpressionVertexColor, -350, 0)
        editing.connect_material_property(vertex, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        editing.connect_material_property(vertex, "A", unreal.MaterialProperty.MP_ROUGHNESS)
        metal = editing.create_material_expression(surface, unreal.MaterialExpressionConstant, -350, 200)
        metal.set_editor_property("r", 0.12)
        editing.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
        editing.recompile_material(surface)
        library.save_loaded_asset(surface)
    source = ROOT / "Assets" / "CoastalUpgrade"
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    tasks = []
    for item in manifest["models"]:
        task = unreal.AssetImportTask()
        task.filename = str(source / f"{item['name']}.fbx")
        task.destination_path = f"{DEST}/Models"
        task.destination_name = item["name"]
        task.automated = True
        task.replace_existing = True
        task.save = True
        task.factory = unreal.FbxFactory()
        options = unreal.FbxImportUI()
        options.import_mesh = True
        options.import_materials = False
        options.import_textures = False
        options.import_as_skeletal = False
        options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        data = options.static_mesh_import_data
        data.combine_meshes = True
        data.auto_generate_collision = False
        data.vertex_color_import_option = unreal.VertexColorImportOption.REPLACE
        task.options = options
        tasks.append(task)
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    tools.import_asset_tasks(tasks)
    # Commandlet không khởi tạo collection EditorSubsystem; API này không giữ state.
    subsystem = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    readback = []
    for item in manifest["models"]:
        mesh = library.load_asset(f"{DEST}/Models/{item['name']}")
        if not mesh:
            raise RuntimeError(f"Import failed: {item['name']}")
        mesh.set_material(0, surface)
        reductions = [
            unreal.StaticMeshReductionSettings(percent_triangles=1.0, screen_size=1.0),
            unreal.StaticMeshReductionSettings(percent_triangles=0.5, screen_size=0.25),
            unreal.StaticMeshReductionSettings(percent_triangles=0.2, screen_size=0.08),
        ]
        options = unreal.StaticMeshReductionOptions(
            auto_compute_lod_screen_size=False, reduction_settings=reductions
        )
        assert subsystem.set_lods(mesh, options) == 3, item["name"]
        subsystem.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
        library.save_loaded_asset(mesh)
        bounds = mesh.get_bounds().box_extent
        actual = [2 * bounds.x, 2 * bounds.y, 2 * bounds.z]
        expected = [100 * value for value in item["dimensions_m"]]
        assert all(abs(a - b) < 0.1 for a, b in zip(actual, expected)), (item["name"], actual, expected)
        readback.append({
            "name": item["name"], "dimensions_cm": actual,
            "lod_count": subsystem.get_lod_count(mesh),
            "collision_shapes": subsystem.get_simple_collision_count(mesh),
            "materials": len(mesh.static_materials),
        })
    report = ROOT / "Saved" / "Upgrade" / "import-readback.json"
    report.write_text(json.dumps(readback, indent=2), encoding="utf-8")
    unreal.log(f"COASTAL_IMPORT_OK {len(readback)} models with 3 LODs; dimensions verified")


if __name__ == "__main__":
    main()
