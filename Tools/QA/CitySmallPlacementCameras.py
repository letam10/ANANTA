"""Five QA views of the authored small props; distances are in native centimetres."""

import math


DIRECTIONS = (("front", 0, .35), ("rear", 180, .35), ("left", -90, .35),
              ("right", 90, .35), ("upper", 45, 1.1))

# Camera nằm trong khoảng trống trước vật che; không di chuyển đồ vật trong scene.
# Values are horizontal radius and height above the existing target, in centimetres.
OVERRIDES = {
    ("CookingPot", "front"): (12, 40),
    ("CookingPot", "rear"): (35, 25),
    ("Saucepan", "rear"): (32, 30),
    ("MakeupCompact", "left"): (28, 12),
}


def cameras(name, location, size, yaw):
    """Return front/rear/left/right/upper views, preserving the prop's local yaw."""
    radius = max(100, math.hypot(size[0], size[1]) * .9)
    target = [location[0], location[1], location[2] + size[2] * .45]
    result = []
    for direction, angle, elevation in DIRECTIONS:
        distance, rise = OVERRIDES.get((name, direction), (radius, radius * elevation))
        radians = math.radians(yaw + angle)
        eye = [target[0] + math.cos(radians) * distance,
               target[1] + math.sin(radians) * distance, target[2] + rise]
        delta = [target[i] - eye[i] for i in range(3)]
        pitch = math.degrees(math.atan2(delta[2], math.hypot(delta[0], delta[1])))
        facing = math.degrees(math.atan2(delta[1], delta[0]))
        result.append(dict(id=name, direction=direction, location=eye, rotation=[pitch, facing, 0]))
    return result
