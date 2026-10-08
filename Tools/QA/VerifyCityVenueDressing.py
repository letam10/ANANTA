"""Source-only geometry audit; does not start or import Unreal."""

import ast
import argparse
from collections import Counter
from itertools import combinations, product
import json
import math
from pathlib import Path
import sys


PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityVenueDressing import ROOMS, describe


ARCHITECTURE_BOUNDS = {
    "InteriorServiceDesk": ((-55, -35, 0), (55, 35, 85)),
    "InteriorSlatPanel": ((-120, -4, 0), (120, 4, 220)),
    "InteriorGalleryFrame": ((-70, -3, 0), (70, 3, 110)),
    "InteriorBotanicalFrame": ((-70, -3, 0), (70, 3, 110)),
}


def transformed_bounds(item, meshes):
    bounds = ({"min": [-50] * 3, "max": [50] * 3} if item["mesh"] == "Cube"
              else meshes[item["mesh"]]["boundsCm"])
    angle = math.radians(item["yaw"])
    cosine, sine = math.cos(angle), math.sin(angle)
    vertices = []
    for corner in product(*zip(bounds["min"], bounds["max"])):
        x, y, z = (v * s for v, s in zip(corner, item["scale"]))
        rotated = (x * cosine - y * sine, x * sine + y * cosine, z)
        vertices.append(tuple(v + p for v, p in zip(rotated, item["location"])))
    return tuple(min(v[a] for v in vertices) for a in range(3)), tuple(
        max(v[a] for v in vertices) for a in range(3))


def capture_existing(manifest):
    items = []

    def prop(mesh, label, location, yaw=0, scale=(1, 1, 1), collision=True):
        items.append(dict(mesh=mesh, label=label, location=location, yaw=yaw, scale=scale,
                          collision=collision))

    def box(label, location, size, material="Concrete", collision=True):
        prop("Cube", label, location, scale=tuple(v / 100 for v in size), collision=collision)

    def room(prefix, centre, size, face, entry):
        return centre[0] + size[0] / 2 * face, centre[1]

    def service(identifier, kind, title, description, location, mesh="Bollard"):
        prop(mesh, "Service_" + identifier, location, collision=False)

    namespace = dict(prop=prop, box=box, room=room, text=lambda *args: None,
                     CAFE={key: value for key, value in ROOMS[0].items() if key != "id"},
                     APARTMENT={key: value for key, value in ROOMS[1].items() if key != "id"},
                     VENUES=ROOMS[2:])
    for filename in ("CityInteriors.py", "CityExpansionVenues.py"):
        path = PROJECT / "Tools/Editor" / filename
        tree = ast.parse(path.read_text(encoding="utf-8"))
        # Thuc thi bo tri goc qua ham thu thap, khong goi Editor hay tao tai san.
        tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
        exec(compile(tree, str(path), "exec"), namespace)
        namespace["service"] = service
        if filename == "CityInteriors.py":
            namespace["furnish"](manifest)
        else:
            namespace["furnish"]()
    return items


def overlaps(first, second):
    # Dung sai 1.3 cm cho tham mong va tiep xuc mat ban, khong bo qua vat lon.
    return all(min(first[1][axis], second[1][axis]) - max(first[0][axis], second[0][axis]) > 1.3
               for axis in range(3))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--architecture-contract", action="store_true")
    parser.add_argument("--report", type=Path, default=PROJECT / "Saved/QA/CityVenueDressingAudit.json")
    args = parser.parse_args()
    if args.architecture_contract and not args.source_only:
        parser.error("Contract bounds require --source-only; they do not verify imported assets")
    manifest = json.loads((PROJECT / "Assets/City/manifest.json").read_text(encoding="utf-8"))
    meshes = {item["id"]: item for item in manifest["meshes"]}
    expansion = json.loads((PROJECT / "Assets/City/expansion_manifest.json").read_text(encoding="utf-8"))
    meshes.update({item["id"]: item for item in expansion["meshes"]})
    finishing = json.loads((PROJECT / "Assets/City/finishing_manifest.json").read_text(encoding="utf-8"))
    meshes.update({item["id"]: item for item in finishing["meshes"]})
    architecture_path = PROJECT / "Assets/City/interior_architecture_manifest.json"
    architecture_source = "manifest"
    if architecture_path.is_file():
        architecture = json.loads(architecture_path.read_text(encoding="utf-8"))
        meshes.update({item["id"]: item for item in architecture["meshes"]})
    elif args.architecture_contract:
        architecture_source = "contract-only provisional bounds"
        meshes.update({key: {"boundsCm": dict(min=low, max=high)}
                       for key, (low, high) in ARCHITECTURE_BOUNDS.items()})
    else:
        parser.error("Missing interior_architecture_manifest.json; use --architecture-contract for provisional QA")
    workshop = json.loads((PROJECT / "Assets/City/workshop_detail_manifest.json").read_text(encoding="utf-8"))
    meshes.update({item["id"]: item for item in workshop["meshes"]})
    items = describe()
    errors = []
    for mesh, (low, high) in ARCHITECTURE_BOUNDS.items():
        actual = meshes.get(mesh, {}).get("boundsCm", {})
        if any(len(actual.get(key, ())) != 3 or any(abs(a - b) > 0.1 for a, b in zip(actual[key], expected))
               for key, expected in (("min", low), ("max", high))):
            errors.append("Architecture contract bounds mismatch " + mesh)
    labels = [item["label"] for item in items]
    if items != describe():
        errors.append("Non-deterministic describe output")
    if len(labels) != len(set(labels)):
        errors.append("Duplicate labels")
    if len(items) >= 240:
        errors.append("Interior additions must remain below 240")
    asset_root = PROJECT / "Content/ANANTA/City"
    for item in items:
        if item["mesh"] != "Cube":
            if item["mesh"] not in meshes:
                errors.append("Unknown mesh " + item["mesh"])
            if not args.source_only and not (asset_root / "Meshes" / f"SM_{item['mesh']}.uasset").is_file():
                errors.append("Mesh package missing " + item["mesh"])
        if item.get("material") and not args.source_only:
            if not (asset_root / "Materials" / f"M_{item['material']}.uasset").is_file():
                errors.append("Material package missing " + item["material"])
        if set(item) - {"label", "mesh", "location", "scale", "yaw", "collision", "material"}:
            errors.append("Unknown schema field " + item["label"])
        if any(s <= 0 for s in item["scale"]):
            errors.append("Invalid scale " + item["label"])
        if not all(math.isfinite(v) for v in (*item["location"], *item["scale"], item["yaw"])):
            errors.append("Non-finite transform " + item["label"])
        if item["mesh"] in ARCHITECTURE_BOUNDS and item["collision"]:
            errors.append("Architecture decoration must not collide " + item["label"])
    bounds = {item["label"]: transformed_bounds(item, meshes) for item in items}
    counts = Counter()
    for item in items:
        room = next((r for r in ROOMS if item["label"].startswith("Dressing_" + r["id"] + "_")), None)
        if room is None:
            errors.append("Label missing room " + item["label"])
            continue
        counts[room["id"]] += 1
        low, high = bounds[item["label"]]
        for axis in (0, 1):
            minimum = room["centre"][axis] - room["size"][axis] / 2 + 22
            maximum = room["centre"][axis] + room["size"][axis] / 2 - 22
            if low[axis] < minimum or high[axis] > maximum:
                errors.append("Outside inner walls " + item["label"])
        if low[2] < 14.95 or high[2] > 327:
            errors.append("Outside floor or ceiling " + item["label"])
        if item["collision"] and high[1] > room["centre"][1] - 220 and low[1] < room["centre"][1] + 220:
            errors.append("Entry corridor obstruction " + item["label"])
        if item["mesh"] in ARCHITECTURE_BOUNDS and item["mesh"] != "InteriorServiceDesk":
            front = room["centre"][0] + room["face"] * room["size"][0] / 2
            if low[0] < front + 50 and high[0] > front - 50:
                errors.append("Wall detail in entry or window zone " + item["label"])
            if high[1] > room["centre"][1] - 220 and low[1] < room["centre"][1] + 220:
                errors.append("Wall detail in central corridor " + item["label"])
    for first, second in combinations(items, 2):
        # Tham mem day 1.5 cm duoc phep nam duoi chan ghe va ban, khong co collision.
        if first["mesh"] == "InteriorWovenRug" or second["mesh"] == "InteriorWovenRug":
            continue
        if overlaps(bounds[first["label"]], bounds[second["label"]]):
            errors.append("New furniture overlap: " + first["label"] + " / " + second["label"])
    existing = capture_existing(manifest)
    existing_bounds = [(item, transformed_bounds(item, meshes)) for item in existing]
    comparisons = 0
    for item in items:
        if item["mesh"] == "InteriorWovenRug":
            low, high = bounds[item["label"]]
            if item["collision"] or low[2] < 15 or high[2] > 17:
                errors.append("Rug must be a thin noncolliding floor covering " + item["label"])
            continue
        for previous, previous_bounds in existing_bounds:
            comparisons += 1
            if overlaps(bounds[item["label"]], previous_bounds):
                errors.append("Existing overlap: " + item["label"] + " / " + previous["label"])
    for room in ROOMS:
        if counts[room["id"]] < 10:
            errors.append("Insufficient dressing " + room["id"])
        top = next(item for item in items if item["label"] == f"Dressing_{room['id']}_ServiceDesk")
        service_id = room.get("serviceId", room["id"] + "_Rest")
        marker = next(item for item in existing if item["label"] == "Service_" + service_id)
        marker_bounds = transformed_bounds(marker, meshes)
        top_bounds = bounds[top["label"]]
        if abs(top_bounds[1][2] - marker_bounds[0][2]) > 0.1:
            errors.append("Service surface height mismatch " + room["id"])
        if not all(top_bounds[0][a] <= marker_bounds[0][a] <= marker_bounds[1][a] <= top_bounds[1][a]
                   for a in (0, 1)):
            errors.append("Service object outside support " + room["id"])
        if top["collision"]:
            errors.append("Service support must not collide " + room["id"])
    source_paths = [PROJECT / "Tools/Editor/CityVenueDressing.py",
                    PROJECT / "Tools/Editor/CityInteriorFinishes.py",
                    PROJECT / "Tools/Editor/CityInteriorArchitecture.py",
                    PROJECT / "Tools/Editor/CityWorkshopDetail.py", Path(__file__)]
    for path in source_paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > 300:
            errors.append("File exceeds 300 lines " + path.name)
        for number, line in enumerate(lines, 1):
            if len(line) > 120:
                errors.append(f"Line exceeds 120 characters {path.name}:{number}")
    result = dict(passed=not errors, sourceOnly=args.source_only,
                  additions=len(items), rooms=dict(counts), deterministic=items == describe(),
                  uniqueLabels=len(labels) == len(set(labels)), corridorWidthCm=440,
                  architectureBoundsSource=architecture_source,
                  serviceDesks=sum(item["mesh"] == "InteriorServiceDesk" for item in items),
                  workshopDetails=sum(item["mesh"].startswith("Workshop") for item in items),
                  wallDetails=sum(item["mesh"] in ARCHITECTURE_BOUNDS
                                  and item["mesh"] != "InteriorServiceDesk" for item in items),
                  existingFurnitureCaptured=len(existing), existingBoundsComparisons=comparisons,
                  meshIds=sorted({item["mesh"] for item in items}), errors=errors,
                  limitations=["Source geometry audit only; root must apply and inspect GPU views.",
                               "Does not certify pre-existing furniture or runtime navigation."])
    path = args.report
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
