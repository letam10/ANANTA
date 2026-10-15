"""Tiled ground detail and small animated water ripples without geometric displacement."""

from pathlib import Path
import sys
import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import create_material, expression, constant
from CityDistrictMaterials import definitions


def main():
    for item in definitions():
        if item["id"] in ("DistrictPaving", "DistrictSand", "DistrictWater", "DistrictTimber",
                          "DistrictPink", "DistrictFireBrick", "DistrictLimestone"):
            create_material(item, PROJECT / "Assets/City")
    material = unreal.load_asset("/Game/ANANTA/City/Materials/M_DistrictWater")
    library = unreal.MaterialEditingLibrary
    position = expression(material, unreal.MaterialExpressionWorldPosition, -1000, 300)
    time = expression(material, unreal.MaterialExpressionTime, -1000, 550)
    ripple = expression(material, unreal.MaterialExpressionCustom, -550, 400)
    ripple.set_editor_property("description", "Small world-space harbor ripples")
    ripple.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    inputs = []
    for name in ("P", "T"):
        item = unreal.CustomInput()
        item.set_editor_property("input_name", name)
        inputs.append(item)
    ripple.set_editor_property("inputs", inputs)
    ripple.set_editor_property("code", """
float2 q = P.xy + 170 * float2(sin(P.y * 0.0017 + T * 0.07), sin(P.x * 0.0013 - T * 0.08));
float a = dot(q, float2(0.023, 0.009)) + T * 1.1;
float b = dot(q, float2(-0.011, 0.031)) - T * 1.7;
float c = dot(q, float2(0.071, -0.053)) + T * 2.2;
float2 slope = float2(0.036, 0.014) * cos(a)
    + float2(-0.017, 0.045) * cos(b) + float2(0.012, -0.009) * cos(c);
return normalize(float3(-slope, 1));
""")
    assert library.connect_material_expressions(position, "", ripple, "P")
    assert library.connect_material_expressions(time, "", ripple, "T")
    assert library.connect_material_property(ripple, "", unreal.MaterialProperty.MP_NORMAL)
    constant(material, 0.3, unreal.MaterialProperty.MP_ROUGHNESS, 1500)
    library.recompile_material(material)
    assert unreal.EditorAssetLibrary.save_loaded_asset(material)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log("CITY_COASTAL_MATERIALS_OK groundTileCm=220 waterRippleNormal=1")


if __name__ == "__main__":
    main()
