"""Preserve FlattenMaterial_VT and modulate its active emissive attribute at runtime."""

import unreal

ROOT = "/Game/ANANTA/City/Materials"
TEMPLATE = "/Engine/EngineMaterials/FlattenMaterial_VT"
DESTINATION = ROOT + "/M_City_HLOD"
MARKER = "City HLOD night attributes"
LIB = unreal.MaterialEditingLibrary


def node(material, cls, x, y):
    return LIB.create_material_expression(material, cls, x, y)


def create_hlod_material():
    collection = unreal.load_asset(ROOT + "/MPC_CityLighting")
    assert collection, "Run CreateCityWindowLighting first"
    material = unreal.load_asset(DESTINATION)
    if not material:
        material = unreal.EditorAssetLibrary.duplicate_asset(TEMPLATE, DESTINATION)
    assert isinstance(material, unreal.Material)
    assert material.get_editor_property("use_material_attributes")
    prop = unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES
    attributes = LIB.get_material_property_input_node(material, prop)
    assert attributes, "FlattenMaterial_VT has no active material-attributes input"
    if attributes.get_editor_property("desc") == MARKER:
        return material
    output = LIB.get_material_property_input_node_output_name(material, prop)
    original_emissive = node(material, unreal.MaterialExpressionBreakMaterialAttributes, 400, -200)
    assert LIB.connect_material_expressions(attributes, output, original_emissive, "")
    night = node(material, unreal.MaterialExpressionCollectionParameter, 400, 200)
    night.set_editor_property("collection", collection)
    night.set_editor_property("parameter_name", "NightAmount")
    multiply = node(material, unreal.MaterialExpressionMultiply, 700, 0)
    assert LIB.connect_material_expressions(original_emissive, "EmissiveColor", multiply, "A")
    assert LIB.connect_material_expressions(night, "", multiply, "B")

    # Chi thay EmissiveColor; noi lai day du PBR, UV va cac thuoc tinh con lai.
    override = node(material, unreal.MaterialExpressionMakeMaterialAttributes, 950, 0)
    override.set_editor_property("desc", MARKER)
    names = LIB.get_material_expression_input_names(override)
    outputs = LIB.get_material_expression_output_names(original_emissive)
    # UE5.8 quy dinh Break/Make dung chung thu tu GetMaterialPropertyFromInputOutputIndex.
    assert len(names) == len(outputs) == 27, (names, outputs)
    for input_name, output_name in zip(names, outputs):
        if output_name == "EmissiveColor":
            assert LIB.connect_material_expressions(multiply, "", override, input_name)
        else:
            assert LIB.connect_material_expressions(original_emissive, output_name, override, input_name)
    assert LIB.connect_material_property(override, "", prop)
    LIB.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material
