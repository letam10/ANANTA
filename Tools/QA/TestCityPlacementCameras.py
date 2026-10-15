"""Reproduce real roof/dock occlusion and check the corrected five camera directions."""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
sys.path.insert(0, str(ROOT / "Tools/QA"))
from CityMetroDistrict import station
from CityInteractiveTransit import ROWBOAT, rowboat_dock
from PrepareCityPlacementViews import cameras


class Geometry:
    def __init__(self):
        self.boxes = []

    def box(self, material, location, size, *args):
        minimum = [location[i] - size[i] / 2 for i in range(3)]
        maximum = [location[i] + size[i] / 2 for i in range(3)]
        self.boxes.append((material, minimum, maximum))

    def add(self, *args, **kwargs):
        pass


def hits(start, end, box):
    near = 0
    far = 1
    for axis in range(3):
        delta = end[axis] - start[axis]
        if abs(delta) < 1e-10:
            if not box[1][axis] <= start[axis] <= box[2][axis]:
                return False
            continue
        first, last = sorted(((box[1][axis] - start[axis]) / delta,
                              (box[2][axis] - start[axis]) / delta))
        near = max(near, first)
        far = min(far, last)
        if near > far:
            return False
    return True


def legacy_eye(location, size, angle):
    radius = math.hypot(size[0], size[1]) * .9
    target = [location[0], location[1], location[2] + size[2] * .45]
    eye = [target[0] + math.cos(angle) * radius,
           target[1] + math.sin(angle) * radius, target[2] + radius * .35]
    return eye, target


def main():
    scene = Geometry()
    station(scene, -66000, 198000)
    roofs = [box for box in scene.boxes if box[0] == "DistrictTeal"]
    assert min(box[1][2] for box in roofs) == 567.5
    size = (2250.186, 333, 412)
    old_eye, target = legacy_eye((-68000, 198500, 51), size, math.pi / 2)
    assert any(hits(old_eye, target, box) for box in roofs), "Old train view must reproduce roof occlusion"
    checked = 0
    for location, yaw in (((-68000, 198500, 51), 0), ((-64000, 197500, 51), 180)):
        target = [location[0], location[1], location[2] + size[2] * .45]
        views = cameras("PassengerTrain", location, size, yaw)
        assert len(views) == 5
        for view in views:
            assert not any(hits(view["location"], target, box) for box in roofs), view
            checked += 1
    dock = Geometry()
    rowboat_dock(dock)
    boat_size = (417.7498, 181, 88.7)
    old_eye, target = legacy_eye(ROWBOAT, boat_size, math.pi)
    assert any(hits(old_eye, target, box) for box in dock.boxes), "Old boat view must reproduce dock occlusion"
    target = [ROWBOAT[0], ROWBOAT[1], ROWBOAT[2] + boat_size[2] * .45 - 25]
    views = cameras("Rowboat", ROWBOAT, boat_size, 90)
    for view in views:
        assert not any(hits(view["location"], target, box) for box in dock.boxes), view
        checked += 1
    print(f"CITY_PLACEMENT_CAMERA_TEST_OK corrected_views={checked} reproduced_failures=2")


if __name__ == "__main__":
    main()
