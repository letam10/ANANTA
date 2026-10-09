"""Check support footprints and existing prop clearance using actual source mesh bounds."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityCivicDistrict import generate as civic
from CityLayout import APARTMENT
from CityLivingDetails import describe as living
from CitySmallDetails import describe
from CityVenueDressing import describe as dressing
from VerifyCityDistricts import Layout, catalogues, overlap


def footprint_on(item, surface):
    return abs(item["min"][2] - surface["max"][2]) < .02 and all(
        surface["min"][axis] <= item["min"][axis] + .01
        and surface["max"][axis] >= item["max"][axis] - .01 for axis in (0, 1))


def main():
    meshes, materials = catalogues()
    fixtures = Layout(meshes, materials)
    civic(fixtures)
    for item in dressing() + living():
        fixtures.add(item["mesh"], item["location"], item["scale"], item["yaw"],
                     item.get("material"), item["collision"])
    ax, ay = APARTMENT["centre"]
    fixtures.box("City_oak_veneer_01", (ax + 815, ay - 590, 93), (60, 90, 4))
    fixtures.box("City_oak_veneer_01", (ax, ay, 7.5), (*APARTMENT["size"], 15))
    surfaces = [item for item in fixtures.items if item["mesh"] in (
        "CafeCounter", "CafeTable", "House_modern_coffee_table_01", "Cube")]
    obstacles = [item for item in fixtures.items if item["mesh"] not in (
        "CafeCounter", "CafeTable", "House_modern_coffee_table_01", "Cube")]
    placed = Layout(meshes, materials)
    results = []
    for item in describe():
        placed.add(item["mesh"], item["location"], item["scale"], item["yaw"], collision=False)
        bounds = placed.items[-1]
        assert any(footprint_on(bounds, surface) for surface in surfaces), "Overhang: " + item["mesh"]
        hits = [obstacle["mesh"] for obstacle in obstacles if overlap(bounds, obstacle)]
        assert not hits, (item["mesh"], "intersects existing props", hits)
        assert not any(overlap(bounds, other) for other in placed.items[:-1]), "New props intersect"
        results.append(dict(id=item["mesh"], boundsMin=bounds["min"], boundsMax=bounds["max"], supported=True))
    # Ba toa do cu phai bi bat loi, tranh test chi doi chieu danh sach moi.
    from CityCivicDistrict import SITES
    _, bx, by, _, _ = next(site for site in SITES if site[0] == "Bar")
    bad = (("KitchenBowl", (bx + 3250, by + 1265, 120)),
           ("CoffeeMug", (bx + 3550, by - 1000, 92)),
           ("RoomVase", (ax - 530, ay - 425, 92)))
    for name, location in bad:
        regression = Layout(meshes, materials)
        regression.add(name, location, collision=False)
        assert not any(footprint_on(regression.items[0], surface) for surface in surfaces), name
    result = dict(passed=True, scope="Source AABB support and clearance; rendered placement pending",
                  props=results, overhangRegressionsRejected=len(bad), visualAccepted=False)
    output = ROOT / "Saved/QA/CitySmallPlacementSource.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("CITY_SMALL_PLACEMENT_SOURCE_OK", len(results), "regressions", len(bad))


if __name__ == "__main__":
    main()
