"""Create deterministic, original Nova City texture maps with Pillow.

These are source art artifacts for the UE material pass.  They intentionally
use seeded noise and restrained colour variation so the imported materials do
not look like flat debug colours while remaining inexpensive on an RTX 3050.
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def noise_texture(size: tuple[int, int], seed: int, base: tuple[int, int, int], variation: int) -> Image.Image:
    rng = random.Random(seed)
    w, h = size
    pixels = []
    for y in range(h):
        for x in range(w):
            wave = int(5 * math.sin(x * 0.043) + 4 * math.sin(y * 0.037) + 3 * math.sin((x + y) * 0.019))
            grain = rng.randint(-variation, variation)
            pixels.append(tuple(max(0, min(255, c + wave + grain)) for c in base) + (255,))
    return Image.new("RGBA", size, (0, 0, 0, 0)) if not pixels else Image.frombytes("RGBA", size, bytes(v for p in pixels for v in p))


def facade(path: Path) -> None:
    # Mặt dựng phải giữ đủ giá trị sáng trong UE khi ánh sáng GI chưa được build.
    image = noise_texture((1024, 1024), 17, (78, 92, 108), 8)
    draw = ImageDraw.Draw(image)
    cell_w, cell_h = 128, 128
    for row in range(8):
        for col in range(8):
            left = col * cell_w + 22
            top = row * cell_h + 18
            glow = 35 + ((row * 13 + col * 19) % 80)
            if (row + col) % 7 == 0:
                colour = (184, 82, 51, 190)
            else:
                colour = (18, 106 + glow // 4, 145 + glow // 3, 210)
            draw.rounded_rectangle((left, top, left + 82, top + 86), radius=8, fill=colour, outline=(8, 16, 26, 255), width=8)
            draw.line((left + 8, top + 12, left + 72, top + 12), fill=(210, 240, 255, 90), width=3)
    for x in range(0, 1024, 256):
        draw.line((x, 0, x, 1024), fill=(8, 16, 25, 100), width=7)
    image = image.filter(ImageFilter.GaussianBlur(0.35))
    image.save(path, optimize=True)


def road(path: Path) -> None:
    image = noise_texture((1024, 1024), 31, (19, 24, 31), 11)
    draw = ImageDraw.Draw(image)
    for y in range(0, 1024, 128):
        draw.line((0, y, 1024, y), fill=(55, 62, 70, 70), width=2)
    for x in range(0, 1024, 256):
        draw.line((x, 0, x, 1024), fill=(8, 12, 18, 120), width=3)
    draw.line((510, 0, 510, 1024), fill=(222, 187, 60, 210), width=7)
    draw.line((530, 0, 530, 1024), fill=(222, 187, 60, 210), width=7)
    for y in range(40, 1024, 160):
        draw.rectangle((120, y, 245, y + 14), fill=(220, 226, 230, 170))
        draw.rectangle((780, y, 905, y + 14), fill=(220, 226, 230, 170))
    image = image.filter(ImageFilter.GaussianBlur(0.25))
    image.save(path, optimize=True)


def sidewalk(path: Path) -> None:
    image = noise_texture((512, 512), 53, (89, 96, 106), 9)
    draw = ImageDraw.Draw(image)
    for x in range(0, 512, 128):
        draw.line((x, 0, x, 512), fill=(40, 47, 57, 140), width=3)
    for y in range(0, 512, 128):
        draw.line((0, y, 512, y), fill=(40, 47, 57, 140), width=3)
    image.save(path, optimize=True)


def glass(path: Path) -> None:
    image = Image.new("RGBA", (512, 512), (8, 30, 52, 255))
    draw = ImageDraw.Draw(image)
    for row in range(8):
        for col in range(8):
            c = 80 + ((row * 31 + col * 13) % 110)
            draw.rectangle((col * 64 + 4, row * 64 + 4, col * 64 + 58, row * 64 + 58), fill=(12, c, min(255, c + 45), 255))
            draw.line((col * 64 + 10, row * 64 + 12, col * 64 + 50, row * 64 + 12), fill=(190, 235, 255, 160), width=3)
    image.save(path, optimize=True)


def grayscale_map(path: Path, size: tuple[int, int], seed: int, base: int, variation: int) -> None:
    """Create a deterministic linear grayscale PBR map."""
    rng = random.Random(seed)
    w, h = size
    pixels = bytearray()
    for y in range(h):
        for x in range(w):
            wave = int(7 * math.sin(x * 0.031) + 5 * math.sin(y * 0.047))
            value = max(0, min(255, base + wave + rng.randint(-variation, variation)))
            pixels.extend((value, value, value, 255))
    Image.frombytes("RGBA", size, bytes(pixels)).save(path, optimize=True)


def normal_map(path: Path, size: tuple[int, int], seed: int, strength: int = 24) -> None:
    """Build a tileable tangent-space normal map from seeded height noise."""
    rng = random.Random(seed)
    w, h = size
    heights = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            wave = int(9 * math.sin(x * 0.043) + 6 * math.sin(y * 0.037) + 4 * math.sin((x + y) * 0.019))
            heights[y][x] = max(0, min(255, 128 + wave + rng.randint(-10, 10)))
    pixels = bytearray()
    for y in range(h):
        for x in range(w):
            left = heights[y][(x - 1) % w]
            right = heights[y][(x + 1) % w]
            up = heights[(y - 1) % h][x]
            down = heights[(y + 1) % h][x]
            dx = (right - left) / 255.0 * strength
            dy = (down - up) / 255.0 * strength
            nx, ny, nz = -dx, -dy, 1.0
            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            pixels.extend((int((nx / length * 0.5 + 0.5) * 255),
                           int((ny / length * 0.5 + 0.5) * 255),
                           int((nz / length * 0.5 + 0.5) * 255), 255))
    Image.frombytes("RGBA", size, bytes(pixels)).save(path, optimize=True)


def pbr_maps(output_dir: Path) -> None:
    """Generate linear roughness/AO and tangent normal maps for authored materials."""
    normal_map(output_dir / "T_NovaFacade_Normal.png", (1024, 1024), 71, strength=18)
    grayscale_map(output_dir / "T_NovaFacade_Roughness.png", (1024, 1024), 73, 184, 16)
    grayscale_map(output_dir / "T_NovaFacade_AO.png", (1024, 1024), 79, 218, 18)
    normal_map(output_dir / "T_NovaRoad_Normal.png", (1024, 1024), 83, strength=12)
    grayscale_map(output_dir / "T_NovaRoad_Roughness.png", (1024, 1024), 89, 210, 14)
    grayscale_map(output_dir / "T_NovaRoad_AO.png", (1024, 1024), 97, 224, 12)
    normal_map(output_dir / "T_NovaSidewalk_Normal.png", (512, 512), 101, strength=14)
    grayscale_map(output_dir / "T_NovaSidewalk_Roughness.png", (512, 512), 103, 228, 10)
    grayscale_map(output_dir / "T_NovaSidewalk_AO.png", (512, 512), 107, 218, 14)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("Saved/Generated/NovaTextures"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    facade(args.output_dir / "T_NovaFacade_Albedo.png")
    road(args.output_dir / "T_NovaRoad_Albedo.png")
    sidewalk(args.output_dir / "T_NovaSidewalk_Albedo.png")
    glass(args.output_dir / "T_NovaGlass_Emissive.png")
    pbr_maps(args.output_dir)
    print("Generated Nova texture maps in", args.output_dir.resolve())


if __name__ == "__main__":
    main()
