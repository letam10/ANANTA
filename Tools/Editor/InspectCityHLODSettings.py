"""Read the saved HLOD layer without loading the city or saving any package."""

import hashlib
import json
from pathlib import Path
import unreal


def main():
    project = Path(unreal.Paths.project_dir()).resolve()
    filename = project / "Content/ANANTA/City/HLOD/City_HLOD.uasset"
    before = hashlib.sha256(filename.read_bytes()).hexdigest()
    layer = unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD")
    assert layer
    builder = layer.get_editor_property("hlod_builder_settings")
    template = builder.get_editor_property("hlod_material")
    base = template
    while isinstance(base, unreal.MaterialInstance):
        base = base.get_editor_property("parent")
    emission = unreal.MaterialEditingLibrary.get_material_property_input_node(
        base, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    proxy = builder.get_editor_property("mesh_simplify_settings")
    fields = ("screen_size", "voxel_size", "override_voxel_size", "calculate_correct_lod_model",
              "merge_distance", "group_identical_meshes_for_baking", "reuse_mesh_lightmap_u_vs",
              "generate_lightmap_u_vs", "allow_distance_field", "support_ray_tracing")
    values = {name: proxy.get_editor_property(name) for name in fields}
    material = proxy.get_editor_property("material_settings")
    material_fields = ("normal_map", "emissive_map", "roughness_map", "metallic_map")
    materials = {name: material.get_editor_property(name) for name in material_fields}
    texture_size = material.get_editor_property("texture_size")
    materials["texture_size"] = [texture_size.x, texture_size.y]
    after = hashlib.sha256(filename.read_bytes()).hexdigest()
    assert after == before, "Inspection changed the saved HLOD layer"
    report = dict(layerType=str(layer.get_editor_property("layer_type")),
                  cellSize=layer.get_editor_property("cell_size"),
                  loadingRange=layer.get_editor_property("loading_range"),
                  builder=builder.get_class().get_name(), proxy=values, material=materials,
                  template=template.get_path_name(), baseMaterial=base.get_path_name(),
                  materialAttributes=base.get_editor_property("use_material_attributes"),
                  emissionNode=emission.get_class().get_name() if emission else None,
                  savedLayerSha256=after, packageUnchanged=True, mapLoaded=False)
    path = project / "Saved/QA/CityHLODSettings.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_HLOD_SETTINGS_READBACK_OK " + json.dumps(report))


if __name__ == "__main__":
    main()
