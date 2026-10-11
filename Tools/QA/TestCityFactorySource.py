"""Real-source regressions and isolated geometric correction examples, without Unreal."""

import copy
import unittest

from VerifyCityFactorySource import (
    RecordingLayout, audit_factory, overlaps, post_height_accepted, shutter_meets_apron,
    shutter_mounted, within_reserve, within_x,
)


class FactorySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = audit_factory()
        cls.checks = cls.audit["geometryChecks"]

    def test_real_source_is_corrected(self):
        self.assertTrue(self.audit["passed"])
        self.assertEqual(self.audit["issues"], [])
        self.assertTrue(all(check["passed"] for check in self.checks.values()))
        self.assertEqual(len(self.audit["sourceSha256"]), 64)

    def test_cube_bounds_and_yaw_are_measured(self):
        layout = RecordingLayout()
        layout.box("Test", (10, 20, 30), (20, 40, 60))
        self.assertEqual(layout.items[0]["min"], [0, 0, 0])
        self.assertEqual(layout.items[0]["max"], [20, 40, 60])
        layout.add("Cube", (0, 0, 0), (2, 1, 3), yaw=90)
        self.assertEqual(layout.items[1]["sizeCm"], [100, 200, 300])

    def test_loading_width_is_within_shell(self):
        shell = self.checks["loading-outside-shell-width"]["shell"]
        apron = self.checks["shutter-apron-gap"]["apron"]
        self.assertEqual(apron["sizeCm"], [3000, 1200, 40])
        self.assertEqual(apron["max"][0], shell["max"][0])
        self.assertTrue(within_x(apron, shell))
        broken = copy.deepcopy(apron)
        broken["max"][0] += 1
        self.assertFalse(within_x(broken, shell))

    def test_shutter_mounting_and_apron_alignment(self):
        shell = self.checks["loading-outside-shell-width"]["shell"]
        apron = self.checks["shutter-apron-gap"]["apron"]
        for measured in self.checks["shutter-mounting-gap"]["shutters"]:
            self.assertEqual(measured["mountingGapCm"], 0)
            self.assertEqual(measured["apronGapCm"], 0)
            shutter = measured["instance"]
            self.assertEqual(shutter["sizeCm"], [920, 54, 1160])
            self.assertTrue(shutter_mounted(shutter, shell))
            self.assertTrue(shutter_meets_apron(shutter, apron))
            broken_wall = copy.deepcopy(shutter)
            broken_wall["max"][1] += 1
            self.assertFalse(shutter_mounted(broken_wall, shell))
            broken_floor = copy.deepcopy(shutter)
            broken_floor["min"][2] += 1
            self.assertFalse(shutter_meets_apron(broken_floor, apron))

    def test_bollard_height_target_and_boundaries(self):
        for post in self.checks["bollard-human-scale"]["bollards"]:
            self.assertEqual(post["sizeCm"], [70, 70, 110])
            self.assertTrue(post_height_accepted(post))
            broken = copy.deepcopy(post)
            broken["max"][2] = broken["min"][2] + 141
            self.assertFalse(post_height_accepted(broken))
            for height, expected in ((79, False), (80, True), (110, True), (140, True), (141, False)):
                corrected = copy.deepcopy(post)
                corrected["max"][2] = corrected["min"][2] + height
                self.assertEqual(post_height_accepted(corrected), expected)

    def test_reserve_and_lane_are_currently_clear(self):
        self.assertTrue(self.checks["reserve-containment"]["passed"])
        self.assertTrue(self.checks["public-access-lane"]["passed"])
        lane = self.audit["accessLaneCm"]
        self.assertEqual(lane["widthCm"], 600)
        self.assertTrue(overlaps(lane, lane))
        touching = copy.deepcopy(lane)
        touching["min"] = list(touching["min"])
        touching["max"] = list(touching["max"])
        touching["min"][0] = lane["max"][0]
        touching["max"][0] += 100
        self.assertFalse(overlaps(touching, lane))
        apron = self.checks["shutter-apron-gap"]["apron"]
        self.assertTrue(within_reserve(apron, self.audit["reserveCm"]))
        outside = copy.deepcopy(apron)
        outside["max"][0] = self.audit["reserveCm"][2] + 1
        self.assertFalse(within_reserve(outside, self.audit["reserveCm"]))

    def test_planter_manifest_bounds_do_not_claim_false_collision(self):
        check = self.checks["planter-loading-aabb"]
        self.assertTrue(check["passed"])
        self.assertEqual(check["planterBounds"][0]["sizeCm"], [138.4192, 129.4812, 138.5])
        nearest = min(check["bollardSeparations"], key=lambda item: sum(item["axisSeparationCm"]))
        self.assertEqual(nearest["axisSeparationCm"], [96.55, 0, 0])


if __name__ == "__main__":
    unittest.main()
