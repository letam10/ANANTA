"""Verify asset provenance and the city layout before expensive Unreal work."""

import hashlib
from collections import Counter
import json
from pathlib import Path
import sys


PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityLayout import generate, stage_groups, CAFE, APARTMENT, ROAD_HALF, WALK


def verify_assets():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["units"] == "cm", "Expected centimetres"
    assert manifest["upAxis"] == "Z", "Expected Z up"
    material_ids = {item["id"] for item in manifest["materials"]}
    ids = [item["id"] for item in manifest["meshes"]]
    assert len(ids) == len(set(ids)), "Duplicate mesh IDs"
    required = {"FacadeResidential", "FacadeCommercial", "FacadeTower", "Storefront", "Cornice",
                "Balcony", "RoofEquipment", "StreetLamp", "Bench", "Bollard", "Planter", "CarBody"}
    assert required <= set(ids), f"Missing kit IDs: {required - set(ids)}"
    for mesh in manifest["meshes"]:
        assert (source / mesh["file"]).is_file(), mesh["file"]
        assert mesh["triangles"] > 0, mesh["id"]
        assert set(mesh["materialSlots"]) <= material_ids, mesh["id"]
    checked_files = 0
    for item in manifest["sourceFiles"]:
        path = source / item["file"]
        assert path.is_file(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == item["sha256"], f"Source hash mismatch: {path}"
        checked_files += 1
    for material in manifest["materials"]:
        for role in ("baseColor", "normal", "roughness", "ao", "metallic"):
            if material.get(role):
                assert (source / material[role]).is_file(), material[role]
    return {"meshes": len(ids), "materials": len(material_ids), "sourceHashes": checked_files}


def verify_routes(layout):
    # Bao phu truc duong tu hinh hoc da sinh, ke ca moi giao lo va ranh gioi cell.
    roads = [item for group in layout["groups"] if group["material"] == "Asphalt"
             for item in group["instances"]]
    samples = 0
    for axis in (0, 1):
        for lane in layout["roadLines"]:
            for distance in range(-60000, 60001, 1000):
                point = [distance, lane] if axis == 0 else [lane, distance]
                covered = any(all(abs(point[i] - road["location"][i]) <= road["scale"][i] * 50
                                  for i in (0, 1)) for road in roads)
                assert covered, f"Disconnected road surface at {point}"
                samples += 1
    for building in layout["buildings"]:
        x, y = building["centre"]
        for road in layout["roadLines"]:
            assert abs(x - road) - building["width"] / 2 >= 900, f"Building blocks road: {building}"
            assert abs(y - road) - building["depth"] / 2 >= 900, f"Building blocks road: {building}"
    for room in (CAFE, APARTMENT):
        for axis in (0, 1):
            for road in layout["roadLines"]:
                clearance = abs(room["centre"][axis] - road) - room["size"][axis] / 2
                assert clearance >= ROAD_HALF + WALK, f"Room intrudes onto sidewalk: {room}"
    return {"roadSurfaceSamples": samples, "buildingRoadOverlaps": 0, "interiorSidewalkOverlaps": 0}


def verify_hero(layout):
    def counts(groups):
        return Counter(tuple(item["buildingCentre"]) for group in groups for item in group["instances"]
                       if "buildingCentre" in item)

    full = counts(layout["groups"])
    hero = counts(stage_groups(layout, "hero"))
    assert len(hero) > 10, "Hero selection lost buildings"
    for centre, count in hero.items():
        assert full[centre] == count, f"Sliced building in hero map: {centre}"
    return {"completeBuildings": len(hero), "partialBuildings": 0}


def main():
    layout = generate()
    result = {"layout": layout["audit"], "routes": verify_routes(layout), "hero": verify_hero(layout)}
    if "--layout-only" not in sys.argv:
        result["assets"] = verify_assets()
    path = PROJECT / "Saved/QA/CitySourceAudit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
