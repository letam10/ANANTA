"""Copy the licensed HOUSE library without modifying its source files."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets/City"
HOUSE = Path("D:/APP/HOUSE")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def material(identifier):
    return dict(id=identifier, baseColor=None, normal=None, roughness=None,
                ao=None, metallic=None, normalConvention="OpenGL",
                baseColorFactor=[1, 1, 1, 1], metallicFactor=0, roughnessFactor=0.65)


def main():
    metadata = json.loads((HOUSE / "assets/manifest.json").read_text(encoding="utf-8"))
    source_files = []
    materials = []
    models = []
    for entry in metadata:
        if entry["license"] != "CC0-1.0" or entry["type"] == "hdris":
            continue
        src = HOUSE / "assets" / entry["type"] / entry["id"]
        dst = OUT / "Sources/HOUSE" / entry["type"] / entry["id"]
        shutil.copytree(src, dst, dirs_exist_ok=True)
        for path in sorted(dst.rglob("*")):
            if path.is_file():
                source_files.append(dict(file=path.relative_to(OUT).as_posix(), sha256=digest(path),
                                         source=entry["source"], license=entry["license"]))
        if entry["type"] == "textures":
            target = OUT / "Textures" / entry["id"]
            shutil.copytree(src, target, dirs_exist_ok=True)
            mat = material("City_" + entry["id"])
            for key, name in [("baseColor", "color.jpg"), ("normal", "normal.jpg"),
                              ("roughness", "roughness.jpg")]:
                mat[key] = (target / name).relative_to(OUT).as_posix()
            materials.append(mat)
            continue
        gltf_path = dst / (entry["id"] + ".gltf")
        doc = json.loads(gltf_path.read_text(encoding="utf-8"))
        slots = []
        for index, raw in enumerate(doc.get("materials", [])):
            identifier = "House_" + entry["id"] + "_" + str(index)
            slots.append(identifier)
            mat = material(identifier)
            pbr = raw.get("pbrMetallicRoughness", {})
            mat["baseColorFactor"] = pbr.get("baseColorFactor", [1, 1, 1, 1])
            mat["metallicFactor"] = pbr.get("metallicFactor", 1)
            mat["roughnessFactor"] = pbr.get("roughnessFactor", 1)
            mat["twoSided"] = raw.get("doubleSided", False)
            target = OUT / "Textures" / entry["id"]
            target.mkdir(parents=True, exist_ok=True)

            def image_path(info):
                tex = doc["textures"][info["index"]]
                return dst / doc["images"][tex["source"]]["uri"]

            for key, info in [("baseColor", pbr.get("baseColorTexture")),
                              ("normal", raw.get("normalTexture"))]:
                if info:
                    image_src = image_path(info)
                    dest = target / image_src.name
                    shutil.copy2(image_src, dest)
                    mat[key] = dest.relative_to(OUT).as_posix()
            # glTF metallic roughness: G la roughness, B la metallic, R la AO.
            for key, info, channel in [("roughness", pbr.get("metallicRoughnessTexture"), 1),
                                       ("metallic", pbr.get("metallicRoughnessTexture"), 2),
                                       ("ao", raw.get("occlusionTexture"), 0)]:
                if info:
                    dest = target / (identifier + "_" + key + ".png")
                    Image.open(image_path(info)).convert("RGB").getchannel(channel).save(dest)
                    mat[key] = dest.relative_to(OUT).as_posix()
            materials.append(mat)
        models.append(dict(id="House_" + entry["id"], sourceFile=gltf_path.relative_to(OUT).as_posix(),
                           source=entry["source"], license=entry["license"], slots=slots))
    source_manifest = OUT / "Sources/HOUSE/manifest.json"
    shutil.copy2(HOUSE / "assets/manifest.json", source_manifest)
    source_files.append(dict(file=source_manifest.relative_to(OUT).as_posix(), sha256=digest(source_manifest),
                             source="D:/APP/HOUSE/assets/manifest.json", license="metadata"))
    result = dict(models=models, materials=materials, sourceFiles=source_files)
    street_path = OUT / "street_catalog.json"
    if street_path.exists():
        street = json.loads(street_path.read_text(encoding="utf-8"))
        result["materials"].extend(street["materials"])
        result["sourceFiles"].extend(street["sourceFiles"])
    (OUT / "source_catalog.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(dict(models=len(models), materials=len(materials), sourceFiles=len(source_files))))


if __name__ == "__main__":
    main()
