"""Label actual orbit PNGs and verify source/mesh hashes after rendering."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Assets/City"
QA = ROOT / "Saved/QA/CityMetroAssets"


def main():
    manifest = json.loads((BASE / "metro_manifest.json").read_text(encoding="utf-8"))
    render = json.loads((QA / "render_audit.json").read_text(encoding="utf-8"))
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    assert len(manifest["meshes"]) == 5
    assert len(render["views"]) == 40
    expected = {(m["id"], yaw) for m in manifest["meshes"] for yaw in range(0, 360, 45)}
    assert {(v["id"], v["yaw"]) for v in render["views"]} == expected
    for view in render["views"]:
        assert hashlib.sha256((QA / view["file"]).read_bytes()).hexdigest() == view["sha256"]
    for record in manifest["meshes"] + manifest["sourceFiles"]:
        assert hashlib.sha256((BASE / record["file"]).read_bytes()).hexdigest() == record["sha256"]
    sheets = []
    for mesh in manifest["meshes"]:
        sheet = Image.new("RGB", (1600, 686), "#18222e")
        draw = ImageDraw.Draw(sheet)
        draw.text((18, 10), f'{mesh["id"]} | {mesh["triangles"]:,} triangles | actual Cycles views',
                  fill="white", font=font)
        for index, yaw in enumerate(range(0, 360, 45)):
            path = QA / f'{mesh["id"]}_{yaw:03}.png'
            source = Image.open(path).convert("RGB")
            assert source.size == (800, 600)
            source.thumbnail((400, 300))
            x = index % 4 * 400
            y = 45 + index // 4 * 320
            sheet.paste(source, (x, y))
            draw.text((x + 12, y + 294), f"yaw {yaw:03} degrees", fill="white", font=font)
        destination = QA / f'{mesh["id"]}_contact.png'
        sheet.save(destination)
        sheets.append(destination.name)
    (QA / "delivery_audit.json").write_text(json.dumps(dict(status="PASS", fbxCount=5,
        actualViewCount=40, contactSheets=sheets, allManifestHashesVerified=True, allRenderHashesVerified=True,
        runtime="Static models only; no gameplay or runtime performance acceptance"), indent=2))
    print("METRO_DELIVERY_PASS: 5 FBX, 40 actual views, 5 contact sheets; hashes verified")


if __name__ == "__main__":
    main()
