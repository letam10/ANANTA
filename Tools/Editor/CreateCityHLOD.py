"""Create the HLOD layer consumed by the new map conversion."""

import unreal


def main():
    path = "/Game/ANANTA/City/HLOD"
    full = path + "/City_HLOD"
    layer = unreal.load_asset(full)
    if not layer:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        layer = tools.create_asset("City_HLOD", path, unreal.HLODLayer, unreal.HLODLayerFactory())
    # Gom mesh/vat lieu lap thanh instance, tranh bake lai tung ban sao cua ca thanh pho.
    layer.set_editor_property("layer_type", unreal.HLODLayerType.INSTANCING)
    layer.set_editor_property("cell_size", 25600)
    layer.set_editor_property("loading_range", 120000.0)
    layer.set_editor_property("is_spatially_loaded", True)
    builder = layer.get_editor_property("hlod_builder_settings")
    assert isinstance(builder, unreal.HLODBuilderInstancingSettings)
    builder.set_editor_property("disallow_nanite", False)
    builder.set_editor_property("instance_filtering_type", unreal.InstanceFilteringType.FILTER_NONE)
    assert unreal.EditorAssetLibrary.save_loaded_asset(layer)
    unreal.log("CITY_HLOD_LAYER_READY type=Instancing filtering=None nanite=Allowed")


if __name__ == "__main__":
    main()
