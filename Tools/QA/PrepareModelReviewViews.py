"""Build deterministic eight-direction model and five-angle placement reviews."""

import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSET_ROOT = ROOT / "Assets" / "City"
OUTPUT = ROOT / "Saved" / "QA" / "CityModelReviewViews.json"

MODEL_DIRECTIONS = (
    ("front", 0.0),
    ("front_right", 45.0),
    ("right", 90.0),
    ("rear_right", 135.0),
    ("rear", 180.0),
    ("rear_left", 225.0),
    ("left", 270.0),
    ("front_left", 315.0),
)
PLACEMENT_DIRECTIONS = (
    ("front", 0.0),
    ("rear", 180.0),
    ("left", 270.0),
    ("right", 90.0),
    ("upper", 45.0),
)


def _point(value, name):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{name} must contain three numbers")
    return tuple(float(item) for item in value)


def _bounds(mesh):
    bounds = mesh.get("boundsCm")
    if not isinstance(bounds, dict):
        raise ValueError(f"{mesh.get('id', '<unnamed>')} has no boundsCm")
    low = _point(bounds.get("min"), "boundsCm.min")
    high = _point(bounds.get("max"), "boundsCm.max")
    if any(high[index] <= low[index] for index in range(3)):
        raise ValueError(f"{mesh.get('id', '<unnamed>')} has invalid bounds")
    return low, high


def _look_at(eye, target):
    delta_x = target[0] - eye[0]
    delta_y = target[1] - eye[1]
    delta_z = target[2] - eye[2]
    yaw = math.degrees(math.atan2(delta_y, delta_x))
    pitch = math.degrees(math.atan2(delta_z, math.hypot(delta_x, delta_y)))
    return [round(pitch, 3), round(yaw, 3), 0.0]


def _camera(direction, angle, radius, eye_z, target):
    radians = math.radians(angle)
    eye = (
        math.cos(radians) * radius,
        math.sin(radians) * radius,
        eye_z,
    )
    return {
        "direction": direction,
        "locationCm": [round(value, 3) for value in eye],
        "targetCm": [round(value, 3) for value in target],
        "rotationDeg": _look_at(eye, target),
        "distanceCm": round(radius, 3),
    }


def _views(mesh_id, low, high):
    size = tuple(high[index] - low[index] for index in range(3))
    target_z = low[2] + size[2] * 0.5
    target = (0.0, 0.0, target_z)
    horizontal_radius = max(75.0, math.hypot(size[0], size[1]) * 0.75)
    model_eye_z = target_z + max(30.0, size[2] * 0.18)
    placement_radius = max(150.0, math.hypot(size[0], size[1]) * 1.05)
    placement_eye_z = max(170.0, low[2] + 170.0)
    upper_eye_z = low[2] + max(400.0, size[2] * 1.10)
    model_views = [
        _camera(name, angle, horizontal_radius, model_eye_z, target)
        for name, angle in MODEL_DIRECTIONS
    ]
    placement_views = []
    for name, angle in PLACEMENT_DIRECTIONS:
        eye_z = upper_eye_z if name == "upper" else placement_eye_z
        placement_views.append(_camera(name, angle, placement_radius, eye_z, target))
    if len(model_views) != 8 or len(placement_views) != 5:
        raise AssertionError(f"{mesh_id} view count changed")
    return model_views, placement_views


def collect_meshes():
    records = []
    seen = set()
    for manifest_path in sorted(ASSET_ROOT.glob("*manifest.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for mesh in payload.get("meshes", []):
            mesh_id = mesh.get("id")
            if not mesh_id or mesh_id in seen:
                continue
            low, high = _bounds(mesh)
            model_views, placement_views = _views(mesh_id, low, high)
            records.append({
                "id": mesh_id,
                "sourceManifest": manifest_path.relative_to(ROOT).as_posix(),
                "file": mesh.get("file"),
                "boundsCm": {"min": list(low), "max": list(high)},
                "triangles": int(mesh.get("triangles", 0)),
                "materialSlots": list(mesh.get("materialSlots", [])),
                "modelViews": model_views,
                "placementViews": placement_views,
            })
            seen.add(mesh_id)
    if not records:
        raise RuntimeError("No mesh records were found in Assets/City/*manifest.json")
    return records


def validate(records):
    for record in records:
        assert len(record["modelViews"]) == 8
        assert len(record["placementViews"]) == 5
        assert record["triangles"] >= 0
        assert record["materialSlots"]
        assert all(view["distanceCm"] > 0 for view in record["modelViews"])
        assert all(view["distanceCm"] > 0 for view in record["placementViews"])


def main():
    records = collect_meshes()
    validate(records)
    categories = Counter(Path(record["sourceManifest"]).stem for record in records)
    payload = {
        "schemaVersion": 1,
        "units": "cm",
        "purpose": "Offline model and placement review; no Unreal render acceptance",
        "forwardAxis": "X",
        "upAxis": "Z",
        "modelDirections": [name for name, _ in MODEL_DIRECTIONS],
        "placementDirections": [name for name, _ in PLACEMENT_DIRECTIONS],
        "models": records,
        "summary": {
            "models": len(records),
            "modelViews": len(records) * 8,
            "placementViews": len(records) * 5,
            "sourceManifests": dict(sorted(categories.items())),
        },
        "accepted": False,
        "visualReview": "Pending Unreal/native capture; this manifest proves camera coverage only.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
