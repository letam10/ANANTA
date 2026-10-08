"""Original vector-like urban and botanical prints, rendered to portable PNGs."""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets/City/InteriorArchitecture/Textures"
SIZE = (1600, 1100)


def canvas():
    image = Image.new("RGB", SIZE, (225, 218, 198))
    return image, ImageDraw.Draw(image)


def grain(image, seed):
    rng = np.random.default_rng(seed)
    values = np.asarray(image).astype(np.int16)
    noise = rng.normal(0, 1.2, (*values.shape[:2], 1))
    return Image.fromarray(np.clip(values + noise, 0, 255).astype(np.uint8))


def title(draw, primary, secondary):
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    draw.line((95, 982, 1505, 982), fill=(117, 112, 97), width=2)
    draw.text((95, 1000), primary, fill=(61, 76, 71), font=font)
    draw.text((1140, 1008), secondary, fill=(87, 91, 78), font=small)


def gallery():
    image, draw = canvas()
    draw.ellipse((1030, 145, 1370, 485), fill=(182, 95, 61))
    draw.rectangle((150, 430, 690, 910), fill=(69, 101, 98))
    draw.pieslice((150, 160, 690, 700), 180, 360, fill=(69, 101, 98))
    draw.rectangle((290, 450, 550, 910), fill=(225, 218, 198))
    draw.pieslice((290, 320, 550, 580), 180, 360, fill=(225, 218, 198))
    draw.rectangle((740, 590, 1435, 910), fill=(130, 144, 118))
    for index in range(10):
        x = 770 + index * 64
        draw.rectangle((x, 620, x + 23, 900), fill=(205, 200, 171))
    draw.rectangle((90, 870, 1510, 915), fill=(189, 128, 79))
    draw.line((90, 925, 1510, 925), fill=(56, 74, 72), width=7)
    for offset in (0, 20, 40):
        draw.arc((780 + offset, 170 + offset, 1000 - offset, 550 - offset),
                 265, 95, fill=(169, 153, 111), width=7)
    title(draw, "URBAN STUDY / 01", "ANANTA   ORIGINAL SERIES")
    grain(image, 8).save(OUT / "GalleryOriginal.png")


def leaf(draw, start, tip, width, colour):
    sx, sy = start
    tx, ty = tip
    dx, dy = tx - sx, ty - sy
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    points = []
    for side in (-1, 1):
        indices = range(25) if side == -1 else range(24, -1, -1)
        for index in indices:
            t = index / 24
            bulge = math.sin(math.pi * t) * width * side
            points.append((sx + dx * t + nx * bulge, sy + dy * t + ny * bulge))
    draw.polygon(points, fill=colour)
    draw.line((start, tip), fill=(175, 184, 145), width=2)


def botanical():
    image, draw = canvas()
    draw.ellipse((870, 145, 1420, 695), fill=(203, 186, 151))
    draw.rounded_rectangle((270, 150, 820, 910), radius=250, fill=(214, 210, 183))
    for branch, shift in enumerate((0, 430)):
        base = (510 + shift, 900)
        top = (685 + shift, 225 + branch * 80)
        draw.line((base, top), fill=(83, 103, 75), width=8)
        for index in range(7):
            t = 0.15 + index * 0.11
            x = base[0] + (top[0] - base[0]) * t
            y = base[1] + (top[1] - base[1]) * t
            side = -1 if index % 2 == 0 else 1
            reach = 225 - index * 12
            colour = (61 + index * 5, 92 + index * 6, 70 + index * 4)
            leaf(draw, (x, y), (x + side * reach, y - 140), 48 - index * 2, colour)
    title(draw, "BOTANICAL STUDY / 02", "ANANTA   ORIGINAL SERIES")
    grain(image, 12).save(OUT / "BotanicalOriginal.png")


def portable_wood():
    target = OUT / "Oak"
    target.mkdir(exist_ok=True)
    for role in ("color", "normal", "roughness"):
        source = ROOT / f"Assets/City/Textures/wood_floor/{role}.jpg"
        image = Image.open(source).convert("RGB")
        assert max(image.size) <= 2048
        image.save(target / (role + ".png"))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    gallery()
    botanical()
    portable_wood()
    print("Original art PNGs created: 1600 x 1100")
