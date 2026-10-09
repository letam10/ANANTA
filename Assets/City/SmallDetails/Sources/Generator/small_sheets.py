"""Label and assemble actual render frames without fabricating missing views."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "Saved/QA/CitySmallAssets"


def main():
    audit = json.loads((QA / "render_audit.json").read_text(encoding="utf-8"))
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 23)
    overview = Image.new("RGB", (1280, 800), (20, 24, 29))
    draw_overview = ImageDraw.Draw(overview)
    records = []
    for index, record in enumerate(audit["meshes"]):
        sheet = Image.new("RGB", (1920, 800), (20, 24, 29))
        draw = ImageDraw.Draw(sheet)
        assert len(record["renders"]) == 8
        for view, frame in enumerate(record["renders"]):
            path = Path(frame["file"])
            assert hashlib.sha256(path.read_bytes()).hexdigest() == frame["sha256"]
            image = Image.open(path).convert("RGB")
            assert image.size == (480, 360)
            x, y = (view % 4) * 480, (view // 4) * 400
            sheet.paste(image, (x, y + 40))
            draw.text((x + 12, y + 8), f"{record['id']} | yaw {frame['yaw']:03d}", font=font, fill="white")
        dest = QA / f"{record['id']}_contact.png"
        sheet.save(dest)
        records.append(dict(id=record["id"], file=str(dest), views=8))
        thumb = Image.open(record["renders"][1]["file"]).convert("RGB")
        thumb.thumbnail((320, 340))
        x, y = (index % 4) * 320, (index // 4) * 400
        overview.paste(thumb, (x, y + 60))
        draw_overview.text((x + 10, y + 15), record["id"], font=font, fill="white")
        draw_overview.text((x + 10, y + 315), f"{record['triangles']} triangles", font=font, fill="white")
    overview.save(QA / "overview.png")
    (QA / "contact_sheets.json").write_text(json.dumps(dict(status="PASS", sheets=records), indent=2))
    print(json.dumps(dict(status="PASS", contactSheets=len(records), actualViews=64)))


if __name__ == "__main__":
    main()
