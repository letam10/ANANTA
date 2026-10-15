"""Deterministic original PBR pixels: enamel, tread rubber, steel and seat cloth."""
import bpy
import numpy as np
from finishing_materials import entry, build_materials

PALETTE = [(0.83, .85, .84), (.95, .66, .05), (.04, .23, .54), (.68, .055, .045),
           (.028, .31, .30), (.90, .25, .038), (.08, .39, .17), (.035, .085, .17),
           (.76, .74, .61), (.38, .22, .10), (.17, .34, .07), (.095, .065, .032),
           (.90, .92, .83), (.85, .026, .018), (.96, .41, .025), (.03, .036, .042)]


def image(path, rgb, color):
    height, width, _ = rgb.shape
    pixels = np.ones((height, width, 4), dtype=np.float32)
    pixels[:, :, :3] = np.clip(rgb, 0, 1)
    data = bpy.data.images.new(path.stem, width, height, alpha=False)
    data.colorspace_settings.name = "sRGB" if color else "Non-Color"
    data.pixels.foreach_set(pixels.ravel())
    data.filepath_raw = str(path)
    data.file_format = "PNG"
    data.save()
    bpy.data.images.remove(data)


def prepare(base, out):
    directory = out / "Textures"
    directory.mkdir(parents=True, exist_ok=True)
    size = 1024
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    noise = np.random.default_rng(260108).normal(0, 1, (size, size)).astype(np.float32)
    grain = .45 * noise + .25 * np.sin(x * .11) * np.cos(y * .019)
    enamel = np.empty((size, size, 3), dtype=np.float32)
    for index, color in enumerate(PALETTE):
        row, col = index // 4, index % 4
        enamel[row * 256:(row + 1) * 256, col * 256:(col + 1) * 256] = color
    enamel *= 1 + grain[:, :, None] * .013
    grooves = (np.sin(x * .24 + np.sin(y * .013)) > .88).astype(np.float32)
    weave = (np.sin(x * 1.57) * np.sin(y * 1.57)) * .02
    specifications = {
        "Enamel": (enamel, .39 + grain * .018, grain * .002),
        "Rubber": (np.stack([.034 + grain * .005 - grooves * .008] * 3, axis=2),
                   .82 + grain * .025, grooves * .06 + noise * .006),
        "Steel": (np.stack([.57 + grain * .014] * 3, axis=2),
                  .30 + .065 * np.sin(y * 1.1) + grain * .015, np.sin(y * 1.1) * .007),
        "Upholstery": (np.stack([.08 + weave, .11 + weave, .13 + weave], axis=2),
                       .86 + grain * .035, weave * .24),
    }
    records = []
    for name, (color, rough, height) in specifications.items():
        dy, dx = np.gradient(height)
        normal = np.stack([-dx, -dy, np.ones_like(dx)], axis=2)
        normal /= np.linalg.norm(normal, axis=2, keepdims=True)
        normal = normal * .5 + .5
        maps = {}
        for role, pixels in (("baseColor", color), ("roughness", np.stack([rough] * 3, axis=2)),
                             ("normal", normal)):
            path = directory / f"{name}_{role}.png"
            image(path, pixels, role == "baseColor")
            maps[role] = path.relative_to(base).as_posix()
        records.append(entry("Mobility_" + name, (1, 1, 1, 1), .5,
                             1 if name == "Steel" else 0, **maps))
    records.append(entry("Mobility_Glass", (.13, .22, .27, 1), .12,
                         opacity=.23, twoSided=True))
    for record in records:
        record.update(source="Original deterministic ANANTA mobility surface authoring",
                      license="Original project asset")
    build_materials(records, base)
    for record in records:
        mat = bpy.data.materials[record["id"]]
        uv = mat.node_tree.nodes.new("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                mat.node_tree.links.new(uv.outputs["UV"], node.inputs["Vector"])
    glass = bpy.data.materials["Mobility_Glass"]
    bsdf = glass.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Alpha"].default_value = .23
    bsdf.inputs["Transmission Weight"].default_value = .35
    return records
