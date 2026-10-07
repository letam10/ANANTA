"""Walkable courtyards, pocket gardens and street amenities, grouped as instances."""

from CityExpansionData import BLOCK, GRID_EXTENT, WORLD_EXTENT, overlaps_reserved


def prop(layout, mesh, x, y, yaw=0, scale=(1, 1, 1), radius=230):
    if not overlaps_reserved(x, y, radius * 2, radius * 2):
        layout.add(mesh, (x, y, 15), scale, yaw, collision=False)


def dress_block(layout, x, y, rng, park):
    # Cac loai vat dung nam trong san, de trong dai via he lien tuc 450 cm.
    layout.box("Sidewalk", (x, y, 6), (1900, 1900, 12))
    for dx, dy in ((-4550, -4550), (-4550, 4550), (4550, -4550), (4550, 4550)):
        scale = rng.uniform(0.75, 1.2)
        prop(layout, rng.choice(("TreeBroadleaf", "TreeColumnar")), x + dx, y + dy,
             rng.uniform(0, 360), (scale, scale, scale), radius=260)
        prop(layout, "Planter", x + dx, y + dy, radius=200)
    for side in (-1, 1):
        for step in (-1800, 1800):
            prop(layout, "TreeColumnar", x + side * 4510, y + step, radius=130)
        prop(layout, "Bench", x + side * 750, y, yaw=90 * side, radius=180)
        prop(layout, "TrashBin", x + side * 700, y + 450, radius=75)
    prop(layout, "BikeRack", x - 4300, y + 600, yaw=90, radius=150)
    prop(layout, "StreetSign", x - 4480, y - 4500, radius=40)
    if park:
        layout.box("GardenSoil", (x, y, 4), (7800, 7800, 8), False)
        layout.box("Sidewalk", (x, y, 6), (1400, 9600, 12))
        layout.box("Sidewalk", (x, y, 6), (9600, 1400, 12))
        for dx in (-2900, -1600, 1600, 2900):
            for dy in (-2800, -1400, 1400, 2800):
                scale = rng.uniform(0.7, 1.15)
                prop(layout, "TreeBroadleaf", x + dx, y + dy, rng.uniform(0, 360),
                     (scale, scale, scale), radius=260)
        for side in (-1, 1):
            prop(layout, "BusShelter", x + side * 1900, y - 4450, radius=300)
    elif rng.random() < 0.32:
        prop(layout, "MarketStall", x, y - 650, radius=280)
    if rng.random() < 0.28:
        prop(layout, "BusShelter", x + 4500, y, yaw=90, radius=270)
    # Bon hoa hep nam ngoai mat tien nha, khong dat va cham trong long duong.
    for side in (-1, 1):
        for step in (-2200, 2100):
            prop(layout, "Planter", x + step, y + side * 4510, radius=140)


def perimeter(layout):
    edge = GRID_EXTENT + 1450
    for side in (-1, 1):
        layout.box("Ground", (0, side * (GRID_EXTENT + 8000), -60),
                   (2 * GRID_EXTENT + 32000, 16000, 100))
        layout.box("Ground", (side * (GRID_EXTENT + 8000), 0, -60),
                   (16000, 2 * GRID_EXTENT, 100))
        layout.box("Sidewalk", (0, side * (GRID_EXTENT + 1125), 5), (2 * GRID_EXTENT, 450, 10))
        layout.box("Sidewalk", (side * (GRID_EXTENT + 1125), 0, 5), (450, 2 * GRID_EXTENT, 10))
        for offset in range(-GRID_EXTENT, GRID_EXTENT, 1200):
            layout.box("Curb", (offset + 600, side * edge, 70), (1200, 35, 140))
            layout.box("Curb", (side * edge, offset + 600, 70), (35, 1200, 140))
            if offset % 2400 == 0:
                layout.add("TreeColumnar", (offset, side * (edge + 300), -10), collision=False)
                layout.add("TreeColumnar", (side * (edge + 300), offset, -10), collision=False)
