"""Assemble actual CPU Cycles renders into one labelled image using Pillow."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "Saved/QA/CityLivingAssets"


def main():
    manifest = json.loads((ROOT / "Assets/City/living_manifest.json").read_text(encoding="utf-8"))
    sheet = Image.new("RGB", (1800, 4 * 445), (29, 33, 40))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 23)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    for i, record in enumerate(manifest["meshes"]):
        x, y = i % 3 * 600, i // 3 * 445
        with Image.open(QA / (record["id"] + "_threequarter.png")) as render:
            sheet.paste(render.convert("RGB"), (x, y))
        draw.text((x + 15, y + 405), record["id"], font=font, fill=(233, 235, 239))
        draw.text((x + 290, y + 409), str(record["triangles"]) + " triangles", font=small,
                  fill=(174, 185, 194))
    draw.text((1220, 1400), "Original living detail kit", font=font, fill=(233, 235, 239))
    draw.text((1220, 1440), "11 FBX / 5 materials / 15 shared 1K maps", font=small, fill=(174, 185, 194))
    draw.text((1220, 1470), "Cycles CPU / 16 samples / 2 threads", font=small, fill=(174, 185, 194))
    draw.text((1220, 1500), "Unreal visual acceptance pending", font=small, fill=(174, 185, 194))
    sheet.save(QA / "contactsheet.png")
    print(json.dumps(dict(status="PASS", contactSheet=str(QA / "contactsheet.png"))))


if __name__ == "__main__":
    main()
