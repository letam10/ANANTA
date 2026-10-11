"""Verify deterministic district profiles and facade variety without opening Unreal."""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDITOR = ROOT / "Tools" / "Editor"
sys.path.insert(0, str(EDITOR))

REQUIRED_DISTRICTS = {"west", "core", "east"}
REQUIRED_STYLES = {
    "FacadeResidential",
    "FacadeCommercial",
    "FacadeTower",
    "FacadeBrickArch",
    "FacadeBay",
    "FacadeArtDeco",
    "FacadeIndustrial",
    "FacadeCivic",
}
REQUIRED_FORMS = {
    "slab",
    "stepped",
    "corner",
    "terrace",
    "twin",
    "crown",
    "pavilion",
    "lantern",
}


def verify(payload):
    buildings = payload.get("buildings", [])
    district_counts = Counter(item.get("district") for item in buildings)
    style_counts = Counter(item.get("style") for item in buildings)
    form_counts = Counter(item.get("form") for item in buildings)
    errors = []
    if len(buildings) < 10000:
        errors.append("building count is unexpectedly low")
    if set(district_counts) != REQUIRED_DISTRICTS:
        errors.append("district profiles are incomplete")
    if set(style_counts) != REQUIRED_STYLES:
        errors.append("facade styles are incomplete")
    if set(form_counts) != REQUIRED_FORMS:
        errors.append("building forms are incomplete")
    if any(not item.get("quality") for item in buildings):
        errors.append("building quality metadata is missing")
    return {
        "status": "PASS" if not errors else "FAIL",
        "buildings": len(buildings),
        "districts": dict(sorted(district_counts.items())),
        "styles": dict(sorted(style_counts.items())),
        "forms": dict(sorted(form_counts.items())),
        "errors": errors,
    }


def main():
    from CityExpansionLayout import generate

    report = verify(generate())
    print(json.dumps(report, sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
