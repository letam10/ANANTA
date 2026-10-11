"""Portable metal rough materials; source attribution is kept verbatim."""
import hashlib
import json
import shutil

import bpy
import numpy as np
from geometry import MATERIALS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(name, color, rough=0.75, metal=0, **maps):
    item = dict(id=name, baseColor=None, normal=None, roughness=None, ao=None, metallic=None,
                baseColorFactor=color, metallicFactor=metal, roughnessFactor=rough,
                normalConvention="OpenGL")
    item.update(maps)
    return item


def texture_node(mat, base, path, color=False):
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(str(base / path), check_existing=True)
    node.image.colorspace_settings.name = "sRGB" if color else "Non-Color"
    return node


def build_materials(records, base):
    for item in records:
        mat = bpy.data.materials.get(item["id"]) or bpy.data.materials.new(item["id"])
        mat.diffuse_color = item["baseColorFactor"]
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = item["baseColorFactor"]
        bsdf.inputs["Metallic"].default_value = item["metallicFactor"]
        bsdf.inputs["Roughness"].default_value = item["roughnessFactor"]
        for key, socket in (("baseColor", "Base Color"), ("roughness", "Roughness")):
            if item[key]:
                node = texture_node(mat, base, item[key], key == "baseColor")
                mat.node_tree.links.new(node.outputs["Color"], bsdf.inputs[socket])
        if item["normal"]:
            node = texture_node(mat, base, item["normal"])
            normal = mat.node_tree.nodes.new("ShaderNodeNormalMap")
            mat.node_tree.links.new(node.outputs["Color"], normal.inputs["Color"])
            mat.node_tree.links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
        MATERIALS[item["id"]] = mat


def resample_sofa_normal(source, target):
    """Bake the source normal UV transform and strength into ordinary UV0 pixels."""
    image = bpy.data.images.load(str(source), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    width, height = image.size
    pixels = np.empty(width * height * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    pixels = pixels.reshape(height, width, 4)
    size = 2048
    v, u = np.mgrid[0:size, 0:size].astype(np.float32)
    u = (u + 0.5) / size
    v = 1 - (v + 0.5) / size
    c, s = np.cos(0.36), np.sin(0.36)
    tx = ((c * u - s * v) * 5) % 1
    ty = (1 - ((s * u + c * v) * 5) % 1) % 1
    sampled = pixels[(ty * height).astype(int) % height, (tx * width).astype(int) % width].copy()
    normal = sampled[:, :, :3] * 2 - 1
    normal[:, :, :2] *= 0.75
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    sampled[:, :, :3] = normal * 0.5 + 0.5
    sampled[:, :, 3] = 1
    result = bpy.data.images.new("Portable navy normal", size, size, alpha=False)
    result.colorspace_settings.name = "Non-Color"
    result.pixels.foreach_set(sampled.ravel())
    result.filepath_raw = str(target)
    result.file_format = "PNG"
    result.save()


def prepare(base, out):
    sources = []
    house = out / "Sources/HOUSE/GlamVelvetSofa"
    house.mkdir(parents=True, exist_ok=True)
    for path in sorted((__import__("pathlib").Path("D:/APP/HOUSE/assets/models/GlamVelvetSofa")).iterdir()):
        if path.is_file():
            dest = house / path.name
            shutil.copy2(path, dest)
            sources.append(dict(file=dest.relative_to(base).as_posix(), sha256=digest(dest),
                                source="GlamVelvetSofa by Eric Chadwick, Wayfair, LLC (2021)", license="CC-BY-4.0"))
    linen = out / "Textures/Linen"
    linen.mkdir(parents=True, exist_ok=True)
    catalog = json.loads((base / "source_catalog.json").read_text(encoding="utf-8"))
    for record in catalog["sourceFiles"]:
        if "textures/rough_linen/" in record["file"]:
            path = base / record["file"]
            dest = out / "Sources/rough_linen" / path.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            sources.append(dict(record, file=dest.relative_to(base).as_posix(), sha256=digest(dest)))
            shutil.copy2(base / "Textures/rough_linen" / path.name, linen / path.name)
    velvet = out / "Textures/Velvet"
    velvet.mkdir(parents=True, exist_ok=True)
    resample_sofa_normal(house / "GlamVelvetSofa_normal.png", velvet / "normal.png")
    shutil.copy2(house / "GlamVelvetSofa_occlusion.png", velvet / "ao.png")
    prefix = "Finishing/Textures/"
    maps = dict(baseColor=prefix + "Linen/color.jpg", normal=prefix + "Linen/normal.jpg",
                roughness=prefix + "Linen/roughness.jpg")
    records = [entry("Finish_VelvetNavy", (0.025, 0.07, 0.16, 1), 0.78,
                     normal=prefix + "Velvet/normal.png", ao=prefix + "Velvet/ao.png"),
               entry("Finish_SofaLegs", (0.02, 0.02, 0.02, 1), 0.4, ao=prefix + "Velvet/ao.png"),
               entry("Finish_SofaFeet", (1, 0.8, 0.7, 1), 0.4, 1, ao=prefix + "Velvet/ao.png"),
               entry("Finish_Woven", (1, 1, 1, 1), **maps),
               entry("Finish_Binding", (0.035, 0.12, 0.14, 1), 0.9, normal=maps["normal"]),
               entry("Finish_Linen", (1, 1, 1, 1), **maps, twoSided=True),
               entry("Finish_Hem", (0.57, 0.51, 0.40, 1), 0.9, normal=maps["normal"], twoSided=True),
               entry("Finish_Brass", (0.55, 0.35, 0.14, 1), 0.32, 1)]
    for path in sorted((out / "Textures").rglob("*")):
        if path.is_file():
            sources.append(dict(file=path.relative_to(base).as_posix(), sha256=digest(path),
                                source="Derived portable channel; raw source preserved in Sources",
                                license="CC-BY-4.0" if "Velvet" in str(path) else "CC0-1.0"))
    return records, sources
