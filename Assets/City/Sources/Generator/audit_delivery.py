"""Validate all manifest references, geometry reports and source hashes."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets/City"
QA = ROOT / "Saved/QA/CityAssets"
REQUIRED = {"FacadeResidential", "FacadeCommercial", "FacadeTower", "Storefront", "Cornice", "Balcony",
            "RoofEquipment", "StreetLamp", "Bench", "Bollard", "Planter", "CarBody", "CafeEntry", "ApartmentEntry"}


def main():
    doc = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    errors = []
    ids = {item["id"] for item in doc["meshes"]}
    assert REQUIRED <= ids
    assert len(ids) == len(doc["meshes"])
    assert (doc["schemaVersion"], doc["units"], doc["upAxis"]) == (1, "cm", "Z")
    material_ids = {entry["id"] for entry in doc["materials"]}
    geometry = json.loads((QA / "geometry_audit.json").read_text(encoding="utf-8"))
    measured = {entry["id"]: entry for entry in geometry["meshes"]}
    for item in doc["meshes"]:
        path = OUT / item["file"]
        assert path.is_file(), str(path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["id"]
        assert set(item["materialSlots"]) <= material_ids, item["id"]
        assert measured[item["id"]]["triangles"] == item["triangles"], item["id"]
        assert measured[item["id"]]["uvLayers"] > 0, item["id"]
        if measured[item["id"]]["zeroAreaFaces"]:
            errors.append(item["id"] + " has zero area faces")
        assert all(v > 0 and math.isfinite(v) for v in item["boundsCm"]["size"])
    for item in doc["materials"]:
        for channel in ["baseColor", "normal", "roughness", "ao", "metallic"]:
            if item[channel]:
                path = OUT / item[channel]
                assert path.is_file(), str(path)
                with Image.open(path) as image:
                    image.verify()
    for item in doc["sourceFiles"]:
        path = OUT / item["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], str(path)
        assert "GlamVelvetSofa/" not in item["file"]
    columns = 5
    width, height = 480, 456
    sheet = Image.new("RGB", (columns * width, math.ceil(len(doc["meshes"]) / columns) * height), "#202830")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    for index, item in enumerate(doc["meshes"]):
        x, y = index % columns * width, index // columns * height
        sheet.paste(Image.open(QA / (item["id"] + ".png")).convert("RGB"), (x, y))
        label = item["id"] + " | " + str(item["triangles"]) + " tris"
        draw.text((x + 12, y + 425), label, font=font, fill="white")
    sheet.save(QA / "contact_sheet.jpg", quality=95)
    result = dict(passed=not errors, meshes=len(ids), materials=len(material_ids),
                  sourceFiles=len(doc["sourceFiles"]), errors=errors, sourceHashesVerified=True,
                  texturesVerified=True, renderer="Cycles 24 samples", visualReview="pending human or agent inspection")
    (QA / "delivery_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    assert not errors, errors


if __name__ == "__main__":
    main()
