"""Fetch two CC0 street texture sets from the official Poly Haven API."""
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "Assets/City"


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ANANTA-local-asset-preparation"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def main():
    result = dict(materials=[], sourceFiles=[])
    for identifier, label in [("asphalt_02", "City_Asphalt"), ("concrete_floor_02", "City_Paving")]:
        src = OUT / "Sources/Street" / identifier
        dst = OUT / "Textures" / identifier
        src.mkdir(parents=True, exist_ok=True)
        dst.mkdir(parents=True, exist_ok=True)
        for endpoint in ["info", "files"]:
            url = "https://api.polyhaven.com/" + endpoint + "/" + identifier
            data = get(url)
            (src / (endpoint + ".json")).write_bytes(data)
        maps = json.loads((src / "files.json").read_text(encoding="utf-8"))
        material = dict(id=label, baseColor=None, normal=None, roughness=None, ao=None, metallic=None,
                        normalConvention="OpenGL", baseColorFactor=[1, 1, 1, 1], metallicFactor=0,
                        roughnessFactor=1)
        channels = [("baseColor", "Diffuse"), ("normal", "nor_gl"), ("roughness", "Rough"), ("ao", "AO")]
        for channel, api_key in channels:
            if api_key not in maps:
                continue
            item = maps[api_key]["2k"]["jpg"]
            path = src / (channel + ".jpg")
            if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest() != item["md5"]:
                path.write_bytes(get(item["url"]))
            assert hashlib.md5(path.read_bytes()).hexdigest() == item["md5"], item["url"]
            shutil.copy2(path, dst / path.name)
            material[channel] = (dst / path.name).relative_to(OUT).as_posix()
        result["materials"].append(material)
        for path in sorted(src.iterdir()):
            result["sourceFiles"].append(dict(file=path.relative_to(OUT).as_posix(),
                                               sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                               source="https://polyhaven.com/a/" + identifier,
                                               license="CC0-1.0"))
    (OUT / "street_catalog.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(dict(materials=len(result["materials"]), sourceFiles=len(result["sourceFiles"]))))


if __name__ == "__main__":
    main()
