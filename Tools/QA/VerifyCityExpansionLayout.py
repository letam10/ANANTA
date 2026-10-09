"""Verify footprints and reserved player routes independently of Unreal assembly."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityExpansionLayout import generate
from CityExpansionData import VENUES, ROAD_LINES, overlaps_reserved


def main():
    data = generate()
    errors = []
    buildings = data["buildings"]
    for index, item in enumerate(buildings):
        x, y = item["centre"]
        width, depth = item["width"], item["depth"]
        if overlaps_reserved(x, y, width, depth):
            errors.append(f"Building overlaps reserved venue {index}")
        if min(abs(x - line) for line in ROAD_LINES) < width / 2 + 1350:
            errors.append(f"Building overlaps north-south street {index}")
        if min(abs(y - line) for line in ROAD_LINES) < depth / 2 + 1350:
            errors.append(f"Building overlaps east-west street {index}")
        for other in buildings[index + 1:]:
            xx, yy = other["centre"]
            if abs(xx - x) < (width + other["width"]) / 2 + 80:
                if abs(yy - y) < (depth + other["depth"]) / 2 + 80:
                    errors.append(f"Building footprints intersect {index}: {item['centre']} / {other['centre']}")
    assert len(buildings) > 1200, len(buildings)
    assert len(data["audit"]["styles"]) == 7
    assert abs(data["audit"]["areaRatio"] - 32) < 0.00001
    assert abs(data["audit"]["previousAreaRatio"] - 4) < 0.00001
    assert data["audit"]["roadBlocks"] == 3136
    assert len(VENUES) == 6
    # Kiem tra loai tai nguyen can import, khong chap nhan mesh khong co trong nguon.
    base = json.loads((ROOT / "Assets/City/manifest.json").read_text(encoding="utf-8"))
    known = {item["id"] for item in base["meshes"]} | {"Cube"}
    expansion_path = ROOT / "Assets/City/expansion_manifest.json"
    if expansion_path.exists():
        known.update(item["id"] for item in json.loads(expansion_path.read_text(encoding="utf-8"))["meshes"])
    mobility_path = ROOT / "Assets/City/mobility_manifest.json"
    if mobility_path.exists():
        known.update(item["id"] for item in json.loads(mobility_path.read_text(encoding="utf-8"))["meshes"])
    for path in (ROOT / "Assets/City").glob("*_manifest.json"):
        entries = json.loads(path.read_text(encoding="utf-8")).get("meshes", [])
        known.update(item["id"] for item in entries)
    pending_meshes = sorted({g["mesh"] for g in data["groups"]} - known)
    report = {**data["audit"], "errors": errors, "pendingAssetMeshes": pending_meshes,
              "newVenues": [v["id"] for v in VENUES], "inEngineVerified": False}
    out = ROOT / "Saved/QA/CityExpansionSourceAudit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    if errors:
        raise RuntimeError("Expanded city has footprint conflicts")


if __name__ == "__main__":
    main()
