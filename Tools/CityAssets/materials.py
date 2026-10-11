"""Rebuild portable PBR materials from the documented channel manifest."""
import bpy
from geometry import MATERIALS

PALETTE = {
    "Dark": ((0.025, 0.035, 0.043, 1), 0.65, 0.34),
    "Aluminium": ((0.54, 0.58, 0.61, 1), 1, 0.27),
    "Brass": ((0.54, 0.34, 0.12, 1), 1, 0.28),
    "Glass": ((0.075, 0.15, 0.20, 1), 0.55, 0.14),
    "Teal": ((0.035, 0.17, 0.18, 1), 0, 0.40),
    "Light": ((0.84, 0.86, 0.75, 1), 0, 0.28),
    "Rubber": ((0.016, 0.018, 0.02, 1), 0, 0.83),
    "CarPaint": ((0.25, 0.41, 0.44, 1), 0.70, 0.22),
    "Red": ((0.45, 0.014, 0.017, 1), 0.15, 0.23),
    "Soil": ((0.065, 0.045, 0.027, 1), 0, 0.96),
    "Foliage": ((0.075, 0.19, 0.07, 1), 0, 0.77),
}
ALIASES = dict(Brick="brick_wall_001", Plaster="white_plaster_rough_01", Stone="stone_wall_02",
               Wood="oak_veneer_01", Linen="rough_linen", Floor="wood_floor", Denim="denim_fabric")


def build(catalog, root):
    for name, (color, metal, rough) in PALETTE.items():
        catalog.append(dict(id="City_" + name, baseColor=None, normal=None, roughness=None,
                            ao=None, metallic=None, normalConvention="OpenGL", baseColorFactor=color,
                            metallicFactor=metal, roughnessFactor=rough))
    for entry in catalog:
        mat = bpy.data.materials.new(entry["id"])
        mat.diffuse_color = entry["baseColorFactor"]
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = entry["baseColorFactor"]
        bsdf.inputs["Metallic"].default_value = entry.get("metallicFactor", 0)
        bsdf.inputs["Roughness"].default_value = entry.get("roughnessFactor", 0.65)
        for key, socket in [("baseColor", "Base Color"), ("roughness", "Roughness"), ("metallic", "Metallic")]:
            if entry.get(key):
                node = mat.node_tree.nodes.new("ShaderNodeTexImage")
                node.image = bpy.data.images.load(str(root / entry[key]), check_existing=True)
                node.image.colorspace_settings.name = "sRGB" if key == "baseColor" else "Non-Color"
                mat.node_tree.links.new(node.outputs["Color"], bsdf.inputs[socket])
        if entry.get("normal"):
            node = mat.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = bpy.data.images.load(str(root / entry["normal"]), check_existing=True)
            node.image.colorspace_settings.name = "Non-Color"
            normal = mat.node_tree.nodes.new("ShaderNodeNormalMap")
            mat.node_tree.links.new(node.outputs["Color"], normal.inputs["Color"])
            mat.node_tree.links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
        MATERIALS[entry["id"]] = mat
    for alias, source in ALIASES.items():
        MATERIALS[alias] = MATERIALS["City_" + source]
    for name in PALETTE:
        MATERIALS[name] = MATERIALS["City_" + name]
