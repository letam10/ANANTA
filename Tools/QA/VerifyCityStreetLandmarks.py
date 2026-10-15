"""Audit authored landmarks against source geometry, routes and transformed mesh bounds."""

import ast
from collections import Counter
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityExpansionData import ROAD_LINES, reserved_rectangles
from CityExpansionLayout import generate
from CityStreetLandmarks import SPACES, describe


def intersects(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def bounds(item, meshes):
    local = meshes[item["mesh"]]["boundsCm"]
    angle = math.radians(item["yaw"])
    cosine, sine = math.cos(angle), math.sin(angle)
    x, y, z = item["location"]
    sx, sy, sz = item["scale"]
    # Xoay ca bon goc cua hop mesh; tam vat the khong du de chung minh khoang trong.
    corners = [(x + xx * sx * cosine - yy * sy * sine, y + xx * sx * sine + yy * sy * cosine)
               for xx in (local["min"][0], local["max"][0])
               for yy in (local["min"][1], local["max"][1])]
    xy = (min(p[0] for p in corners), min(p[1] for p in corners),
          max(p[0] for p in corners), max(p[1] for p in corners))
    return xy, (z + local["min"][2] * sz, z + local["max"][2] * sz)


def mission_anchors():
    source = ast.parse((ROOT / "Tools/Editor/CityInteriors.py").read_text(encoding="utf-8"))
    mission = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "mission")
    anchors = []
    for node in ast.walk(mission):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "positions"
                                             for t in node.targets):
            anchors.extend(ast.literal_eval(node.value))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "spawn":
            if len(node.args) > 2 and isinstance(node.args[1], ast.Constant):
                if node.args[1].value == "City_MissionGiver":
                    anchors.append(ast.literal_eval(node.args[2]))
    assert len(anchors) == 4, "Mission anchor source format changed; update the audit"
    return anchors


def main():
    meshes = {"Cube": {"boundsCm": {"min": [-50] * 3, "max": [50] * 3}}}
    materials = set()
    for filename in ("manifest.json", "expansion_manifest.json"):
        data = json.loads((ROOT / "Assets/City" / filename).read_text(encoding="utf-8"))
        meshes.update((item["id"], item) for item in data["meshes"])
        materials.update(item["id"] for item in data["materials"])
    layout = generate()
    forbidden = [(f"Reserved{i}", rectangle) for i, rectangle in enumerate(reserved_rectangles())]
    forbidden.append(("Encounter", (24700, 3300, 27300, 5700)))
    for index, (x, y, _) in enumerate(mission_anchors()):
        forbidden.append((f"MissionAnchor{index}", (x - 500, y - 500, x + 500, y + 500)))
    for index, building in enumerate(layout["buildings"]):
        x, y = building["centre"]
        w, d = building["width"], building["depth"]
        # Du ra 100 cm de bao ca chi tiet mat tien vuot ngoai shell.
        forbidden.append((f"Building{index}", (x - w / 2 - 100, y - d / 2 - 100,
                                               x + w / 2 + 100, y + d / 2 + 100)))
    existing = []
    for group in layout["groups"]:
        if group["mesh"] == "Cube":
            continue
        for instance in group["instances"]:
            if not instance.get("buildingCentre"):
                item = dict(instance, mesh=group["mesh"])
                existing.append((group["mesh"], bounds(item, meshes)[0]))
    items = describe()
    errors = []
    if items != describe():
        errors.append("describe is not deterministic")
    labels = [item["label"] for item in items]
    if len(labels) != len(set(labels)) or any(not label.startswith("Landmark_") for label in labels):
        errors.append("Invalid or duplicate labels")
    if len(items) > 160:
        errors.append("More than 160 additions")
    measured = []
    for item in items:
        label = item["label"]
        if item["mesh"] not in meshes or item.get("material", "City_Paving") not in materials:
            errors.append(f"Unknown asset: {label}")
            continue
        if item["mesh"] != "Cube":
            asset = ROOT / "Content/ANANTA/City/Meshes" / ("SM_" + item["mesh"] + ".uasset")
            if not asset.is_file():
                errors.append(f"Missing imported mesh: {label}")
        if item.get("material"):
            asset = ROOT / "Content/ANANTA/City/Materials" / ("M_" + item["material"] + ".uasset")
            if not asset.is_file():
                errors.append(f"Missing imported material: {label}")
        xy, z = bounds(item, meshes)
        measured.append(dict(label=label, xy=xy, z=z))
        for name, rectangle in forbidden:
            if intersects(xy, rectangle):
                errors.append(f"{label} intersects {name}")
        for line in ROAD_LINES:
            if xy[0] < line + 1350 and xy[2] > line - 1350:
                errors.append(f"{label} intersects vertical road {line}")
            if xy[1] < line + 1350 and xy[3] > line - 1350:
                errors.append(f"{label} intersects horizontal road {line}")
        space = label.split("_")[1]
        x, y = SPACES[space]
        if not label.endswith("Paving"):
            if intersects(xy, (x - 250, y - 1800, x + 250, y + 1800)):
                errors.append(f"{label} blocks 500 cm centre passage")
            for mesh, rectangle in existing:
                if intersects(xy, rectangle):
                    errors.append(f"{label} intersects existing {mesh}")
        if item["collision"] and item["mesh"] not in ("Bench", "House_dining_chair_02", "Cube"):
            errors.append(f"Collision outside seating or low wall: {label}")
    # Ghe va tuong moi khong duoc chen vao nhau; cay trong bon la chu y thiet ke.
    for index, item in enumerate(items):
        if not item["collision"]:
            continue
        a, az = bounds(item, meshes)
        for other in items[index + 1:]:
            if not other["collision"]:
                continue
            b, bz = bounds(other, meshes)
            if intersects(a, b) and az[0] < bz[1] and az[1] > bz[0]:
                errors.append(f"Colliding furnishings overlap: {item['label']} / {other['label']}")
    report = dict(passed=not errors, additions=len(items), countBySpace=dict(Counter(
        item["label"].split("_")[1] for item in items)), spaceCentres=SPACES,
        buildingsChecked=len(layout["buildings"]), reservedChecked=len(reserved_rectangles()),
        missionAnchorsChecked=4, minimumCentrePassageCm=500, fullTransformedBounds=True,
        inEngineVerified=False, errors=errors, measuredBounds=measured)
    output = ROOT / "Saved/QA/CityLandmarkAudit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "measuredBounds"}))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
