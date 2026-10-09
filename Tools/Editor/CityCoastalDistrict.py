"""Beach, working harbour and west-side piers matched to the three vessel stops."""

import json
from pathlib import Path


RESERVES = ((120000, -168000, 168000, -120000),)
WATER_RECT = (128000, -146000, 168000, -120000)
WATER_LEVEL = -120
SEABED_LEVEL = -1600
DOCK_Y = -141000
DOCKS = (("CargoShip", 131000, 305), ("Motorboat", 135200, 117.5), ("Sailboat", 139400, 135))
PIER_WIDTH = 420
QUAY_Y = -146000


def ocean_rectangles():
    from CityExpansionData import WORLD_EXTENT

    horizon = WORLD_EXTENT + 2000000
    return (WATER_RECT, (168000, -horizon, horizon, -120000),
            (120000, -horizon, 168000, -168000))


def vessel_half_width(name, fallback):
    path = Path(__file__).resolve().parents[2] / "Assets/City/mobility_manifest.json"
    if path.exists():
        item = next(item for item in json.loads(path.read_text(encoding="utf-8"))["meshes"] if item["id"] == name)
        return item["boundsCm"]["size"][1] / 2
    return fallback


def piers():
    result = []
    for name, x, fallback in DOCKS:
        half_width = vessel_half_width(name, fallback)
        # Me ben cach hull 20 cm; capsule cua tai +65 cm nam tron tren mat ben.
        edge = x - half_width - 20
        result.append(dict(id=name, x=x, halfWidth=half_width, edge=edge,
                           centre=edge - PIER_WIDTH / 2, doorX=x - half_width - 65,
                           sidewalkX=x - half_width - 320))
    return result


def rail(layout, x, y, length, axis="x"):
    size = (length, 12, 12) if axis == "x" else (12, length, 12)
    for z in (65, 120):
        layout.box("DistrictSteel", (x, y, z), size)
    count = max(1, int(length / 180))
    for index in range(count + 1):
        offset = -length / 2 + length * index / count
        xx, yy = (x + offset, y) if axis == "x" else (x, y + offset)
        layout.box("DistrictSteel", (xx, yy, 65), (12, 12, 100))


def pier(layout, dock):
    cx, edge = dock["centre"], dock["edge"]
    north = DOCK_Y + 650
    length = north - QUAY_Y
    cy = (QUAY_Y + north) / 2
    layout.box("DistrictTimber", (cx, cy, -10), (PIER_WIDTH, length, 50))
    layout.box("DistrictYellow", (edge - 6, cy, 16), (12, length, 2), False)
    layout.box("DistrictSteel", (cx, cy, -80), (PIER_WIDTH - 40, length, 40))
    for y in range(QUAY_Y + 300, north, 650):
        for xx in (edge - 55, edge - PIER_WIDTH + 55):
            layout.box("DistrictTimber", (xx, y, -810), (30, 30, 1570))
        layout.add("HarborBollard", (edge - PIER_WIDTH + 40, y, 15))
    # Cua cap ben de trong 600 cm ca hai phia, du cho doi huong capsule.
    for start, end in ((QUAY_Y, DOCK_Y - 500), (DOCK_Y + 500, north)):
        rail(layout, edge - 14, (start + end) / 2, end - start, "y")
    rail(layout, edge - PIER_WIDTH + 14, cy, length, "y")
    rail(layout, cx, north - 14, PIER_WIDTH - 28)
    layout.add("BusStopSign", (cx - 75, DOCK_Y + 440, 15), yaw=90)


def container(layout, x, y, z, color):
    layout.box(color, (x, y, z + 130), (1200, 244, 260))
    for side in (-1, 1):
        for offset in range(-560, 561, 80):
            layout.box("DistrictSteel", (x + offset, y + side * 124, z + 130), (12, 8, 230), False)
        layout.box("DistrictSteel", (x + side * 585, y, z + 265), (25, 250, 18))
        for yy in (-62, 62):
            layout.box("DistrictSteel", (x + side * 603, y + yy, z + 130), (8, 8, 230), False)
    for xx in (-560, 560):
        for yy in (-110, 110):
            layout.box("DistrictLimestone", (x + xx, y + yy, z + 260), (40, 30, 20))


def cargo_yard(layout):
    layout.box("DistrictPaving", (147000, -157000, 7.5), (35000, 18000, 15))
    for row in range(5):
        for column in range(7):
            x, y = 134000 + column * 4200, -152000 - row * 2400
            color = "DistrictContainerRed" if (row + column) % 2 else "DistrictContainerBlue"
            for tier in range(1 + (row + column) % 3):
                container(layout, x, y, 15 + tier * 280, color)
    for x in (138000, 155000):
        for yy in (-151000, -160000):
            for dx in (-1700, 1700):
                layout.box("DistrictYellow", (x + dx, yy, 1115), (180, 180, 2200))
                layout.box("DistrictSteel", (x + dx, yy, 115), (400, 360, 200))
        for dx in (-1700, 1700):
            layout.box("DistrictYellow", (x + dx, -155500, 2265), (220, 9500, 260))
        layout.box("DistrictYellow", (x, -155500, 2420), (3700, 450, 220))
        layout.box("DistrictSteel", (x, -155500, 2230), (500, 700, 180))
        for dx in (-170, 170):
            layout.box("DistrictSteel", (x + dx, -155500, 1670), (12, 12, 950), False)
        layout.box("DistrictYellow", (x, -155500, 1160), (900, 280, 100))
    for x in range(130000, 166001, 2400):
        layout.add("DetailedStreetLamp", (x, -147500, 15), yaw=90)
        layout.add("RoadBarrier", (x, -166000, 15))
        layout.box("RoadMark", (x, -149000, 16), (1000, 18, 2), False)


def beach(layout):
    layout.box("DistrictPaving", (122000, -133000, 7.5), (4000, 26000, 15))
    for index, top in enumerate((15, -25, -70, -115)):
        layout.box("DistrictSand", (124500 + index * 1000, -133000, (top - 1600) / 2),
                   (1000, 26000, top + 1600))
    for y in range(-143500, -121499, 2000):
        layout.add("DetailedStreetLamp", (123600, y, 15), yaw=0)
        layout.add("Bench", (123300, y + 500, 15), yaw=90)
        layout.add("DetailedPlanter", (123650, y + 900, 15))
        layout.add("House_mid_century_lounge_chair", (125000, y, 15), yaw=-90)
        layout.add("House_mid_century_lounge_chair", (125000, y + 300, 15), yaw=-90)
        layout.box("DistrictTimber", (124800, y + 150, 130), (18, 18, 230))
        layout.box("DistrictTeal", (124800, y + 150, 270), (500, 600, 28))
    for x in (121400, 122600):
        layout.add("MarketStall", (x, -140000, 15), yaw=90)


def generate(layout):
    # Nuoc chi de hien thi; chi day bien va cau ben co collision vat ly.
    for left, bottom, right, top in ocean_rectangles():
        location = ((left + right) / 2, (bottom + top) / 2)
        size = (right - left, top - bottom)
        layout.box("DistrictWater", (*location, WATER_LEVEL - 5), (*size, 10), False)
        layout.box("DistrictSand", (*location, SEABED_LEVEL - 20), (*size, 40))
    layout.box("DistrictPaving", (144000, -157000, -20), (48000, 22000, 70))
    beach(layout)
    cargo_yard(layout)
    for dock in piers():
        pier(layout, dock)
    for x in range(143000, 168000, 600):
        layout.add("HarborBollard", (x, QUAY_Y - 150, 15))
    rail(layout, 153500, QUAY_Y - 20, 27500)
