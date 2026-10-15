"""Regression tests for the source-only airport terminal camera manifest."""

import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))

import CityMetroDistrict as metro
import PrepareFacilityCloseViews as airport


class FacilityCloseViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views = airport.build_close_views(
            airport.TERMINAL_LOCATION,
            airport.TERMINAL_TARGET,
            airport.TERMINAL_SIZE,
        )

    def test_real_airport_source_uses_terminal_anchor(self):
        source = inspect.getsource(metro.airport)
        self.assertIn("shell(layout, 186000, 188000, 750", source)
        self.assertNotIn("shell(layout, 228000, 204000", source)
        self.assertNotEqual(airport.TERMINAL_LOCATION[:2], (228000, 204000))

    def test_five_views_have_stable_identity_and_order(self):
        directions = [view["direction"] for view in self.views]
        self.assertEqual(
            directions,
            ["front", "rear", "left", "right", "upper"],
        )
        self.assertEqual({view["id"] for view in self.views}, {"AirportTerminal"})
        self.assertEqual(len({tuple(view["location"]) for view in self.views}), 5)

    def test_horizontal_directions_face_the_correct_sides(self):
        locations = {view["direction"]: view["location"] for view in self.views}
        x, y, _ = airport.TERMINAL_LOCATION
        self.assertLess(locations["front"][1], y)
        self.assertGreater(locations["rear"][1], y)
        self.assertLess(locations["left"][0], x)
        self.assertGreater(locations["right"][0], x)
        self.assertGreater(locations["upper"][2], y - x)

    def test_all_eight_corners_project_inside_frame(self):
        for view in self.views:
            projection = view["projection"]
            self.assertEqual(projection["cornerCount"], 8)
            self.assertGreater(projection["minDepthCm"], 0)
            self.assertLessEqual(
                projection["maxAbsNormalized"],
                projection["frameMargin"],
            )
            self.assertTrue(projection["passes"])

    def test_ground_eye_height_and_upper_clearance(self):
        for view in self.views:
            if view["direction"] == "upper":
                self.assertGreater(
                    view["eyeHeightCm"],
                    airport.GROUND_EYE_HEIGHT_CM,
                )
            else:
                self.assertEqual(
                    view["eyeHeightCm"],
                    airport.GROUND_EYE_HEIGHT_CM,
                )

    def test_default_target_rejects_old_site_centre(self):
        old_site_centre = (228000.0, 204000.0, 620.0)
        self.assertNotEqual(airport.TERMINAL_TARGET, old_site_centre)
        self.assertTrue(all(view["target"] != list(old_site_centre)
                            for view in self.views))

    def test_input_validation_and_determinism(self):
        with self.assertRaises(ValueError):
            airport.build_close_views((0, 0), airport.TERMINAL_TARGET,
                                      airport.TERMINAL_SIZE)
        with self.assertRaises(ValueError):
            airport.build_close_views(airport.TERMINAL_LOCATION,
                                      airport.TERMINAL_TARGET, (0, 1, 1))
        repeat = airport.build_close_views(
            airport.TERMINAL_LOCATION,
            airport.TERMINAL_TARGET,
            airport.TERMINAL_SIZE,
        )
        self.assertEqual(self.views, repeat)


if __name__ == "__main__":
    unittest.main()
