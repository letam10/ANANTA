"""Check delivery metadata and compose labelled front and quarter review sheets."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Assets/City"
QA = ROOT / "Saved/QA/CityExpansionAssets"


def main():
    scripts = sorted((ROOT / "Tools/CityAssets").glob("expansion_*.py"))
    for path in scripts:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
        assert len(path.read_text(encoding="utf-8").splitlines()) < 300, path
    doc = json.loads((BASE / "expansion_manifest.json").read_text(encoding="utf-8"))
    roundtrip = json.loads((QA / "fbx_roundtrip.json").read_text(encoding="utf-8"))
    assert roundtrip["passed"] and len(roundtrip["meshes"]) == 11
    assert len(doc["meshes"]) == 11
    for entry in doc["meshes"]:
        assert hashlib.sha256((BASE / entry["file"]).read_bytes()).hexdigest() == entry["sha256"]
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    for view in ("front", "quarter"):
        sheet = Image.new("RGB", (1920, 2440), "#202830")
        draw = ImageDraw.Draw(sheet)
        for index, entry in enumerate(doc["meshes"]):
            x, y = index % 3 * 640, index // 3 * 610
            sheet.paste(Image.open(QA / (entry["id"] + "_" + view + ".png")).convert("RGB"), (x, y))
            label = entry["id"] + " | " + str(entry["triangles"]) + " tris"
            draw.text((x + 12, y + 566), label, font=font, fill="white")
        sheet.save(QA / ("review_" + view + ".jpg"), quality=95)
    result = dict(passed=True, meshes=11, sourceSyntaxChecked=len(scripts),
                  hashesVerified=True, fbxRoundtripPassed=True, reviewImages=22,
                  visualReview="Awaiting agent inspection of front and quarter sheets")
    (QA / "delivery_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
