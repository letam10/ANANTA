"""Cheap window occupancy shading without furnished rooms in shell buildings."""

from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import create_material, expression, ROOT, LIB, TOOLS


def main():
    path = ROOT + "/Materials/MPC_CityLighting"
    collection = unreal.load_asset(path)
    if not collection:
        collection = TOOLS.create_asset("MPC_CityLighting", ROOT + "/Materials",
                                        unreal.MaterialParameterCollection,
                                        unreal.MaterialParameterCollectionFactoryNew())
    parameters = list(collection.get_editor_property("scalar_parameters"))
    matches = [item for item in parameters if str(item.get_editor_property("parameter_name")) == "NightAmount"]
    assert len(matches) <= 1, "NightAmount must be unique"
    if matches:
        matches[0].set_editor_property("default_value", 0.0)
    else:
        parameter = unreal.CollectionScalarParameter()
        parameter.set_editor_property("parameter_name", "NightAmount")
        parameter.set_editor_property("default_value", 0.0)
        parameters.append(parameter)
    collection.set_editor_property("scalar_parameters", parameters)
    unreal.EditorAssetLibrary.save_loaded_asset(collection)
    create_material(dict(id="City_WindowGlass", baseColorFactor=[0.045, 0.085, 0.105],
                         metallicFactor=0.45, roughnessFactor=0.24), PROJECT / "Assets/City")
    material = unreal.load_asset(ROOT + "/Materials/M_City_WindowGlass")
    position = expression(material, unreal.MaterialExpressionWorldPosition, -750, -350)
    night = expression(material, unreal.MaterialExpressionCollectionParameter, -750, -150)
    night.set_editor_property("collection", collection)
    night.set_editor_property("parameter_name", "NightAmount")
    shader = expression(material, unreal.MaterialExpressionCustom, -350, -300)
    shader.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    shader.set_editor_property("description", "City occupied windows")
    inputs = []
    for name in ("WorldPos",):
        item = unreal.CustomInput()
        item.set_editor_property("input_name", name)
        inputs.append(item)
    shader.set_editor_property("inputs", inputs)
    shader.set_editor_property("code", """
float3 cell = floor(WorldPos / float3(190.0, 190.0, 320.0));
float seed = frac(sin(dot(cell, float3(12.9898, 78.233, 37.719))) * 43758.5453);
float occupied = step(0.68, seed);
float blinds = 0.65 + 0.35 * step(0.20, frac(WorldPos.z / 28.0));
float3 tint = lerp(float3(1.0, 0.52, 0.22), float3(0.55, 0.75, 1.0), step(0.94, seed));
return tint * occupied * blinds * 3.5;
""")
    assert LIB.connect_material_expressions(position, "", shader, "WorldPos")
    runtime = expression(material, unreal.MaterialExpressionMultiply, -100, -300)
    assert LIB.connect_material_expressions(shader, "", runtime, "A")
    assert LIB.connect_material_expressions(night, "", runtime, "B")
    # Bake giu cua so sang; nhanh Realtime van theo ngay/dem cua MPC.
    proxy = expression(material, unreal.MaterialExpressionMaterialProxyReplace, 150, -300)
    assert LIB.connect_material_expressions(runtime, "", proxy, "Realtime")
    assert LIB.connect_material_expressions(shader, "", proxy, "MaterialProxy")
    assert LIB.connect_material_property(proxy, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    LIB.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    targets = ("FacadeResidential", "FacadeCommercial", "FacadeTower", "FacadeBrickArch", "FacadeBay",
               "FacadeArtDeco", "FacadeIndustrial", "Storefront")
    changed = 0
    for identifier in targets:
        mesh = unreal.load_asset(f"{ROOT}/Meshes/SM_{identifier}")
        for index, slot in enumerate(mesh.get_editor_property("static_materials")):
            interface = slot.get_editor_property("material_interface")
            if interface and interface.get_name() in ("M_City_Glass", "M_City_WindowGlass"):
                mesh.set_material(index, material)
                changed += 1
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    assert changed == 8, changed
    unreal.log(f"CITY_WINDOW_LIGHTING_READY meshes={changed} defaultNight=0")


if __name__ == "__main__":
    main()
