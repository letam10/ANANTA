"""Source geometry audit; imported collision and rendered art still need engine checks."""

from collections import Counter
import ast
import json
import math
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
import CityCivicDistrict as civic
import CityCoastalDistrict as coast
import CityDistrictMaterials as finishes
from CityAssetOrientation import imported_yaw


def catalogues():
    meshes = {"Cube": dict(boundsCm=dict(min=[-50] * 3, max=[50] * 3))}
    materials = set(finishes.MATERIAL_IDS) | {"InteriorGlass", "RoadMark"}
    for path in (ROOT / "Assets/City").glob("*manifest.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        meshes.update({item["id"]: item for item in document.get("meshes", [])})
        materials.update(item["id"] for item in document.get("materials", []))
    return meshes, materials


class Layout:
    def __init__(self, meshes, materials):
        self.meshes = meshes
        self.materials = materials
        self.items = []

    def add(self, mesh, location, scale=(1, 1, 1), yaw=0, material=None, collision=True):
        assert mesh in self.meshes, f"Missing mesh reference: {mesh}"
        assert material is None or material in self.materials, f"Missing material reference: {material}"
        bounds = self.meshes[mesh]["boundsCm"]
        angle = math.radians(imported_yaw(mesh, yaw))
        corners = []
        for x in (bounds["min"][0], bounds["max"][0]):
            for y in (bounds["min"][1], bounds["max"][1]):
                for z in (bounds["min"][2], bounds["max"][2]):
                    xx, yy = x * scale[0], y * scale[1] * (-1 if mesh != "Cube" else 1)
                    corners.append((location[0] + xx * math.cos(angle) - yy * math.sin(angle),
                                    location[1] + xx * math.sin(angle) + yy * math.cos(angle),
                                    location[2] + z * scale[2]))
        minimum = tuple(min(corner[i] for corner in corners) for i in range(3))
        maximum = tuple(max(corner[i] for corner in corners) for i in range(3))
        self.items.append(dict(mesh=mesh, material=material, collision=collision, min=minimum, max=maximum))

    def box(self, material, location, size, collision=True):
        self.add("Cube", location, tuple(value / 100 for value in size), material=material, collision=collision)


def overlap(a, b):
    return all(a["min"][i] < b["max"][i] - 0.001 and a["max"][i] > b["min"][i] + 0.001
               for i in range(3))


def clear(layout, minimum, maximum, label):
    volume = dict(min=minimum, max=maximum)
    hits = [item for item in layout.items if item["collision"] and overlap(item, volume)]
    assert not hits, f"Blocked {label}: {hits[:2]}"


def supported(layout, x, y):
    return any(item["collision"] and item["mesh"] == "Cube" and 14 <= item["max"][2] <= 15
               and item["min"][0] <= x <= item["max"][0] and item["min"][1] <= y <= item["max"][1]
               for item in layout.items)


def check_reserves(layout, reserves):
    for item in layout.items:
        assert any(item["min"][0] >= left - 0.01 and item["max"][0] <= right + 0.01
                   and item["min"][1] >= bottom - 0.01 and item["max"][1] <= top + 0.01
                   for left, bottom, right, top in reserves), f"Outside reserve: {item}"
    for left, bottom, right, top in reserves:
        assert min(left, bottom) >= -170000 and max(right, top) <= 170000


def check_civic(layout):
    for name, minimum, maximum in civic.access_lanes():
        clear(layout, minimum, maximum, name + " 480 cm main corridor")
        for x in range(int(minimum[0]), int(maximum[0]), 100):
            assert supported(layout, x, (minimum[1] + maximum[1]) / 2), name + " floor gap"
    for name, x, y, _, _ in civic.SITES[:4]:
        floors = [item for item in layout.items if item["mesh"] == "Cube"
                  and item["min"][0] < x + 3500 < item["max"][0]
                  and item["min"][1] < y < item["max"][1] and item["max"][2] <= 15]
        tops = sorted(item["max"][2] for item in floors)
        assert len(tops) == 2 and tops[1] - tops[0] >= 1, name + " coplanar floor layers"
        for side in (-1, 1):
            clear(layout, (x + 2950, y + side * 500 - 120, 16),
                  (x + 4150, y + side * 500 + 120, 230), name + " 240 cm side corridor")
    assert len(civic.SERVICES) == 4
    assert all(right - left <= 9000 and top - bottom <= 9000 for left, bottom, right, top in civic.RESERVES)


def check_coast(layout, meshes):
    water = [item for item in layout.items if item["material"] == "DistrictWater"]
    assert len(water) == 1 and not water[0]["collision"]
    assert water[0]["max"][2] == coast.WATER_LEVEL
    result = []
    for dock in coast.piers():
        name, x, half_width = dock["id"], dock["x"], dock["halfWidth"]
        assert name in meshes
        bounds = meshes[name]["boundsCm"]
        assert abs(half_width - bounds["size"][1] / 2) < 0.001
        half_length = bounds["size"][0] / 2
        clear(layout, (x - half_width, coast.DOCK_Y - half_length, coast.WATER_LEVEL + bounds["min"][2]),
              (x + half_width, -134000 + half_length, coast.WATER_LEVEL + bounds["max"][2]),
              name + " dock and north departure")
        for key in ("doorX", "sidewalkX"):
            assert supported(layout, dock[key], coast.DOCK_Y), name + " unsupported " + key
        clear(layout, (dock["sidewalkX"] - 32, coast.DOCK_Y - 32, 18),
              (dock["doorX"] + 32, coast.DOCK_Y + 32, 202), name + " boarding capsule sweep")
        clear(layout, (dock["centre"] - 120, coast.QUAY_Y + 30, 16),
              (dock["centre"] + 120, coast.DOCK_Y, 230), name + " 240 cm pier walk")
        result.append(dict(id=name, halfWidth=half_width, hullGapCm=20, doorX=dock["doorX"],
                           sidewalkX=dock["sidewalkX"], deckZ=15, pierClearWidth=240))
    return result


def integration_issues(layout, meshes):
    issues = []
    path = ROOT / "Source/ANANTA/Private/City/CityServiceState.cpp"
    source = path.read_text(encoding="utf-8")
    missing = [name + "_Read" for name, _ in civic.SERVICES if 'TEXT("' + name + '_Read")' not in source]
    if missing:
        issues.append(dict(kind="service-registration", ids=missing))
    path = ROOT / "Source/ANANTA/Private/City/Mobility/CityMobilityData.cpp"
    source = path.read_text(encoding="utf-8")
    old_return = re.search(r"FVector\(X\s*\+\s*4200,\s*-141000,\s*WaterLevel\)", source)
    if old_return:
        counts = {}
        for name, x, _ in coast.DOCKS:
            half_length = meshes[name]["boundsCm"]["size"][0] / 2
            half_width = meshes[name]["boundsCm"]["size"][1] / 2
            volume = dict(min=(x - half_length, coast.DOCK_Y - half_width, -100),
                          max=(x + 4200 + half_length, coast.DOCK_Y + half_width, 250))
            counts[name] = sum(item["collision"] and overlap(item, volume) for item in layout.items)
        issues.append(dict(kind="runtime-return-crosses-piers", collisionCounts=counts,
                           required="Return facing north; never turn or travel west across piers at dock Y."))
    return issues


def check_sources():
    paths = [ROOT / "Tools/Editor" / (name + ".py")
             for name in ("CityCivicDistrict", "CityCoastalDistrict", "CityDistrictMaterials")]
    paths.append(Path(__file__))
    for path in paths:
        source = path.read_text(encoding="utf-8")
        ast.parse(source)
        compile(source, str(path), "exec")
        lines = source.splitlines()
        assert len(lines) < 300, f"Too many lines: {path}"
        assert all(len(line) <= 120 for line in lines), f"Long line: {path}"
    for item in finishes.definitions():
        for role in ("baseColor", "normal", "roughness", "ao"):
            if item.get(role):
                assert (ROOT / "Assets/City" / item[role]).is_file(), item["id"] + " missing texture " + role
    assert all(item.get("normal") and item.get("roughness") for item in finishes.definitions()[:11])


def main():
    meshes, materials = catalogues()
    city = Layout(meshes, materials)
    harbour = Layout(meshes, materials)
    civic.generate(city)
    coast.generate(harbour)
    check_sources()
    check_reserves(city, civic.RESERVES)
    check_reserves(harbour, coast.RESERVES)
    check_civic(city)
    docks = check_coast(harbour, meshes)
    issues = integration_issues(harbour, meshes)
    combined = city.items + harbour.items
    used = set(item["mesh"] for item in combined)
    required = {"DetailedPlanter", "DetailedStreetLamp", "TrafficSignal", "RoadBarrier", "HarborBollard", "BusStopSign"}
    assert required <= used
    report = dict(sourceGeometry="PASS", engineAccepted=False, civicInstances=len(city.items),
                  coastalInstances=len(harbour.items), collisionInstances=sum(item["collision"] for item in combined),
                  meshCounts=dict(Counter(item["mesh"] for item in combined)), materialCount=len(finishes.MATERIAL_IDS),
                  serviceIds=[name + "_Read" for name, _ in civic.SERVICES], piers=docks, integrationIssues=issues,
                  requiredEngineChecks=["material creation/import and map reopen", "actual simple collision bounds",
                                        "walk all civic entrances and service prompts", "complete every vessel route",
                                        "boarding and alighting with actual capsule", "GPU art and frame-time capture"])
    output = ROOT / "Saved/QA/CityDistricts/source-audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
