"""Offline regressions against compact native fixtures, without Unreal or Saved files."""

import itertools
import math
import unittest

from CitySmallPlacementCameras import cameras


# Provenance: Saved/QA/CitySmallNativeBounds.json, read-only persisted-map readback,
# 2026-10-10, 36 entries / 67 source actors. Bounds rounded to six decimals (cm).
# The compact blocker is Dressing_Apartment_BedroomVase, NOT a TableLamp actor.
KITCHEN = {
    "CookingPot": ((-33241, -4714.5, 120), (-33219, -4685.5, 132.5)),
    "Saucepan": ((-33168, -4689.000002, 120), (-33132, -4671.000002, 127.5)),
    "kettle": ((-33216.044542, -4712.427652, 120), (-33183.955469, -4687.572348, 150.474001)),
    "microwave": ((-33327.500004, -4727.276348, 120), (-33271.949999, -4680.999996, 152.5)),
    "counter": ((-33347, -4741.500023, 15), (-33053, -4658.499977, 119.999992)),
}
BEDROOM = {
    "MakeupCompact": ((3196.197162, 2946.5, 54), (3203.802838, 2953.5, 61.488924)),
    "vase": ((3194.387970, 2904.388019, 53.999956), (3205.612021, 2915.611980, 95.437138)),
    "table": ((3170.000004, 2849.908497, 14.999987), (3230.000021, 2970.091503, 53.999985)),
    "bed": ((2914.000015, 2759.999992, 17), (3086.000015, 2979.000015, 140)),
    "back_wall": ((3337.5, 1700, 15), (3362.5, 3300, 335)),
    "ceiling": ((1350, 1700, 327), (3350, 3300, 335)),
}
PLACEMENTS = {
    "CookingPot": ((-33230, -4700, 120), (22, 29, 12.5), KITCHEN),
    "Saucepan": ((-33150, -4680, 120), (36, 18, 7.5), KITCHEN),
    "MakeupCompact": ((3200, 2950, 54), (7.605676, 7, 7.488924), BEDROOM),
}
ANGLES = {"front": 0, "rear": 180, "left": -90, "right": 90, "upper": 45}


def hits(start, end, bounds):
    """Conservative segment/AABB intersection, including an eye inside the box."""
    near, far = 0, 1
    for axis in range(3):
        delta = end[axis] - start[axis]
        if abs(delta) < 1e-10:
            if not bounds[0][axis] <= start[axis] <= bounds[1][axis]:
                return False
            continue
        first, last = sorted((bounds[side][axis] - start[axis]) / delta for side in (0, 1))
        near = max(near, first)
        far = min(far, last)
        if near > far:
            return False
    return True


def target_for(location, size):
    return [location[0], location[1], location[2] + size[2] * .45]


def legacy_eye(location, size, direction):
    """Frozen old small-scope formula; deliberately independent of the new helper."""
    target = target_for(location, size)
    radius = max(100, math.hypot(size[0], size[1]) * .9)
    angle = math.radians(ANGLES[direction])
    rise = radius * (1.1 if direction == "upper" else .35)
    return [target[0] + radius * math.cos(angle), target[1] + radius * math.sin(angle), target[2] + rise]


class SmallCameraTests(unittest.TestCase):
    def test_intersection_distinguishes_segment_and_infinite_line(self):
        box = ((1, -1, -1), (2, 1, 1))
        self.assertTrue(hits((0, 0, 0), (3, 0, 0), box))
        self.assertTrue(hits((1.5, 0, 0), (3, 0, 0), box))
        self.assertFalse(hits((3, 0, 0), (4, 0, 0), box))
        self.assertFalse(hits((0, 2, 0), (3, 2, 0), box))

    def test_three_legacy_occlusions_from_native_bounds(self):
        cases = (("CookingPot", "front", "kettle"), ("CookingPot", "rear", "microwave"),
                 ("MakeupCompact", "left", "vase"))
        for name, direction, blocker in cases:
            with self.subTest(name=name, direction=direction):
                location, size, scene = PLACEMENTS[name]
                self.assertTrue(hits(legacy_eye(location, size, direction),
                                     target_for(location, size), scene[blocker]))

    def test_all_fifteen_new_central_rays_clear_known_neighbors(self):
        for name, (location, size, scene) in PLACEMENTS.items():
            for view in cameras(name, location, size, 0):
                for other, bounds in scene.items():
                    if other == name:
                        continue
                    with self.subTest(name=name, direction=view["direction"], blocker=other):
                        self.assertFalse(hits(view["location"], target_for(location, size), bounds))

    def test_changed_views_clear_entire_target_box_of_reported_blocker(self):
        cases = (("CookingPot", "front", "kettle"), ("CookingPot", "rear", "microwave"),
                 ("Saucepan", "rear", "kettle"), ("MakeupCompact", "left", "vase"))
        for name, direction, blocker in cases:
            location, size, scene = PLACEMENTS[name]
            view = next(item for item in cameras(name, location, size, 0) if item["direction"] == direction)
            corners = itertools.product(*(tuple(scene[name][side][axis] for side in (0, 1)) for axis in range(3)))
            for corner in corners:
                with self.subTest(name=name, direction=direction, corner=corner):
                    self.assertFalse(hits(view["location"], corner, scene[blocker]))

    def test_saucepan_old_center_was_clear_despite_foreground_kettle(self):
        location, size, scene = PLACEMENTS["Saucepan"]
        self.assertFalse(hits(legacy_eye(location, size, "rear"), target_for(location, size), scene["kettle"]))

    def test_api_directions_aim_roll_and_yaw(self):
        for name, (location, size, _) in PLACEMENTS.items():
            for yaw in (0, 90, 213):
                views = cameras(name, location, size, yaw)
                self.assertEqual([item["direction"] for item in views], list(ANGLES))
                target = target_for(location, size)
                for view in views:
                    self.assertEqual(set(view), {"id", "direction", "location", "rotation"})
                    self.assertEqual(view["id"], name)
                    self.assertEqual(view["rotation"][2], 0)
                    pitch, heading, _ = map(math.radians, view["rotation"])
                    forward = (math.cos(pitch) * math.cos(heading),
                               math.cos(pitch) * math.sin(heading), math.sin(pitch))
                    delta = [target[i] - view["location"][i] for i in range(3)]
                    length = math.sqrt(sum(value * value for value in delta))
                    for axis in range(3):
                        self.assertAlmostEqual(forward[axis], delta[axis] / length, places=9)
                    angle = math.radians(yaw + ANGLES[view["direction"]])
                    self.assertAlmostEqual(delta[0] * math.sin(angle) - delta[1] * math.cos(angle), 0, places=8)

    def test_other_props_retain_old_camera_plan(self):
        cases = (("KitchenBowl", (17, 17, 6.7)), ("CoffeeMug", (11.6, 8, 10)),
                 ("ToyBlocks", (20, 10.7, 10)), ("RoomVase", (12, 12, 22)),
                 ("BathroomSoap", (12, 8.2, 4)), ("KitchenSink", (60, 71, 57.569374)))
        for name, size in cases:
            location = (3000, 2000, 95)
            for view in cameras(name, location, size, 0):
                self.assertEqual(view["location"], legacy_eye(location, size, view["direction"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
