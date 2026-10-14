"""Owned material palette and inexpensive opaque ocean with animated normals."""

import unreal


ROOT = "/Game/ANANTA/CoastalUpgrade/Materials"
COLORS = {
    "Concrete": (0.48, 0.46, 0.41, 0.8),
    "Cream": (0.68, 0.62, 0.46, 0.75),
    "Terracotta": (0.36, 0.12, 0.075, 0.8),
    "Teal": (0.07, 0.26, 0.26, 0.65),
    "White": (0.78, 0.8, 0.75, 0.55),
    "Glass": (0.025, 0.09, 0.12, 0.13),
    "Road": (0.035, 0.042, 0.045, 0.85),
    "Sidewalk": (0.34, 0.35, 0.33, 0.9),
    "Wood": (0.25, 0.115, 0.045, 0.7),
    "Metal": (0.19, 0.22, 0.23, 0.35),
    "Sand": (0.57, 0.44, 0.24, 0.88),
    "Grass": (0.075, 0.15, 0.035, 0.9),
    "Blue": (0.025, 0.15, 0.4, 0.5),
    "Red": (0.43, 0.025, 0.035, 0.6),
    "Yellow": (0.82, 0.58, 0.045, 0.6),
    "Plaster": (0.74, 0.71, 0.65, 0.9),
    "WindowGlass": (0.36, 0.55, 0.62, 0.12),
}


def material(name):
    path = f"{ROOT}/M_{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path), False
    result = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        f"M_{name}", ROOT, unreal.Material, unreal.MaterialFactoryNew()
    )
    return result, True


def constant(mat, value, property_name, y=0):
    node = unreal.MaterialEditingLibrary.create_material_expression(
        mat, unreal.MaterialExpressionConstant, -200, y
    )
    node.r = value
    unreal.MaterialEditingLibrary.connect_material_property(node, "", property_name)


def palette():
    result = {}
    editing = unreal.MaterialEditingLibrary
    for name, rgba in COLORS.items():
        mat, created = material(name)
        if created:
            if name == "WindowGlass":
                mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
                constant(mat, 0.12, unreal.MaterialProperty.MP_OPACITY, 220)
            node = editing.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
            node.constant = unreal.LinearColor(*rgba[:3], 1)
            editing.connect_material_property(node, "", unreal.MaterialProperty.MP_BASE_COLOR)
            constant(mat, rgba[3], unreal.MaterialProperty.MP_ROUGHNESS)
            constant(mat, 0.55 if name == "Metal" else 0, unreal.MaterialProperty.MP_METALLIC, 120)
        editing.set_base_material_usage(mat, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
        editing.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        result[name] = mat
    return result


def ocean():
    mat, created = material("Ocean")
    if not created:
        unreal.MaterialEditingLibrary.set_base_material_usage(
            mat, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES
        )
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        return mat
    editing = unreal.MaterialEditingLibrary
    position = editing.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -800, 0)
    time = editing.create_material_expression(mat, unreal.MaterialExpressionTime, -800, 180)
    normal = editing.create_material_expression(mat, unreal.MaterialExpressionCustom, -450, 150)
    normal.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    normal.set_editor_property("code", "return normalize(float3(0.14*cos(P.x*0.004+T*0.9)"
                              "+0.06*cos((P.x+P.y)*0.012-T*1.5),"
                              "0.12*cos(P.y*0.005-T*0.6),1));")
    inputs = []
    for name in ("P", "T"):
        entry = unreal.CustomInput()
        entry.set_editor_property("input_name", name)
        inputs.append(entry)
    normal.set_editor_property("inputs", inputs)
    editing.connect_material_expressions(position, "", normal, "P")
    editing.connect_material_expressions(time, "", normal, "T")
    editing.connect_material_property(normal, "", unreal.MaterialProperty.MP_NORMAL)
    color = editing.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, -100)
    color.constant = unreal.LinearColor(0.012, 0.105, 0.14, 1)
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    constant(mat, 0.15, unreal.MaterialProperty.MP_ROUGHNESS, 250)
    constant(mat, 0.65, unreal.MaterialProperty.MP_SPECULAR, 350)
    editing.set_base_material_usage(mat, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
    editing.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
