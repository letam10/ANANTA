"""Source render budget gate; reports reuse and LOD readiness without running Unreal."""

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ROOT = ROOT / "Assets" / "City"
LAYOUT_INPUT = ROOT / "Saved" / "QA" / "CityExpansionLayout.json"
OUTPUT = ROOT / "Saved" / "QA" / "CityPerformanceSourceAudit.json"
DECORATIVE_COLLISIONLESS = {
    "DetailedStreetLamp",
    "BusStopSign",
    "TrafficSignal",
    "RoadBarrier",
}


def load_layout():
    if not LAYOUT_INPUT.exists():
        raise FileNotFoundError(LAYOUT_INPUT)
    return json.loads(LAYOUT_INPUT.read_text(encoding="utf-8"))


def layout_budget(payload):
    groups = payload.get("groups", [])
    signatures = defaultdict(int)
    invalid = []
    water_collision = []
    decorative_collision = []
    instance_count = 0
    for index, group in enumerate(groups):
        if not isinstance(group, dict) or not isinstance(group.get("instances"), list):
            invalid.append(index)
            continue
        mesh = group.get("mesh")
        count = len(group["instances"])
        signature = (mesh, group.get("material"), bool(group.get("collision", True)),
                     bool(group.get("hidden", False)))
        signatures[signature] += count
        instance_count += count
        if mesh == "DistrictWater" and group.get("collision", False):
            water_collision.append(index)
        if mesh in DECORATIVE_COLLISIONLESS and group.get("collision", True):
            decorative_collision.append((index, mesh))
    unique_signatures = len(signatures)
    reusable = max(0, instance_count - unique_signatures)
    return {
        "groupCount": len(groups),
        "instanceCount": instance_count,
        "uniqueSignatures": unique_signatures,
        "reusableInstances": reusable,
        "reusableFraction": round(reusable / instance_count, 6) if instance_count else 0,
        "invalidGroups": invalid,
        "waterCollisionGroups": water_collision,
        "decorativeCollisionGroups": decorative_collision,
        "topMeshes": dict(Counter(
            group.get("mesh") for group in groups if isinstance(group, dict)
        ).most_common(12)),
    }


def lod_budget():
    missing = []
    invalid = []
    mesh_count = 0
    for path in sorted(ASSET_ROOT.glob("*manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("meshes", []):
            mesh_count += 1
            identifier = f"{path.name}:{item.get('id')}"
            lod = item.get("lodRecommendation")
            if not lod:
                missing.append(identifier)
                continue
            screens = lod.get("screenSizes", [])
            ratios = lod.get("triangleRatios", [])
            if len(screens) < 3 or len(ratios) < 3:
                invalid.append(identifier)
                continue
            if screens[0] != 1 or ratios[0] != 1:
                invalid.append(identifier)
            if any(a < b for a, b in zip(screens, screens[1:])):
                invalid.append(identifier)
            if any(a < b for a, b in zip(ratios, ratios[1:])):
                invalid.append(identifier)
    return {
        "manifestMeshCount": mesh_count,
        "missingLodRecommendations": missing,
        "invalidLodRecommendations": sorted(set(invalid)),
    }


def main():
    errors = []
    payload = load_layout()
    layout = layout_budget(payload)
    lod = lod_budget()
    scene_text = (ROOT / "Tools" / "Editor" / "CityScene.py").read_text(encoding="utf-8")
    if not layout["groupCount"] or not layout["instanceCount"]:
        errors.append("Layout contains no render groups or instances")
    if layout["invalidGroups"]:
        errors.append("Layout contains invalid instance groups")
    if layout["reusableFraction"] < 0.99:
        errors.append("Reusable instance fraction is below 0.99")
    if layout["waterCollisionGroups"]:
        errors.append("Water groups must remain collision false")
    if lod["missingLodRecommendations"]:
        errors.append("One or more imported meshes lack LOD recommendations")
    if lod["invalidLodRecommendations"]:
        errors.append("One or more LOD recommendations are not monotonic")
    if "HierarchicalInstancedStaticMeshComponent" not in scene_text:
        errors.append("CityScene.py lacks HISM support")
    if "add_instances" not in scene_text:
        errors.append("CityScene.py lacks bulk instance insertion")
    report = {
        "status": "PASS" if not errors else "FAIL",
        "sourceOnly": True,
        "runtimeFpsVerified": False,
        "layout": layout,
        "lod": lod,
        "collisionReview": {
            "decorativeCollisionGroups": layout["decorativeCollisionGroups"],
            "interpretation": "Reported for review because signs barriers and some planters may intentionally block traversal",
        },
        "hism": {
            "componentPath": "HierarchicalInstancedStaticMeshComponent",
            "bulkInsertion": "add_instances",
        },
        "errors": errors,
        "limitations": [
            "No Unreal editor, packaged game, GPU capture, benchmark, or soak test was run.",
            "The reuse fraction is a source group metric, not a draw call or frame time measurement.",
            "LOD recommendations still require import and native visual review.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
