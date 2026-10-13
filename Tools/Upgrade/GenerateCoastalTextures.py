"""Tileable metric PBR detail; normals derive from physical height gradients."""

import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "Assets" / "CoastalUpgrade" / "Textures"
SIZE = 1024


def save(name, albedo, height, roughness, span):
    dy, dx = np.gradient(height)
    nx = -dx * SIZE / span[0]
    ny = -dy * SIZE / span[1]
    normal = np.stack((nx, ny, np.ones_like(nx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    normal = np.clip((normal * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)
    color = np.clip(albedo * 255, 0, 255).astype(np.uint8)
    Image.fromarray(np.repeat(color[:, :, None], 3, axis=2)).save(OUTPUT / f"{name}_Color.png")
    Image.fromarray(normal).save(OUTPUT / f"{name}_Normal.png")
    Image.fromarray(np.clip(roughness * 255, 0, 255).astype(np.uint8)).save(OUTPUT / f"{name}_Rough.png")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    random = np.random.default_rng(17013)
    y, x = np.indices((SIZE, SIZE))
    grain = random.random((SIZE, SIZE))
    smooth = np.sin(x * np.pi * 2 / SIZE) * np.cos(y * np.pi * 6 / SIZE)
    manifest = {}
    for name in ("Concrete", "Brick", "Asphalt", "Tile", "Sand"):
        span = (2.4, 1.2) if name == "Brick" else (2.4, 2.4)
        albedo = 0.88 + grain * 0.1 + smooth * 0.015
        height = grain * 0.0003
        roughness = 0.84 + grain * 0.14
        if name == "Brick":
            row = y // (SIZE // 8)
            horizontal = (x + (row % 2) * (SIZE // 16)) % (SIZE // 8)
            # Mạch 1 cm được đổi sang pixel theo bề rộng ô 2,4 m.
            grout = (horizontal < round(0.01 / span[0] * SIZE)) | (y % (SIZE // 8) < 8)
            albedo[grout] = 0.52
            height += np.where(grout, 0, 0.004)
        elif name == "Tile":
            grout = (x % (SIZE // 4) < 4) | (y % (SIZE // 4) < 4)
            albedo[grout] = 0.62
            height += np.where(grout, 0, 0.002)
        elif name == "Asphalt":
            albedo = 0.74 + grain * 0.22
            height = grain * 0.0006
        elif name == "Sand":
            ripples = np.sin(y * np.pi * 32 / SIZE + smooth * 0.4)
            albedo += ripples * 0.045
            height += ripples * 0.001
        save(name, albedo, height, roughness, span)
        manifest[name] = {"tile_span_m": span, "size": SIZE,
                          "normal_source": "physical height gradient, metres"}
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("COASTAL_TEXTURES_OK 5 sets x color/normal/roughness at 1024 px")


if __name__ == "__main__":
    main()
