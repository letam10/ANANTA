"""Validate unchanged small-prop placements from persisted Unreal mesh/instance bounds."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CitySmallDetails import describe
from VerifyCityDistricts import Layout, catalogues, overlap

SUPPORTS = {
    "CookingPot": "SM_CafeCounter",
    "Saucepan": "SM_CafeCounter",
    "KitchenBowl": "SM_CafeCounter",
    "CoffeeMug": "SM_CafeTable",
    "MakeupCompact": "SM_House_modern_coffee_table_01",
    "ToyBlocks": "SM_CityCubeNanite",
    "RoomVase": "SM_CafeTable",
    "BathroomSoap": "SM_CityCubeNanite",
}

def supported(item, surface):
    return abs(item["min"][2] - surface["max"][2]) < .02 and all(
        surface["min"][axis] <= item["min"][axis] + .01
        and surface["max"][axis] >= item["max"][axis] - .01 for axis in (0, 1))

def main():
    path = ROOT / "Saved/QA/CitySmallNativeBounds.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["persistedMap"] and not data["changed"]
    meshes, materials = catalogues()
    source = Layout(meshes, materials)
    rows = []
    actors = data["actors"]
    for item in describe():
        source.add(item["mesh"], item["location"], item["scale"], item["yaw"], collision=False)
        expected = source.items[-1]
        matches = [actor for actor in actors if actor["label"] == item["label"]]
        assert len(matches) == 1, (item["label"], len(matches))
        actual = matches[0]
        assert actual["mesh"] == "SM_" + item["mesh"]
        assert actual["spatiallyLoaded"] and actual["collisionProfile"] == "NoCollision", actual
        assert actual["instance"] is None and len(actual["guid"]) == 32, actual
        bounds = actual["bounds"]
        difference = max(abs(bounds[key][axis] - expected[key][axis])
                         for key in ("min", "max") for axis in range(3))
        assert difference < .02, (item["mesh"], "source/native mismatch", difference)
        surfaces = [actor for actor in actors if actor["mesh"] == SUPPORTS[item["mesh"]]
                    and supported(bounds, actor["bounds"])]
        assert surfaces, (item["mesh"], "no native support")
        hits = [actor["label"] for actor in actors if actor is not actual and overlap(bounds, actor["bounds"])]
        assert not hits, (item["mesh"], "native bounds overlap", hits)
        rows.append(dict(id=item["mesh"], guid=actual["guid"], bounds=bounds,
                         sourceDifferenceCm=difference, nativeSupport=[a["label"] for a in surfaces],
                         overlaps=hits, autoHLOD=actual["autoHLOD"], hlodLayer=actual["hlodLayer"]))
    pot = next(actor for actor in actors if actor["label"] == "Living_Small_CookingPot")
    kettles = [actor for actor in actors if actor["mesh"] == "SM_House_vintage_electric_kettle"]
    gap = min(abs(actor["bounds"]["min"][0] - pot["bounds"]["max"][0]) for actor in kettles)
    result = dict(passed=True, completedUtc=data["completedUtc"], nativeSourceActors=data["sourceActors"],
                  testedProps=rows, nearestPotKettleXGapCm=gap, geometryChanged=False,
                  hlodRebuildRequired=False, visualAccepted=False,
                  scope="Persisted native AABB support/clearance/source parity; camera image review separate")
    output = ROOT / "Saved/QA/CitySmallNativePlacement.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"CITY_SMALL_NATIVE_PLACEMENT_OK props={len(rows)} pot_kettle_gap_cm={gap:.4f}")

if __name__ == "__main__":
    main()
