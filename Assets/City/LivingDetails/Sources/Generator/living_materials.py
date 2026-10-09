"""Original deterministic 1K PBR enamel, brushed metal, stone, rubber and linen."""
import numpy as np
import bpy
from finishing_materials import entry, build_materials
from mobility_materials import image

PALETTE = [( .78, .81, .81), (.77, .67, .47), (.045, .32, .29), (.64, .035, .025),
           (.025, .18, .55), (.90, .61, .035), (.82, .20, .025), (.027, .032, .04),
           (.28, .13, .052), (.055, .39, .12), (.026, .32, .43), (.9, .85, .57),
           (.64, .08, .22), (.30, .35, .38), (.025, .053, .10), (.35, .20, .075)]


def prepare(base, out):
    directory = out / "Textures"
    directory.mkdir(parents=True, exist_ok=True)
    y, x = np.mgrid[0:1024, 0:1024].astype(np.float32)
    rng = np.random.default_rng(20261008)
    noise = rng.normal(0, 1, (1024, 1024)).astype(np.float32)
    grain = noise * .4 + np.sin(x * .012) * np.cos(y * .015) * .4
    enamel = np.empty((1024, 1024, 3), dtype=np.float32)
    for index, color in enumerate(PALETTE):
        row, col = index // 4, index % 4
        enamel[row * 256:(row + 1) * 256, col * 256:(col + 1) * 256] = color
    enamel *= 1 + grain[:, :, None] * .018
    weave = np.sin(x * 1.57) * np.sin(y * 1.57)
    flecks = (noise > 1.1).astype(np.float32)
    materials = {
        "Enamel": (enamel, .38 + grain * .035, grain * .004),
        "Steel": (np.stack([.65 + noise * .012] * 3, axis=2),
                  .30 + np.sin(y * 1.1) * .012 + noise * .015, np.sin(y * 1.1) * .0018),
        "Dark": (np.stack([.034 + grain * .005] * 3, axis=2), .79 + grain * .04, grain * .008),
        "Stone": (np.stack([.23 + grain * .021 + flecks * .11] * 3, axis=2),
                  .71 + grain * .06, grain * .04 + flecks * .04),
        "Linen": (np.stack([.66 + weave * .025, .57 + weave * .025, .41 + weave * .025], axis=2),
                  .82 + weave * .04, weave * .028),
    }
    records = []
    for name, (color, rough, height) in materials.items():
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
        records.append(entry("Living_" + name, (1, 1, 1, 1), .5, 1 if name == "Steel" else 0, **maps))
    for record in records:
        record.update(source="Original deterministic ANANTA living surface authoring",
                      license="Original project asset")
    build_materials(records, base)
    for record in records:
        mat = bpy.data.materials[record["id"]]
        uv = mat.node_tree.nodes.new("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                mat.node_tree.links.new(uv.outputs["UV"], node.inputs["Vector"])
    return records
