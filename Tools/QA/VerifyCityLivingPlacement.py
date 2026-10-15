"""Audit source hashes, world bounds, furniture overlaps and preserved clear paths."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityLayout import APARTMENT
from CityLivingDetails import REQUIRED, describe
import CityCivicDistrict as civic
from CityVenueDressing import describe as dressing
from VerifyCityDistricts import Layout, catalogues, overlap


def check_manifest():
    source = ROOT / "Assets/City"
    manifest = json.loads((source / "living_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1 and manifest["units"] == "cm"
    assert manifest["upAxis"] == "Z" and manifest["forwardAxis"] == "X"
    assert len(manifest["meshes"]) == len(REQUIRED)
    assert {item["id"] for item in manifest["meshes"]} == set(REQUIRED)
    files = manifest["meshes"] + manifest["sourceFiles"]
    for item in files:
        assert hashlib.sha256((source / item["file"]).read_bytes()).hexdigest() == item["sha256"], item["file"]
    for item in manifest["materials"]:
        for role in ("baseColor", "normal", "roughness"):
            assert (source / item[role]).is_file(), (item["id"], role)
    return len(files)


def volume(minimum, maximum):
    return dict(min=minimum, max=maximum)


def check_clear(items, minimum, maximum, label):
    hits = [item["label"] for item in items if overlap(item, volume(minimum, maximum))]
    assert not hits, f"Blocked {label}: {hits}"


def site_bounds(site):
    if site == "Apartment":
        x, y = APARTMENT["centre"]
        width, depth = APARTMENT["size"]
        return volume((x - width / 2 + 12.5, y - depth / 2 + 12.5, 15),
                      (x + width / 2 - 12.5, y + depth / 2 - 12.5, 327))
    index = next(i for i, entry in enumerate(civic.SITES) if entry[0] == site)
    left, bottom, right, top = civic.RESERVES[index]
    return volume((left, bottom, 0), (right, top, 496))


def check_paths(items, original):
    paths = []
    for name, minimum, maximum in civic.access_lanes():
        check_clear(items, minimum, maximum, name + " entry")
        paths.append(dict(site=name, widthCm=480))
    for name, x, y, _, _ in civic.SITES[:4]:
        for side in (-1, 1):
            check_clear(items, (x + 2950, y + side * 500 - 120, 16),
                        (x + 4150, y + side * 500 + 120, 240), name + " side aisle")
    x, y = APARTMENT["centre"]
    check_clear(items, (x - 1000, y - 120, 16), (x + 900, y + 120, 240), "apartment aisle")
    # Cua cu chi rong 140 cm: bao cao dung kich thuoc, khong gan nhan cua 240 cm.
    check_clear(items, (x - 1050, y - 70, 16), (x - 900, y + 70, 255), "apartment existing door")
    paths.append(dict(site="Apartment", interiorAisleCm=240, existingDoorCm=140))
    _, px, py, _, _ = civic.SITES[4]
    playground = volume((px + 1800, py - 120, 16), (px + 9600, py + 120, 240))
    check_clear(items, playground["min"], playground["max"], "playground main aisle")
    for item in items:
        if item["mesh"] not in ("PlaygroundSlide", "PlaygroundSwing"):
            continue
        # Dai 240 cm phia nam noi truc tiep toi loi giua san, ngoai khoang hoat dong thiet bi.
        minimum = (item["min"][0], item["min"][1] - 260, 16)
        maximum = (px + 9600, item["min"][1] - 20, 240)
        check_clear(items, minimum, maximum, item["label"] + " approach")
        assert not any(obstacle["collision"] and overlap(obstacle, volume(minimum, maximum))
                       for obstacle in original.items), item["label"] + " existing approach obstruction"
    paths.append(dict(site="AmusementPark", mainAisleCm=240, equipmentApproachCm=240))
    return paths


def check_sources():
    paths = [ROOT / "Tools/Editor" / (name + ".py")
             for name in ("ImportCityLiving", "CityLivingDetails", "ApplyCityLivingDetails")]
    for path in paths + [Path(__file__)]:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
        assert len(source.splitlines()) < 300, path
        assert all(len(line) <= 120 for line in source.splitlines()), path


def check_support(items, existing):
    supported_kinds = {"TableLamp", "Microwave", "Refrigerator", "FireExtinguisher",
                       "PlaygroundSlide", "PlaygroundSwing", "ArcadeCabinet"}
    for item in items:
        if item["mesh"] not in supported_kinds:
            continue
        supports = [support for support in existing.items
                    if abs(support["max"][2] - item["min"][2]) < 0.01
                    and all(support["min"][i] <= item["min"][i]
                            and support["max"][i] >= item["max"][i] for i in range(2))]
        assert supports, "Missing floor/table support: " + item["label"]


def main():
    checked_hashes = check_manifest()
    check_sources()
    meshes, materials = catalogues()
    materials.update({"Living_Steel"})
    layout = Layout(meshes, materials)
    placements = describe()
    assert len({item["label"] for item in placements}) == len(placements)
    assert all(item["label"].startswith("Living_") for item in placements)
    assert set(REQUIRED) <= {item["mesh"] for item in placements}
    for item in placements:
        layout.add(item["mesh"], item["location"], item["scale"], item["yaw"],
                   item["material"], item["collision"])
        bounds = layout.items[-1]
        bounds.update(label=item["label"], site=item["site"])
        site = site_bounds(item["site"])
        assert all(site["min"][i] <= bounds["min"][i] + 0.01
                   and bounds["max"][i] <= site["max"][i] + 0.01 for i in range(3)), item["label"]
    existing = Layout(meshes, materials)
    civic.generate(existing)
    for item in dressing():
        if item["label"].startswith("Dressing_Apartment_"):
            existing.add(item["mesh"], item["location"], item["scale"], item["yaw"],
                         collision=item["collision"])
    for item in layout.items:
        hits = [obstacle["mesh"] for obstacle in existing.items if overlap(item, obstacle)]
        assert not hits, f"Existing furniture overlap: {item['label']} {hits}"
    for index, item in enumerate(layout.items):
        for other in layout.items[index + 1:]:
            if "_Sink" in item["label"] and "_Sink" in other["label"]:
                continue
            assert not overlap(item, other), (item["label"], other["label"])
    check_support(layout.items, existing)
    paths = check_paths(layout.items, existing)
    report = dict(sourceGeometry="PASS", checkedHashes=checked_hashes, manifestCoverage=len(REQUIRED),
                  placementCount=len(placements), meshCounts=dict(Counter(item["mesh"] for item in placements)),
                  paths=paths, placements=layout.items, engineAccepted=False,
                  requiredEngineChecks=["import all meshes and reopen saved map", "actual simple collision bounds",
                                        "walk apartment and civic entrances", "GPU furnishing and support inspection"])
    output = ROOT / "Saved/QA/CityLivingAssets/placement-source.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"CITY_LIVING_PLACEMENT_PASS kinds={len(REQUIRED)} actors={len(placements)} hashes={checked_hashes}")


if __name__ == "__main__":
    main()
