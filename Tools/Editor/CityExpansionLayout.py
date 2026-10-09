"""Dense city expansion using instanced geometry and reserved accessible venues."""

from collections import defaultdict
import json
import math
from pathlib import Path
import random

from CityExpansionData import BLOCK, GRID_EXTENT, GRID_BLOCKS, WORLD_EXTENT, ROAD_LINES, SEED
from CityExpansionData import overlaps_reserved, coastal_cutout
from CityExpansionBuildings import building, STYLES
from CityExpansionLandscape import dress_block, perimeter


class Layout:
    def __init__(self):
        self.groups = defaultdict(list)
        self.buildings = []
        self.building_centre = None

    def add(self, mesh, location, scale=(1, 1, 1), yaw=0, material=None, collision=True, hidden=False):
        cell = tuple(math.floor((v + GRID_EXTENT) / BLOCK) for v in location[:2])
        item = dict(location=location, scale=scale, yaw=yaw)
        if self.building_centre:
            item["buildingCentre"] = self.building_centre
        self.groups[(cell, mesh, material, collision, hidden)].append(item)

    def box(self, material, location, size, collision=True):
        self.add("Cube", location, tuple(v / 100 for v in size), material=material, collision=collision)

    def collider(self, location, size, yaw=0):
        self.add("Cube", location, tuple(v / 100 for v in size), yaw=yaw, collision=True, hidden=True)

    def export(self):
        groups = []
        for (cell, mesh, material, collision, hidden), instances in sorted(self.groups.items(), key=lambda x: str(x[0])):
            origin = [-GRID_EXTENT + (cell[i] + 0.5) * BLOCK for i in range(2)] + [0]
            groups.append(dict(cell=cell, origin=origin, mesh=mesh, material=material,
                               collision=collision, hidden=hidden, instances=instances))
        return dict(schemaVersion=2, units="cm", extent=WORLD_EXTENT, roadLines=ROAD_LINES,
                    groups=groups, buildings=self.buildings)


def streets(layout):
    for ix in range(GRID_BLOCKS):
        for iy in range(GRID_BLOCKS):
            x, y = (-GRID_EXTENT + BLOCK * (v + 0.5) for v in (ix, iy))
            if not coastal_cutout(x, y):
                layout.box("Ground", (x, y, -20), (BLOCK, BLOCK, 40))
    for road in ROAD_LINES:
        for start in range(-GRID_EXTENT, GRID_EXTENT, BLOCK):
            centre = start + BLOCK / 2
            for vertical in (False, True):
                def xyz(along, across, z):
                    return (across, along, z) if vertical else (along, across, z)
                def size(along, across, z):
                    return (across, along, z) if vertical else (along, across, z)
                sample = xyz(centre, road, 0)
                if coastal_cutout(sample[0], sample[1]):
                    continue
                layout.box("Asphalt", xyz(centre, road, 1), size(BLOCK, 1800, 2))
                for side in (-1, 1):
                    layout.box("Sidewalk", xyz(centre, road + side * 1125, 7.5), size(10200, 450, 15))
                    layout.box("Curb", xyz(centre, road + side * 910, 9), size(10200, 20, 18))
                    if not vertical:
                        for step in (-3600, 0, 3600):
                            layout.add("DetailedStreetLamp", xyz(centre + step, road + side * 1220, 15),
                                       yaw=180 if side > 0 else 0, collision=False)
                            layout.collider(xyz(centre + step, road + side * 1220, 205), (32, 32, 380))
                for step in range(-4200, 4201, 900):
                    layout.box("RoadMark", xyz(centre + step, road, 2.5), size(400, 12, 1), False)
    for x in ROAD_LINES[1:-1]:
        for y in ROAD_LINES[1:-1]:
            if coastal_cutout(x, y):
                continue
            for side in (-1, 1):
                for stripe in range(-700, 701, 200):
                    layout.box("RoadMark", (x + stripe, y + side * 1150, 2.9), (95, 420, 1), False)
                    layout.box("RoadMark", (x + side * 1150, y + stripe, 3), (420, 95, 1), False)
                layout.box("Sidewalk", (x + side * 1250, y + side * 1250, 6), (500, 500, 12))
            if x % 24000 == 0 and y % 24000 == 0:
                for side in (-1, 1):
                    location = (x + side * 1310, y - side * 1310, 15)
                    layout.add("TrafficSignal", location, yaw=0 if side > 0 else 180, collision=False)
                    layout.collider((location[0], location[1], 215), (30, 30, 400))


def city_blocks(layout):
    # Mot hat giong rieng moi o giup ket qua on dinh khi mo rong vung bien.
    for ix in range(GRID_BLOCKS):
        for iy in range(GRID_BLOCKS):
            cx, cy = (-GRID_EXTENT + BLOCK * (v + 0.5) for v in (ix, iy))
            if coastal_cutout(cx, cy):
                continue
            rng = random.Random(SEED + int(cx) * 31 + int(cy))
            district = 0 if cx < -20000 else 1 if cx < 20000 else 2
            outer = max(abs(cx), abs(cy)) > 84000
            park = (int(cx // BLOCK) * 7 + int(cy // BLOCK) * 3) % 13 == 0 and abs(cy) > 12000
            if not park:
                for ox, oy in ((-3100, -3100), (0, -3100), (3100, -3100),
                               (-3100, 0), (3100, 0), (-3100, 3100), (0, 3100), (3100, 3100)):
                    if outer and (ox == 0 or oy == 0):
                        continue
                    columns = rng.choice((4, 5, 6))
                    rows = rng.choice((4, 5, 6))
                    x, y = cx + ox + rng.choice((-100, 0, 100)), cy + oy + rng.choice((-100, 0, 100))
                    if overlaps_reserved(x, y, columns * 400, rows * 400, 200):
                        continue
                    styles = ((1, 3, 5, 6), (0, 3, 4, 5), (1, 2, 5, 6))[district]
                    style = STYLES[rng.choice(styles)]
                    floors = rng.randint(3, 9) if district == 1 else rng.randint(4, 15)
                    if outer:
                        floors = rng.randint(2, 7)
                    if district == 2 and (ix + iy) % 4 == 0:
                        floors += 8
                    building(layout, x, y, columns, rows, floors, style, rng)
            if not overlaps_reserved(cx, cy, 9000, 9000):
                dress_block(layout, cx, cy, rng, park)


def generate():
    layout = Layout()
    streets(layout)
    city_blocks(layout)
    perimeter(layout)
    from CityCivicDistrict import generate as civic
    from CityCoastalDistrict import generate as coast
    civic(layout)
    coast(layout)
    data = layout.export()
    data["audit"] = dict(buildings=len(data["buildings"]), groups=len(data["groups"]),
                         instances=sum(len(g["instances"]) for g in data["groups"]),
                         widthMetres=WORLD_EXTENT * 2 / 100, areaRatio=(WORLD_EXTENT / 60000) ** 2,
                         previousAreaRatio=(WORLD_EXTENT / (60000 * math.sqrt(2))) ** 2,
                         roadBlocks=GRID_BLOCKS ** 2, shellOnly=True,
                         styles=sorted(set(b["style"] for b in data["buildings"])))
    return data


if __name__ == "__main__":
    data = generate()
    path = Path(__file__).resolve().parents[2] / "Saved/QA/CityExpansionLayout.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    print(json.dumps(data["audit"]))
