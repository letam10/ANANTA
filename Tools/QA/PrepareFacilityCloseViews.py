"""Prepare deterministic, close ground views for the Airport terminal review."""

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = (("front", 0.0), ("rear", 180.0), ("left", -90.0),
              ("right", 90.0), ("upper", 45.0))
GROUND_EYE_HEIGHT_CM = 170.0


def _point(value, name):
    if len(value) != 3:
        raise ValueError(f"{name} must contain x, y, z")
    return tuple(float(item) for item in value)


def _site_size(value):
    size = _point(value, "site_size")
    if any(item <= 0 for item in size):
        raise ValueError("site_size values must be positive")
    return size


def build_close_views(location, target, site_size):
    """Return front, rear, left, right and upper terminal camera records.

    ``location`` is the terminal ground anchor, ``target`` is the point to keep
    centred, and ``site_size`` is the terminal envelope in centimetres.  The
    four horizontal views use a player eye height; the upper view is elevated
    only enough to show the terminal roof and its immediate apron.
    """
    origin = _point(location, "location")
    focus = _point(target, "target")
    width, depth, height = _site_size(site_size)
    radius = max(650.0, math.hypot(width, depth) * 0.62)
    upper_radius = max(700.0, math.hypot(width, depth) * 0.72)
    views = []
    for direction, angle in DIRECTIONS:
        distance = upper_radius if direction == "upper" else radius
        eye_height = (origin[2] + GROUND_EYE_HEIGHT_CM
                      if direction != "upper"
                      else origin[2] + max(900.0, height * 0.95))
        radians = math.radians(angle)
        eye = (origin[0] + math.cos(radians) * distance,
               origin[1] + math.sin(radians) * distance,
               eye_height)
        delta_x = focus[0] - eye[0]
        delta_y = focus[1] - eye[1]
        delta_z = focus[2] - eye[2]
        yaw = math.degrees(math.atan2(delta_y, delta_x))
        pitch = math.degrees(math.atan2(delta_z, math.hypot(delta_x, delta_y)))
        views.append({
            "id": "Airport",
            "direction": direction,
            "location": [round(value, 3) for value in eye],
            "target": [round(value, 3) for value in focus],
            "rotation": [round(pitch, 3), round(yaw, 3), 0.0],
            "distanceCm": round(distance, 3),
            "eyeHeightCm": round(eye_height - origin[2], 3),
        })
    assert [view["direction"] for view in views] == [item[0] for item in DIRECTIONS]
    return views


def _validate(views, location, target):
    assert len(views) == 5
    assert [view["direction"] for view in views] == [item[0] for item in DIRECTIONS]
    ground_z = float(location[2])
    for view in views:
        assert view["target"] == [round(float(item), 3) for item in target]
        assert view["distanceCm"] > 0
        if view["direction"] != "upper":
            assert view["eyeHeightCm"] == GROUND_EYE_HEIGHT_CM
            assert view["location"][2] == round(ground_z + GROUND_EYE_HEIGHT_CM, 3)
        else:
            assert view["eyeHeightCm"] > GROUND_EYE_HEIGHT_CM


def main():
    location = (228000.0, 204000.0, 21.0)
    target = (228000.0, 204000.0, 620.0)
    site_size = (6600.0, 4200.0, 1400.0)
    views = build_close_views(location, target, site_size)
    _validate(views, location, target)
    output = ROOT / "Saved/QA/CityAirportCloseViews.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "facility": "Airport",
        "purpose": "Close ground-level terminal review",
        "locationCm": list(location),
        "targetCm": list(target),
        "siteSizeCm": list(site_size),
        "views": views,
        "accepted": False,
        "visualReview": "Pending Unreal capture; this manifest does not prove visual acceptance.",
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"views": len(views), "output": str(output)}))


if __name__ == "__main__":
    main()

