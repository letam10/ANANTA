"""PBR graph creation; imported colour and data textures use explicit colour spaces."""

from pathlib import Path
import unreal


ROOT = "/Game/ANANTA/City"
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
LIB = unreal.MaterialEditingLibrary


def texture(source, asset_id, role, normal_convention="OpenGL"):
    destination = f"{ROOT}/Textures/{asset_id}_{role}"
    tex = unreal.load_asset(destination)
    if not tex:
        task = unreal.AssetImportTask()
        task.filename = str(source)
        task.destination_path = f"{ROOT}/Textures"
        task.destination_name = f"{asset_id}_{role}"
        task.automated = True
        task.save = True
        TOOLS.import_asset_tasks([task])
        tex = unreal.load_asset(destination)
    if not tex:
        raise RuntimeError(f"Texture import failed: {source}")
    tex.set_editor_property("srgb", role == "baseColor")
    tex.set_editor_property("max_texture_size", 2048)
    if role == "normal":
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property("flip_green_channel", normal_convention.lower() in ("opengl", "gl"))
    elif role != "baseColor":
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    unreal.EditorAssetLibrary.save_loaded_asset(tex)
    return tex


def expression(material, cls, x, y):
    return LIB.create_material_expression(material, cls, x, y)


def constant(material, value, output, y):
    if isinstance(value, (tuple, list)):
        node = expression(material, unreal.MaterialExpressionConstant3Vector, -300, y)
        node.set_editor_property("constant", unreal.LinearColor(*value[:3], 1))
    else:
        node = expression(material, unreal.MaterialExpressionConstant, -300, y)
        node.set_editor_property("r", float(value))
    if not LIB.connect_material_property(node, "", output):
        raise RuntimeError(f"Cannot connect constant {output}")


def world_uv(material, centimetres):
    pos = expression(material, unreal.MaterialExpressionWorldPosition, -1100, 0)
    mask = expression(material, unreal.MaterialExpressionComponentMask, -900, 0)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", True)
    mask.set_editor_property("b", False)
    scale = expression(material, unreal.MaterialExpressionDivide, -700, 0)
    scale.set_editor_property("const_b", centimetres)
    if not LIB.connect_material_expressions(pos, "", mask, ""):
        raise RuntimeError("World position did not connect to component mask")
    if not LIB.connect_material_expressions(mask, "", scale, "A"):
        raise RuntimeError("World position mask did not connect to UV scale")
    return scale


def create_material(item, source_root):
    name = item["id"]
    path = f"{ROOT}/Materials/M_{name}"
    material = unreal.load_asset(path)
    if not material:
        material = TOOLS.create_asset(f"M_{name}", f"{ROOT}/Materials", unreal.Material,
                                      unreal.MaterialFactoryNew())
    LIB.delete_all_material_expressions(material)
    material.set_editor_property("two_sided", item.get("twoSided", False))
    LIB.set_material_usage(material, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
    if "opacity" not in item:
        LIB.set_material_usage(material, unreal.MaterialUsage.MATUSAGE_NANITE)
    properties = {
        "baseColor": unreal.MaterialProperty.MP_BASE_COLOR,
        "normal": unreal.MaterialProperty.MP_NORMAL,
        "roughness": unreal.MaterialProperty.MP_ROUGHNESS,
        "ao": unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,
        "metallic": unreal.MaterialProperty.MP_METALLIC,
        "emissive": unreal.MaterialProperty.MP_EMISSIVE_COLOR,
    }
    uv = world_uv(material, item["worldTileCm"]) if item.get("worldTileCm") else None
    connected = []
    for index, (role, prop) in enumerate(properties.items()):
        filename = item.get(role)
        if not filename:
            continue
        source = source_root / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        tex = texture(source, item.get("textureSetId", name), role, item.get("normalConvention", "OpenGL"))
        node = expression(material, unreal.MaterialExpressionTextureSample, -450, index * 200)
        node.set_editor_property("texture", tex)
        if role == "normal":
            node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        elif role != "baseColor":
            node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
        if uv:
            if not LIB.connect_material_expressions(uv, "", node, "UVs"):
                raise RuntimeError(f"World UV did not connect: {name}.{role}")
        channel = "RGB" if role in ("baseColor", "normal", "emissive") else "R"
        output = node
        tint = item.get("baseColorFactor", [1, 1, 1])[:3]
        if role == "baseColor" and tint != [1, 1, 1]:
            output = expression(material, unreal.MaterialExpressionMultiply, -150, index * 200)
            colour = expression(material, unreal.MaterialExpressionConstant3Vector, -450, -200)
            colour.set_editor_property("constant", unreal.LinearColor(*tint, 1))
            assert LIB.connect_material_expressions(node, "RGB", output, "A")
            assert LIB.connect_material_expressions(colour, "", output, "B")
            channel = ""
        if not LIB.connect_material_property(output, channel, prop):
            raise RuntimeError(f"Material graph not connected: {name}.{role}")
        connected.append(role)
    defaults = {
        "baseColor": item.get("baseColorFactor", [0.4, 0.4, 0.4]),
        "roughness": item.get("roughnessFactor", 0.65),
        "metallic": item.get("metallicFactor", 0.0),
    }
    for index, (role, value) in enumerate(defaults.items()):
        if role not in connected:
            constant(material, value, properties[role], 1250 + index * 160)
    if item.get("emissiveFactor"):
        constant(material, item["emissiveFactor"], properties["emissive"], 1700)
    if "opacity" in item:
        material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        constant(material, item["opacity"], unreal.MaterialProperty.MP_OPACITY, 1850)
    LIB.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return {"id": name, "asset": path, "textureConnections": connected}


def street_materials(items):
    result = []
    search = {
        "Asphalt": ("asphalt", "road"),
        "Sidewalk": ("concrete", "plaster", "stone"),
        "Ground": ("concrete", "plaster", "stone"),
        "Curb": ("concrete", "plaster", "stone"),
    }
    colours = {"Asphalt": [0.07, 0.075, 0.085], "Sidewalk": [0.4, 0.42, 0.43],
               "Ground": [0.2, 0.22, 0.2], "Curb": [0.5, 0.51, 0.52]}
    for name, tokens in search.items():
        source = next((item for item in items if any(t in item["id"].lower() for t in tokens)), {})
        result.append({**source, "id": name, "worldTileCm": 400,
                       "baseColorFactor": colours[name]})
    result.extend([
        {**next(item for item in items if item["id"] == "City_white_plaster_rough_01"),
         "id": "InteriorPlaster", "baseColor": None, "baseColorFactor": [0.55, 0.51, 0.44]},
        {**next(item for item in items if item["id"] == "City_wood_floor"),
         "id": "InteriorFloor", "worldTileCm": 250},
        {"id": "InteriorGlass", "baseColorFactor": [0.35, 0.48, 0.48],
         "roughnessFactor": 0.12, "opacity": 0.12, "twoSided": True},
        {"id": "Concrete", "baseColorFactor": [0.32, 0.34, 0.35], "roughnessFactor": 0.82},
        {"id": "Roof", "baseColorFactor": [0.14, 0.17, 0.2], "roughnessFactor": 0.75},
        {"id": "RoadMark", "baseColorFactor": [0.78, 0.77, 0.68], "roughnessFactor": 0.8},
        {"id": "Anomaly", "baseColorFactor": [0.07, 0.16, 0.25],
         "emissiveFactor": [0.1, 2.1, 3.0], "metallicFactor": 0.4},
    ])
    return result
