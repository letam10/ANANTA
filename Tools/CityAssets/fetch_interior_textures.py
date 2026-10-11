"""Download two documented CC0 PBR finishes without modifying Unreal content."""

import hashlib
import json
from pathlib import Path
import urllib.request

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Assets/City"
SETS = (("terrazzo_tiles", "InteriorTerrazzo"),
        ("concrete_floor_painted", "InteriorWorkshopConcrete"))
CHANNELS = (("baseColor", "Diffuse"), ("normal", "nor_gl"),
            ("roughness", "Rough"), ("ao", "AO"))


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ANANTA-asset-pipeline"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main():
    result = dict(schemaVersion=1, materials=[], sourceFiles=[])
    audit = []
    license_url = "https://polyhaven.com/license"
    license_file = BASE / "Finishes/Sources/PolyHavenLicense.html"
    license_file.parent.mkdir(parents=True, exist_ok=True)
    license_file.write_bytes(get(license_url))
    assert b"CC0" in license_file.read_bytes(), "Source license page does not confirm CC0"
    result["sourceFiles"].append(dict(file=license_file.relative_to(BASE).as_posix(),
                                      source=license_url, license="License documentation",
                                      sha256=hashlib.sha256(license_file.read_bytes()).hexdigest()))
    for identifier, label in SETS:
        source = BASE / "Finishes/Sources" / identifier
        source.mkdir(parents=True, exist_ok=True)
        for endpoint in ("info", "files"):
            path = source / f"{endpoint}.json"
            path.write_bytes(get(f"https://api.polyhaven.com/{endpoint}/{identifier}"))
        info = json.loads((source / "info.json").read_bytes())
        files = json.loads((source / "files.json").read_bytes())
        # Kich thuoc Poly Haven la mm; shader toa do the gioi dung cm.
        dimensions = info["dimensions"]
        assert dimensions[0] == dimensions[1] and dimensions[0] > 0, dimensions
        material = dict(id=label, baseColorFactor=[1, 1, 1, 1], metallicFactor=0,
                        roughnessFactor=1, normalConvention="OpenGL",
                        worldTileCm=dimensions[0] / 10)
        for role, api_role in CHANNELS:
            entry = files[api_role]["2k"]["jpg"]
            path = source / f"{role}.jpg"
            if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest() != entry["md5"]:
                path.write_bytes(get(entry["url"]))
            assert hashlib.md5(path.read_bytes()).hexdigest() == entry["md5"], path
            with Image.open(path) as image:
                assert image.size == (2048, 2048), image.size
                image.verify()
            material[role] = path.relative_to(BASE).as_posix()
            audit.append(dict(material=label, channel=role, width=2048, height=2048,
                              md5=entry["md5"], url=entry["url"]))
        result["materials"].append(material)
        for path in sorted(source.iterdir()):
            result["sourceFiles"].append(dict(file=path.relative_to(BASE).as_posix(),
                                              sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                              source=f"https://polyhaven.com/a/{identifier}",
                                              authors=info["authors"], license="CC0-1.0"))
    target = BASE / "interior_finish_catalog.json"
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    report = dict(passed=True, materials=len(result["materials"]), images=audit,
                  unrealImported=False)
    report_path = ROOT / "Saved/QA/CityInteriorTextures.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"INTERIOR_TEXTURES_OK materials={len(result['materials'])} images={len(audit)}")


if __name__ == "__main__":
    main()
