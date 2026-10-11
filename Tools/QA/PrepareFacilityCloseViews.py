"""Prepare deterministic close views for the real airport terminal anchor."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TERMINAL_LOCATION = (186000.0, 188000.0, 20.0)
TERMINAL_TARGET = (186000.0, 188000.0, 425.0)
TERMINAL_SIZE = (6800.0, 5680.0, 810.0)
GROUND_EYE_HEIGHT_CM = 170.0
HORIZONTAL_FOV_DEGREES = 75.0
ASPECT_RATIO = 16.0 / 9.0
FRAME_MARGIN = 0.92
DIRECTIONS = (
    ("front", (0.0, -1.0, 0.0)),
    ("rear", (0.0, 1.0, 0.0)),
    ("left", (-1.0, 0.0, 0.0)),
    ("right", (1.0, 0.0, 0.0)),
    ("upper", (math.sqrt(0.5), -math.sqrt(0.5), 0.0)),
)


def _point(value, name):
    if len(value) != 3:
        raise ValueError(f"{name} must contain x y z")
    return tuple(float(item) for item in value)


def _site_size(value):
    size = _point(value, "site_size")
    if any(item <= 0 for item in size):
        raise ValueError("site_size values must be positive")
    return size


def _normalize(vector):
    length = math.sqrt(sum(item * item for item in vector))
    if length <= 0:
        raise ValueError("direction must not be zero")
    return tuple(item / length for item in vector)


def _dot(first, second):
    return sum(first[index] * second[index] for index in range(3))


def _cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def _camera_rotation(eye, target):
    delta = tuple(target[index] - eye[index] for index in range(3))
    yaw = math.degrees(math.atan2(delta[1], delta[0]))
    pitch = math.degrees(math.atan2(delta[2], math.hypot(delta[0], delta[1])))
    return [round(pitch, 3), round(yaw, 3), 0.0]


def _envelope_corners(location, site_size):
    width, depth, height = site_size
    half_width = width / 2.0
    half_depth = depth / 2.0
    return [
        (location[0] + x, location[1] + y, location[2] + z)
        for x in (-half_width, half_width)
        for y in (-half_depth, half_depth)
        for z in (0.0, height)
    ]


def _project_envelope(eye, target, site_size, location):
    forward = _normalize(tuple(target[index] - eye[index] for index in range(3)))
    right = _normalize((-forward[1], forward[0], 0.0))
    up = _normalize(_cross(forward, right))
    horizontal_half_angle = math.radians(HORIZONTAL_FOV_DEGREES / 2.0)
    vertical_half_angle = math.atan(math.tan(horizontal_half_angle) / ASPECT_RATIO)
    tangent_x = math.tan(horizontal_half_angle)
    tangent_y = math.tan(vertical_half_angle)
    normalized = []
    depths = []
    for corner in _envelope_corners(location, site_size):
        offset = tuple(corner[index] - eye[index] for index in range(3))
        depth = _dot(offset, forward)
        depths.append(depth)
        if depth <= 0:
            continue
        normalized.append((
            _dot(offset, right) / (depth * tangent_x),
            _dot(offset, up) / (depth * tangent_y),
        ))
    maximum = max(
        (max(abs(axis) for axis in pair) for pair in normalized),
        default=math.inf,
    )
    return {
        "cornerCount": 8,
        "minDepthCm": round(min(depths), 3),
        "maxAbsNormalized": round(maximum, 6),
        "frameMargin": FRAME_MARGIN,
        "passes": (
            len(normalized) == 8
            and min(depths) > 0
            and maximum <= FRAME_MARGIN
        ),
    }


def build_close_views(location, target, site_size):
    """Return exactly five close camera records around the terminal envelope."""
    origin = _point(location, "location")
    focus = _point(target, "target")
    size = _site_size(site_size)
    width, depth, height = size
    radius = max(10000.0, math.hypot(width, depth) * 1.4)
    upper_radius = max(11000.0, math.hypot(width, depth) * 1.6)
    views = []
    for direction, vector in DIRECTIONS:
        normalized = _normalize(vector)
        distance = upper_radius if direction == "upper" else radius
        eye_height = (
            origin[2] + GROUND_EYE_HEIGHT_CM
            if direction != "upper"
            else origin[2] + max(height + 1200.0, 2000.0)
        )
        eye = tuple(
            origin[index] + normalized[index] * distance
            for index in range(3)
        )
        eye = (eye[0], eye[1], eye_height)
        projection = _project_envelope(eye, focus, size, origin)
        views.append({
            "id": "AirportTerminal",
            "direction": direction,
            "location": [round(value, 3) for value in eye],
            "target": [round(value, 3) for value in focus],
            "rotation": _camera_rotation(eye, focus),
            "distanceCm": round(distance, 3),
            "eyeHeightCm": round(eye_height - origin[2], 3),
            "projection": projection,
        })
    _validate(views, origin, focus)
    return views


def _validate(views, location, target):
    assert len(views) == len(DIRECTIONS)
    assert [view["direction"] for view in views] == [
        item[0] for item in DIRECTIONS
    ]
    target_values = [round(float(item), 3) for item in target]
    for view in views:
        assert view["id"] == "AirportTerminal"
        assert view["target"] == target_values
        assert view["distanceCm"] > 0
        assert view["projection"]["passes"]
        if view["direction"] != "upper":
            assert view["eyeHeightCm"] == GROUND_EYE_HEIGHT_CM
        else:
            assert view["eyeHeightCm"] > GROUND_EYE_HEIGHT_CM


def main():
    views = build_close_views(
        TERMINAL_LOCATION,
        TERMINAL_TARGET,
        TERMINAL_SIZE,
    )
    output = ROOT / "Saved/QA/CityAirportCloseViews.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 2,
        "facility": "AirportTerminal",
        "purpose": "Close five angle terminal review",
        "locationCm": list(TERMINAL_LOCATION),
        "targetCm": list(TERMINAL_TARGET),
        "siteSizeCm": list(TERMINAL_SIZE),
        "horizontalFovDegrees": HORIZONTAL_FOV_DEGREES,
        "aspectRatio": ASPECT_RATIO,
        "views": views,
        "accepted": False,
        "visualReview": (
            "Pending Unreal capture; this manifest does not prove visual acceptance."
        ),
    }
    output.write_text(
        json.dumps(payload, indent=2) + chr(10),
        encoding="utf-8",
    )
    print(json.dumps({
        "views": len(views),
        "output": str(output),
        "accepted": False,
    }))


if __name__ == "__main__":
    main()
