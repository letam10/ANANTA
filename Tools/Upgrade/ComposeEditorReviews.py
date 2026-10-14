"""Build five-angle sheets from editor-only captures and reject blank images."""

import json
import argparse
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat


root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--geometry", action="store_true")
arguments = parser.parse_args()
pointer = "latest-room-geometry.txt" if arguments.geometry else "latest-editor-views.txt"
folder = Path((root / "Saved/Upgrade" / pointer).read_text(encoding="utf-8"))
coverage = json.loads((folder / "coverage.json").read_text(encoding="utf-8"))
groups = defaultdict(list)
for view in coverage["views"]:
    groups[view["name"].rsplit("_", 1)[0]].append(view["name"])
for name, views in groups.items():
    assert len(views) == 5, (name, len(views))
    sheet = Image.new("RGB", (1920, 1152), (20, 25, 30))
    draw = ImageDraw.Draw(sheet)
    for index, view in enumerate(views):
        with Image.open(folder / f"{view}.png") as source:
            source = source.convert("RGB")
            assert max(ImageStat.Stat(source).stddev) > 3, f"Blank editor capture: {view}"
            left = (index % 2) * 960
            top = (index // 2) * 384
            sheet.paste(source.resize((960, 360)), (left, top + 24))
            draw.text((left + 8, top + 5), view, fill="white")
    sheet.save(folder / f"{name}_sheet.jpg", quality=90)
print(f"PLACEMENT_REVIEW_SHEETS_OK {len(groups)} rooms, {len(coverage['views'])} views; {coverage['mode']}")
if arguments.geometry:
    buildings = defaultdict(list)
    for name in groups:
        buildings[name.rsplit("_", 1)[0]].append(name)
    for building, rooms in buildings.items():
        sheet = Image.new("RGB", (1920, 240 * len(rooms)), (20, 25, 30))
        draw = ImageDraw.Draw(sheet)
        for row, room in enumerate(sorted(rooms)):
            for column, view in enumerate(groups[room]):
                with Image.open(folder / f"{view}.png") as source:
                    sheet.paste(source.convert("RGB").resize((384, 216)), (column * 384, row * 240 + 24))
                draw.text((column * 384 + 5, row * 240 + 5), view, fill="white")
        sheet.save(folder / f"{building}_all_rooms.jpg", quality=92)
