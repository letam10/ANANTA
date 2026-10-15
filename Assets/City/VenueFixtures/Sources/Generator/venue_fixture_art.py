"""Original venue graphics, mapped directly from the eight authored room centres."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityVenueDressing import ROOMS

OUT = ROOT / "Assets/City/VenueFixtures"
FONT = "C:/Windows/Fonts/arial.ttf"
BOLD = "C:/Windows/Fonts/arialbd.ttf"
INK = (30, 58, 62)
PAPER = (232, 234, 220)
TEAL = (31, 101, 103)

def text(draw, xy, value, size, color=INK, bold=False, anchor=None):
    draw.text(xy, value, font=ImageFont.truetype(BOLD if bold else FONT, size),
              fill=color, anchor=anchor)

def guide():
    image = Image.new("RGB", (2048, 768), PAPER)
    draw = ImageDraw.Draw(image)
    text(draw, (65, 28), "NEIGHBORHOOD GUIDE", 79, bold=True)
    text(draw, (69, 124), "EASTLINE  /  CITY VENUES", 27)
    text(draw, (1980, 129), "NORTH +Y   /   EAST +X", 24, anchor="ra")
    draw.rounded_rectangle((62, 185, 1985, 490), 18, fill=(214, 222, 213))
    scale = .017
    origin = (790, 349)
    def pixel(centre):
        return [round(origin[0] + centre[0] * scale, 3), round(origin[1] - centre[1] * scale, 3)]
    # Cung ti le tren hai truc; cac diem chinh la tam phong that trong game.
    for x in range(-36000, 72001, 12000):
        px = pixel((x, 0))[0]
        if 75 < px < 1970:
            draw.line((px, 199, px, 477), fill=(238, 239, 228), width=17)
    draw.line((75, origin[1], 1970, origin[1]), fill=(238, 239, 228), width=21)
    names = {"Cafe": "CAFE", "Apartment": "APARTMENT", "Bookshop": "BOOKSHOP",
             "Clinic": "CLINIC", "Market": "MARKET", "Gallery": "GALLERY",
             "Workshop": "WORKSHOP", "Transit": "VISITOR CENTRE"}
    entries = []
    for index, room in enumerate(ROOMS, 1):
        px, py = pixel(room["centre"])
        color = (174, 84, 42) if room["id"] == "Transit" else TEAL
        draw.ellipse((px - 23, py - 23, px + 23, py + 23), fill=color, outline=PAPER, width=3)
        text(draw, (px, py), str(index), 29, PAPER, True, "mm")
        col, row = (index - 1) % 4, (index - 1) // 4
        lx, ly = 82 + col * 487, 548 + row * 108
        draw.ellipse((lx, ly, lx + 46, ly + 46), fill=color)
        text(draw, (lx + 23, ly + 23), str(index), 27, PAPER, True, "mm")
        text(draw, (lx + 61, ly + 1), names[room["id"]], 31, bold=True)
        cx, cy = room["centre"]
        text(draw, (lx + 61, ly + 40), f"X {cx / 100:g} m   Y {cy / 100:g} m", 22)
        entries.append(dict(number=index, id=room["id"], centreCm=list(room["centre"]),
                            markerPixel=[px, py], legend=names[room["id"]]))
    text(draw, (88, 457), "VENUE LOCATIONS  /  100 m", 19)
    draw.line((391, 467, 561, 467), fill=INK, width=4)
    for px in (391, 561):
        draw.line((px, 460, px, 474), fill=INK, width=3)
    text(draw, (1955, 454), "8  YOU ARE HERE", 22, (174, 84, 42), True, "ra")
    image.save(OUT / "Textures/NeighborhoodGuide.png")
    metadata = dict(title="NEIGHBORHOOD GUIDE", source="Tools/Editor/CityVenueDressing.py ROOMS",
                    convention="X east/right, Y north/up; uniform scale, centimetres",
                    imageSize=[2048, 768], pixelsPerCm=scale, originPixel=origin, venues=entries)
    (OUT / "Sources/GuideCoordinates.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

def labels():
    image = Image.new("RGB", (1024, 1024), PAPER)
    sections = [("CLINIC / SUPPLY STORAGE", "CONTROLLED STOCK  /  STAFF ACCESS"),
                ("01  DRESSINGS", "GAUZE  /  BANDAGES  /  TAPE"),
                ("02  HYGIENE", "GLOVES  /  MASKS  /  WIPES"),
                ("03  EQUIPMENT", "INSTRUMENTS  /  REUSABLE KITS")]
    for row, (title, subtitle) in enumerate(sections):
        panel = Image.new("RGB", (1024, 256), PAPER)
        draw = ImageDraw.Draw(panel)
        draw.rectangle((12, 12, 1011, 243), outline=TEAL, width=5)
        draw.rectangle((31, 35, 44, 220), fill=TEAL)
        text(draw, (73, 48), title, 55 if row else 53, bold=True)
        draw.line((74, 133, 956, 133), fill=TEAL, width=3)
        text(draw, (75, 165), subtitle, 32)
        image.paste(panel, (0, row * 256))
    header = Image.new("RGB", (1024, 55), PAPER)
    head_draw = ImageDraw.Draw(header)
    head_draw.rectangle((3, 3, 1020, 51), outline=TEAL, width=2)
    text(head_draw, (512, 27), "CLINIC / SUPPLY STORAGE", 43, bold=True, anchor="mm")
    image.paste(header.resize((1024, 256), Image.Resampling.LANCZOS), (0, 0))
    image.save(OUT / "Textures/SupplyLabels.png")

def main():
    (OUT / "Textures").mkdir(parents=True, exist_ok=True)
    (OUT / "Sources").mkdir(exist_ok=True)
    guide()
    labels()
    print("PASS original guide art and eight coordinate records")

if __name__ == "__main__":
    main()
