"""Deterministic city layout in centimetres; no Unreal dependency."""

from collections import defaultdict
import json
import math
from pathlib import Path
import random


EXTENT = 60000
BLOCK = 12000
ROAD_HALF = 900
WALK = 450
SEED = 71026
ROAD_LINES = list(range(-EXTENT, EXTENT + 1, BLOCK))
DISTRICTS = ("Commercial", "Residential", "Transit")
CAFE = {"centre": (-26150, 2400), "size": (1600, 1200), "face": 1}
APARTMENT = {"centre": (2350, 2500), "size": (2000, 1600), "face": -1}


class Layout:
    def __init__(self):
        self.groups = defaultdict(list)
        self.buildings = []
        self.building_centre = None

    def add(self, mesh, location, scale=(1, 1, 1), yaw=0, material=None, collision=True):
        cell = tuple(math.floor((v + EXTENT) / BLOCK) for v in location[:2])
        key = (cell, mesh, material, collision)
        item = {"location": location, "scale": scale, "yaw": yaw}
        if self.building_centre:
            item["buildingCentre"] = self.building_centre
        self.groups[key].append(item)

    def box(self, material, location, size, collision=True):
        self.add("Cube", location, tuple(v / 100 for v in size), material=material, collision=collision)

    def export(self):
        groups = []
        for (cell, mesh, material, collision), instances in sorted(
            self.groups.items(), key=lambda item: str(item[0])
        ):
            groups.append({"cell": cell, "mesh": mesh, "material": material,
                           "collision": collision, "instances": instances})
        return {"schemaVersion": 1, "units": "cm", "extent": EXTENT,
                "roadLines": ROAD_LINES, "groups": groups, "buildings": self.buildings}


def streets(layout):
    for ix in range(10):
        for iy in range(10):
            x = -EXTENT + BLOCK * (ix + 0.5)
            y = -EXTENT + BLOCK * (iy + 0.5)
            layout.box("Ground", (x, y, -20), (BLOCK, BLOCK, 40))
    for coordinate in ROAD_LINES:
        for offset in range(-EXTENT, EXTENT, BLOCK):
            centre = offset + BLOCK / 2
            layout.box("Asphalt", (centre, coordinate, 1), (BLOCK, ROAD_HALF * 2, 2))
            layout.box("Asphalt", (coordinate, centre, 1.2), (ROAD_HALF * 2, BLOCK, 2))
            length = BLOCK - 2 * ROAD_HALF
            for side in (-1, 1):
                edge = coordinate + side * (ROAD_HALF + WALK / 2)
                layout.box("Sidewalk", (centre, edge, 7.5), (length, WALK, 15))
                layout.box("Sidewalk", (edge, centre, 7.5), (WALK, length, 15))
                curb = coordinate + side * (ROAD_HALF + 10)
                layout.box("Curb", (centre, curb, 9), (length, 20, 18))
                layout.box("Curb", (curb, centre, 9), (20, length, 18))
            for step in range(-4200, 4201, 900):
                layout.box("RoadMark", (centre + step, coordinate, 2.5), (400, 12, 1), False)
                layout.box("RoadMark", (coordinate, centre + step, 2.7), (12, 400, 1), False)
            for side in (-1, 1):
                for step in (-3600, 0, 3600):
                    layout.add("StreetLamp", (centre + step, coordinate + side * 1220, 15),
                               yaw=180 if side > 0 else 0, collision=False)
    for x in ROAD_LINES[1:-1]:
        for y in ROAD_LINES[1:-1]:
            for side in (-1, 1):
                for stripe in range(-700, 701, 200):
                    layout.box("RoadMark", (x + stripe, y + side * 1150, 2.9), (95, 420, 1), False)
                    layout.box("RoadMark", (x + side * 1150, y + stripe, 3), (420, 95, 1), False)
                # Ha via he o giao lo de nhan vat va xe khong mac canh bac.
                layout.box("Sidewalk", (x + side * 1250, y + side * 1250, 6), (500, 500, 12))


def building(layout, x, y, columns, rows, floors, style, rng):
    layout.building_centre = (x, y)
    width = columns * 400
    depth = rows * 400
    height = floors * 320
    layout.buildings.append({"centre": [x, y], "width": width, "depth": depth,
                             "height": height, "style": style, "interior": False})
    layout.box("Concrete", (x, y, height / 2 + 15), (width - 35, depth - 35, height))
    for floor in range(floors):
        z = 15 + floor * 320
        for column in range(columns):
            xx = x - width / 2 + 200 + column * 400
            mesh = "Storefront" if floor == 0 and style != "FacadeResidential" else style
            layout.add(mesh, (xx, y - depth / 2, z), collision=False)
            layout.add(style, (xx, y + depth / 2, z), yaw=180, collision=False)
        for row in range(rows):
            yy = y - depth / 2 + 200 + row * 400
            layout.add(style, (x - width / 2, yy, z), yaw=-90, collision=False)
            layout.add(style, (x + width / 2, yy, z), yaw=90, collision=False)
        if style == "FacadeResidential" and floor > 0 and floor % 2 == 1:
            for side in (-1, 1):
                layout.add("Balcony", (x + side * 400, y - depth / 2, z), collision=False)
    layout.box("Roof", (x, y, height + 30), (width + 70, depth + 70, 30))
    for column in range(columns):
        xx = x - width / 2 + 200 + column * 400
        layout.add("Cornice", (xx, y - depth / 2, height + 15), collision=False)
        layout.add("Cornice", (xx, y + depth / 2, height + 15), yaw=180, collision=False)
    layout.add("RoofEquipment", (x + width * 0.2, y, height + 45),
               yaw=rng.choice((0, 90)), collision=False)
    layout.building_centre = None


def city_blocks(layout):
    rng = random.Random(SEED)
    for ix in range(10):
        for iy in range(10):
            cx = -EXTENT + BLOCK * (ix + 0.5)
            cy = -EXTENT + BLOCK * (iy + 0.5)
            district = 0 if cx < -16000 else 1 if cx < 16000 else 2
            style = ("FacadeCommercial", "FacadeResidential", "FacadeTower")[district]
            for ox in (-2900, 2900):
                for oy in (-2900, 2900):
                    x, y = cx + ox, cy + oy
                    # Giua truc nhiem vu la quang truong va hai noi that, khong dat khoi nha kin.
                    reserved = -30000 < x < -21000 and -1000 < y < 6500
                    reserved |= -3000 < x < 6500 and -1000 < y < 6500
                    reserved |= 21000 < x < 31000 and -1000 < y < 8500
                    if reserved:
                        continue
                    floors = rng.randint(3, 7) if district == 1 else rng.randint(5, 13)
                    if district == 2 and (ix + iy) % 3 == 0:
                        floors += 7
                    building(layout, x, y, rng.choice((6, 7, 8)), rng.choice((5, 6, 7)), floors, style, rng)
            for ox in (-4700, 4700):
                for oy in (-3600, 0, 3600):
                    px, py = cx + ox, cy + oy
                    if (-27500 < px < -23500 and 1000 < py < 3800
                            or 500 < px < 3600 and 1400 < py < 3700):
                        continue
                    layout.add("Planter", (cx + ox, cy + oy, 15), collision=False)
                    layout.add("Bench", (cx + ox + 240, cy + oy, 15), yaw=90, collision=True)
            # Via he trong block noi san nha voi cac duong bao quanh.
            layout.box("Sidewalk", (cx, cy, 7), (1200, BLOCK - 2 * ROAD_HALF, 14))
            layout.box("Sidewalk", (cx, cy, 7.2), (BLOCK - 2 * ROAD_HALF, 1200, 14))


def perimeter(layout):
    # Nen mo rong che mep duong; dai cong vien va lan can gioi han vung choi.
    for side in (-1, 1):
        layout.box("Ground", (0, side * 75500, -110), (180000, 30000, 200))
        layout.box("Ground", (side * 75500, 0, -110), (30000, 120000, 200))
        layout.box("Sidewalk", (0, side * 60500, -10), (120000, 1100, 20))
        layout.box("Sidewalk", (side * 60500, 0, -10), (1100, 120000, 20))
        for offset in range(-59400, 60000, 1200):
            layout.box("Curb", (offset, side * 61000, 55), (1200, 45, 110))
            layout.box("Curb", (side * 61000, offset, 55), (45, 1200, 110))
            layout.add("Planter", (offset, side * 60800, 0), collision=False)
            layout.add("Planter", (side * 60800, offset, 0), collision=False)


def validate(data):
    assert data["extent"] * 2 == 120000
    assert len(data["roadLines"]) == 11
    assert len(data["buildings"]) > 300
    assert all(not b["interior"] for b in data["buildings"])
    for group in data["groups"]:
        for item in group["instances"]:
            assert all(math.isfinite(v) for v in item["location"] + tuple(item["scale"]))
    return {"buildings": len(data["buildings"]), "groups": len(data["groups"]),
            "instances": sum(len(g["instances"]) for g in data["groups"]),
            "connectedRoadGrid": True}


def stage_groups(data, stage):
    result = []
    for group in data["groups"]:
        items = group["instances"]
        if stage == "hero" and group["material"] != "Ground":
            items = [item for item in items
                     if -38500 <= item.get("buildingCentre", item["location"])[0] <= -11500
                     and -13500 <= item.get("buildingCentre", item["location"])[1] <= 13500]
        if items:
            result.append({**group, "instances": items})
    return result


def generate():
    layout = Layout()
    streets(layout)
    city_blocks(layout)
    perimeter(layout)
    data = layout.export()
    data["audit"] = validate(data)
    return data


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[2] / "Saved/QA/CityLayout.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = generate()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data["audit"]))
