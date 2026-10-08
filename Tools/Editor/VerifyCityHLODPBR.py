"""Independently inspect saved HLOD settings and material graphs without opening a map."""

import hashlib
import json
from pathlib import Path
import unreal

ROOT = "/Game/ANANTA/City"
LIB = unreal.MaterialEditingLibrary


def inputs(material, expression):
    names = LIB.get_material_expression_input_names(expression)
    nodes = LIB.get_inputs_for_material_expression(material, expression)
    assert len(names) == len(nodes)
    return {name.replace(" ", ""): value for name, value in zip(names, nodes)}


def require_type(node, cls):
    assert isinstance(node, cls), f"Expected {cls}, found {node}"
    return node


def check_night(node, collection):
    require_type(node, unreal.MaterialExpressionCollectionParameter)
    assert node.get_editor_property("collection") == collection
    assert str(node.get_editor_property("parameter_name")) == "NightAmount"


def parameters(material):
    result = {}
    for kind in ("scalar", "vector", "texture", "static_switch"):
        names = getattr(LIB, f"get_{kind}_parameter_names")(material)
        getter = getattr(LIB, f"get_material_default_{kind}_parameter_value")
        values = {}
        for name in names:
            value = getter(material, name)
            if kind == "texture":
                value = value.get_path_name() if value else None
            elif kind == "vector":
                value = [value.get_editor_property(channel) for channel in ("r", "g", "b", "a")]
            values[str(name)] = value
        result[kind] = values
    return result


def check_source(material, collection):
    assert not material.get_editor_property("use_material_attributes")
    proxy = LIB.get_material_property_input_node(material, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    require_type(proxy, unreal.MaterialExpressionMaterialProxyReplace)
    branches = inputs(material, proxy)
    runtime = require_type(branches["Realtime"], unreal.MaterialExpressionMultiply)
    lit = require_type(branches["MaterialProxy"], unreal.MaterialExpressionCustom)
    runtime_inputs = inputs(material, runtime)
    assert runtime_inputs["A"] == lit
    check_night(runtime_inputs["B"], collection)
    lit_inputs = inputs(material, lit)
    assert list(lit_inputs) == ["WorldPos"], lit_inputs
    require_type(lit_inputs["WorldPos"], unreal.MaterialExpressionWorldPosition)
    code = lit.get_editor_property("code")
    assert "Night" not in code and "occupied" in code and "* 3.5" in code
    return dict(proxy=proxy.get_name(), fullyLitBake=lit.get_name(), runtime=runtime.get_name())


def check_template(material, collection, original):
    assert material.get_editor_property("use_material_attributes")
    prop = unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES
    override = LIB.get_material_property_input_node(material, prop)
    require_type(override, unreal.MaterialExpressionMakeMaterialAttributes)
    pins = inputs(material, override)
    multiply = require_type(pins["EmissiveColor"], unreal.MaterialExpressionMultiply)
    values = inputs(material, multiply)
    check_night(values["B"], collection)
    extractor = require_type(values["A"], unreal.MaterialExpressionBreakMaterialAttributes)
    original_attributes = list(inputs(material, extractor).values())
    assert len(original_attributes) == 1 and original_attributes[0]
    assert LIB.get_input_node_output_name_for_material_expression(multiply, extractor) == "EmissiveColor"
    names = LIB.get_material_expression_input_names(override)
    output_names = LIB.get_material_expression_output_names(extractor)
    assert len(names) == len(output_names) == 27
    for name, output_name in zip(names, output_names):
        expected = multiply if output_name == "EmissiveColor" else extractor
        assert pins[name.replace(" ", "")] == expected, name
    original_root = LIB.get_material_property_input_node(original, prop)
    assert original_attributes[0].get_class() == original_root.get_class()
    saved_parameters = parameters(material)
    assert saved_parameters == parameters(original), "Flatten template parameters changed"
    return dict(activeAttributes=override.get_name(), originalAttributes=original_attributes[0].get_name(),
                emissiveMultiplier=multiply.get_name(), engineParametersPreserved=saved_parameters)


def main():
    project = Path(unreal.Paths.project_dir()).resolve()
    relative = ("HLOD/City_HLOD", "Materials/M_City_HLOD", "Materials/M_City_WindowGlass",
                "Materials/MPC_CityLighting")
    files = [project / f"Content/ANANTA/City/{name}.uasset" for name in relative]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    layer, template, source, collection = [unreal.load_asset(f"{ROOT}/{name}") for name in relative]
    assert all((layer, template, source, collection))
    assert layer.get_editor_property("layer_type") == unreal.HLODLayerType.MESH_SIMPLIFY
    assert layer.get_editor_property("cell_size") == 25600
    assert layer.get_editor_property("loading_range") == 120000.0
    builder = layer.get_editor_property("hlod_builder_settings")
    require_type(builder, unreal.HLODBuilderMeshSimplifySettings)
    assert builder.get_editor_property("hlod_material") == template
    proxy = builder.get_editor_property("mesh_simplify_settings")
    assert proxy.get_editor_property("calculate_correct_lod_model")
    assert not proxy.get_editor_property("group_identical_meshes_for_baking")
    settings = proxy.get_editor_property("material_settings")
    channels = {name: settings.get_editor_property(name)
                for name in ("normal_map", "emissive_map", "roughness_map", "metallic_map")}
    assert all(channels.values()), channels
    night = [item for item in collection.get_editor_property("scalar_parameters")
             if str(item.get_editor_property("parameter_name")) == "NightAmount"]
    assert len(night) == 1 and night[0].get_editor_property("default_value") == 0.0
    original = unreal.load_asset("/Engine/EngineMaterials/FlattenMaterial_VT")
    report = dict(channels=channels, template=template.get_path_name(), defaultNight=0.0,
                  correctLOD=True, identicalMeshGrouping=False,
                  sourceGraph=check_source(source, collection),
                  templateGraph=check_template(template, collection, original))
    after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    assert before == after, "Readback changed a saved package"
    report.update(packageHashes=after, packagesUnchanged=True, mapLoaded=False)
    destination = project / "Saved/QA/CityHLODPBRReadback.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_HLOD_PBR_READBACK_OK " + json.dumps(report))


if __name__ == "__main__":
    main()
