"""Create the HLOD layer consumed by the new map conversion."""

from pathlib import Path
import sys
import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()).resolve() / "Tools/Editor"))
from CityHLODMaterial import create_hlod_material


def main():
    path = "/Game/ANANTA/City/HLOD"
    full = path + "/City_HLOD"
    layer = unreal.load_asset(full)
    if not layer:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        layer = tools.create_asset("City_HLOD", path, unreal.HLODLayer, unreal.HLODLayerFactory())
    layer.set_editor_property("layer_type", unreal.HLODLayerType.MESH_SIMPLIFY)
    layer.set_editor_property("cell_size", 25600)
    layer.set_editor_property("loading_range", 120000.0)
    layer.set_editor_property("is_spatially_loaded", True)
    builder = layer.get_editor_property("hlod_builder_settings")
    assert isinstance(builder, unreal.HLODBuilderMeshSimplifySettings)
    proxy = builder.get_editor_property("mesh_simplify_settings")
    settings = proxy.get_editor_property("material_settings")
    for name in ("normal_map", "emissive_map", "roughness_map", "metallic_map"):
        settings.set_editor_property(name, True)
    proxy.set_editor_property("material_settings", settings)
    proxy.set_editor_property("calculate_correct_lod_model", True)
    proxy.set_editor_property("group_identical_meshes_for_baking", False)
    builder.set_editor_property("mesh_simplify_settings", proxy)
    builder.set_editor_property("hlod_material", create_hlod_material())
    unreal.EditorAssetLibrary.save_loaded_asset(layer)
    unreal.log("CITY_HLOD_LAYER_READY")


if __name__ == "__main__":
    main()
