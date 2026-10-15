"""Check new furniture bounds against room walls, clear access lanes, and existing seating."""

import json
import math
from pathlib import Path

from CityBarSeating import generate as bar_seating
from CityCivicDressing import generate as arcade_dressing
from CityCivicDistrict import FLOOR_Z, SITES, access_lanes
from CityLayout import Layout

PROJECT = Path(__file__).resolve().parents[2]


def bounds_for(item, bounds):
    minimum = bounds["minimum"]
    maximum = bounds["maximum"]
    angle = math.radians(item["yaw"])
    cosine = math.cos(angle)
    sine = math.sin(angle)
    x, y, z = item["location"]
    corners = [(x + xx * cosine - yy * sine, y + xx * sine + yy * cosine)
               for xx in (minimum[0], maximum[0]) for yy in (minimum[1], maximum[1])]
    return (min(point[0] for point in corners), min(point[1] for point in corners), z + minimum[2],
            max(point[0] for point in corners), max(point[1] for point in corners), z + maximum[2])


def intersects(first, second):
    return all(min(first[axis + 3], second[axis + 3]) - max(first[axis], second[axis]) > 0.1
               for axis in range(3))


def main():
    mesh_bounds = json.loads((PROJECT / "Saved/QA/CityCivicMeshBounds.json").read_text())["meshes"]
    layout = Layout()
    arcade_dressing(layout)
    bar_seating(layout)
    groups = layout.export()["groups"]
    colliders = []
    errors = []
    lanes = access_lanes()
    for group in groups:
        if not group["collision"]:
            continue
        bounds = mesh_bounds[group["mesh"]]
        assert bounds["available"]
        for item in group["instances"]:
            box = bounds_for(item, bounds)
            colliders.append((group["mesh"], box))
            site = "Arcade" if group["mesh"] == "ArcadeCabinet" else "Bar"
            _, x, y, _, _ = next(entry for entry in SITES if entry[0] == site)
            if box[0] < x + 1817.5 or box[3] > x + 5182.5:
                errors.append(f"Outside room x: {group['mesh']} {box}")
            if box[1] < y - 1782.5 or box[4] > y + 1782.5:
                errors.append(f"Outside room y: {group['mesh']} {box}")
            for name, lower, upper in lanes:
                expanded = (lower[0] - 38, lower[1] - 38, lower[2],
                            upper[0] + 38, upper[1] + 38, upper[2])
                if intersects(box, expanded):
                    errors.append(f"Blocks {name} lane plus capsule radius: {group['mesh']}")
    for index, (mesh, box) in enumerate(colliders):
        for other_mesh, other_box in colliders[index + 1:]:
            if intersects(box, other_box):
                errors.append(f"New furniture overlap: {mesh} / {other_mesh}")
    _, x, y, _, _ = next(entry for entry in SITES if entry[0] == "Bar")
    existing = Layout()
    for xx in (2800, 3250, 3700):
        existing.add("CafeCounter", (x + xx, y + 1300, FLOOR_Z))
    for xx in (2600, 3550, 4400):
        existing.add("CafeTable", (x + xx, y - 1050, FLOOR_Z))
        for yy in (-1300, -800):
            existing.add("House_dining_chair_02", (x + xx, y + yy, FLOOR_Z))
    for group in existing.export()["groups"]:
        for item in group["instances"]:
            old_box = bounds_for(item, mesh_bounds[group["mesh"]])
            for mesh, box in colliders:
                if intersects(box, old_box):
                    errors.append(f"Overlaps existing seating: {mesh} / {group['mesh']}")
    report = dict(writtenGroups=len(groups), instances=sum(len(group["instances"]) for group in groups),
                  colliders=len(colliders), capsuleRadiusCm=38, errors=errors,
                  checks=["room containment", "access lanes with capsule radius", "new pairwise overlap",
                          "existing cafe seating overlap"],
                  limitations=["living appliances retained in place", "runtime physics and images pending"])
    (PROJECT / "Saved/QA/CityCivicDressingLayout.json").write_text(json.dumps(report, indent=2))
    assert not errors, "\n".join(errors)
    print("CITY_CIVIC_DRESSING_LAYOUT_OK " + json.dumps(report))


if __name__ == "__main__":
    main()
