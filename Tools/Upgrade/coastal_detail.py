"""Rebuild owned facade/ground materials with metric color, roughness and normal maps."""

import json
from pathlib import Path

import unreal

from coastal_materials import COLORS


SOURCE = Path(unreal.Paths.project_dir()) / "Assets" / "CoastalUpgrade" / "Textures"
DEST = "/Game/ANANTA/CoastalUpgrade/Textures"
KINDS = {"Concrete": "Concrete", "Cream": "Concrete", "Terracotta": "Brick",
         "Teal": "Concrete", "White": "Concrete", "Road": "Asphalt",
         "Sidewalk": "Tile", "Sand": "Sand"}


def apply_texture_detail(palette):
    manifest = json.loads((SOURCE / "manifest.json").read_text())
    tasks = []
    for name in manifest:
        for kind in ("Color", "Normal", "Rough"):
            if unreal.EditorAssetLibrary.does_asset_exist(f"{DEST}/{name}_{kind}"):
                continue
            task = unreal.AssetImportTask()
            task.filename = str(SOURCE / f"{name}_{kind}.png")
            task.destination_path = DEST
            task.destination_name = f"{name}_{kind}"
            task.automated = True
            task.save = True
            tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for name in manifest:
        for kind in ("Color", "Normal", "Rough"):
            texture = unreal.load_asset(f"{DEST}/{name}_{kind}")
            texture.set_editor_property("srgb", kind == "Color")
            if kind == "Normal":
                texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            elif kind == "Rough":
                texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
            unreal.EditorAssetLibrary.save_loaded_asset(texture)
    editing = unreal.MaterialEditingLibrary
    for name, texture_kind in KINDS.items():
        mat = palette[name]
        editing.delete_all_material_expressions(mat)
        position = editing.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -1100, -50)
        normal_ws = editing.create_material_expression(mat, unreal.MaterialExpressionVertexNormalWS, -1100, 100)
        uv = editing.create_material_expression(mat, unreal.MaterialExpressionCustom, -900, 0)
        uv.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT2)
        span = manifest[texture_kind]["tile_span_m"]
        inputs = []
        for input_name in ("P", "N"):
            entry = unreal.CustomInput()
            entry.set_editor_property("input_name", input_name)
            inputs.append(entry)
        uv.set_editor_property("inputs", inputs)
        uv.set_editor_property("code", "float2 Q=abs(N.z)>0.5?P.xy:"
                               "float2(abs(N.x)>0.5?P.y:P.x,P.z);"
                               f"return Q/float2({span[0] * 100},{span[1] * 100});")
        editing.connect_material_expressions(position, "", uv, "P")
        editing.connect_material_expressions(normal_ws, "", uv, "N")
        nodes = {}
        for index, kind in enumerate(("Color", "Normal", "Rough")):
            sample = editing.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -600, index * 200)
            sample.set_editor_property("texture", unreal.load_asset(f"{DEST}/{texture_kind}_{kind}"))
            if kind == "Normal":
                sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            elif kind == "Rough":
                sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
            editing.connect_material_expressions(uv, "", sample, "Coordinates")
            nodes[kind] = sample
        tint = editing.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -550, -200)
        tint.constant = unreal.LinearColor(*COLORS[name][:3], 1)
        multiply = editing.create_material_expression(mat, unreal.MaterialExpressionMultiply, -250, 0)
        editing.connect_material_expressions(tint, "", multiply, "A")
        editing.connect_material_expressions(nodes["Color"], "RGB", multiply, "B")
        editing.connect_material_property(multiply, "", unreal.MaterialProperty.MP_BASE_COLOR)
        editing.connect_material_property(nodes["Normal"], "RGB", unreal.MaterialProperty.MP_NORMAL)
        editing.connect_material_property(nodes["Rough"], "R", unreal.MaterialProperty.MP_ROUGHNESS)
        editing.set_base_material_usage(mat, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
        editing.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    unreal.log("COASTAL_PBR_OK 8 facade/ground materials, 5 metric 1K PBR texture sets")
