"""Validate native placement captures and collect five actual angles per placement."""

import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ["front", "rear", "left", "right", "upper"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("metro", "small", "facilities"), required=True)
    parser.add_argument("--diagnostic", choices=("None", "NaniteShadowAsyncOn"), default="None")
    parser.add_argument("--asset", choices=("All", "Rowboat"), default="All")
    args = parser.parse_args()
    scope = args.scope
    suffix = "" if args.asset == "All" else f"_{args.asset}"
    suffix += "" if args.diagnostic == "None" else f"_{args.diagnostic}"
    directory = ROOT / f"Saved/QA/CityPlacement_{scope}{suffix}"
    data = json.loads((directory / "Manifest.json").read_text(encoding="utf-8"))
    views = data["views"]
    assert len(views) == data["placements"] * 5
    for view in views:
        path = directory / view["image"]
        assert path.is_file(), path
        with Image.open(path) as image:
            assert image.size == (1920, 1080), (path, image.size)
    output = directory / "Contacts"
    output.mkdir(exist_ok=True)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 21) if font_path.is_file() else ImageFont.load_default()
    rows = []
    for index in range(data["placements"]):
        group = views[index * 5:index * 5 + 5]
        assert [view["direction"] for view in group] == DIRECTIONS, group
        assert len({view["id"] for view in group}) == 1
        sheet = Image.new("RGB", (2880, 1176), (21, 27, 39))
        draw = ImageDraw.Draw(sheet)
        for angle, view in enumerate(group):
            x = (angle % 3) * 960
            y = (angle // 3) * 588
            with Image.open(directory / view["image"]) as image:
                sheet.paste(image.convert("RGB").resize((960, 540), Image.Resampling.LANCZOS), (x, y))
            draw.text((x + 12, y + 548), f"{view['id']} | {view['direction']} | {view['image']}",
                      font=font, fill=(235, 239, 246))
        draw.text((1932, 660), f"Placement {index + 1} / {data['placements']}", font=font, fill="white")
        draw.text((1932, 705), "Five actual scene angles", font=font, fill="white")
        draw.text((1932, 750), "Originals: native 1920 x 1080", font=font, fill="white")
        draw.text((1932, 795), "Manual visual review pending", font=font, fill=(245, 191, 91))
        path = output / f"Placement_{index:02d}.png"
        sheet.save(path)
        with Image.open(path) as written:
            assert written.size == (2880, 1176)
        rows.append(dict(index=index, id=group[0]["id"], contact=str(path),
                         images=[view["image"] for view in group], visualAccepted=False))
    report = dict(scope=scope, diagnostic=args.diagnostic,
                  nativeCaptureCount=len(views), contacts=rows, visualAccepted=False)
    (output / "index.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"CITY_PLACEMENT_CONTACTS_OK scope={scope} captures={len(views)} contacts={len(rows)}")


if __name__ == "__main__":
    main()
