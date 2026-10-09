"""Walkable courtyards, pocket gardens and street amenities, grouped as instances."""

from CityExpansionData import BLOCK, GRID_EXTENT, WORLD_EXTENT, overlaps_reserved, coastal_cutout


def prop(layout, mesh, x, y, yaw=0, scale=(1, 1, 1), radius=230):
    if not overlaps_reserved(x, y, radius * 2, radius * 2):
        mesh = "DetailedPlanter" if mesh == "Planter" else mesh
        solid = mesh in ("DetailedPlanter", "Bench", "TrashBin", "MarketStall")
        layout.add(mesh, (x, y, 15), scale, yaw, collision=solid)
        if mesh.startswith("Tree"):
            layout.collider((x, y, 185 * scale[2]), (32 * scale[0], 32 * scale[1], 340 * scale[2]))


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
    # Cat dai dat o bo dong va nam: bien phai thong ra chan troi.
    reach = WORLD_EXTENT - GRID_EXTENT
    end = -120000
    land_length = GRID_EXTENT - end
    land_centre = (GRID_EXTENT + end) / 2
    layout.box("Ground", (0, GRID_EXTENT + reach / 2, -60),
               (WORLD_EXTENT * 2, reach, 100))
    layout.box("Ground", (-GRID_EXTENT - reach / 2, 0, -60),
               (reach, WORLD_EXTENT * 2, 100))
    layout.box("Ground", (-land_centre, -GRID_EXTENT - reach / 2, -60),
               (land_length, reach, 100))
    layout.box("Ground", (GRID_EXTENT + reach / 2, land_centre, -60),
               (reach, land_length, 100))
    for side in (-1, 1):
        for offset in range(-GRID_EXTENT, GRID_EXTENT, 1200):
            for vertical in (False, True):
                x, y = (side * edge, offset + 600) if vertical else (offset + 600, side * edge)
                if coastal_cutout(x, y):
                    continue
                size = (35, 1200, 140) if vertical else (1200, 35, 140)
                layout.box("Curb", (x, y, 70), size)
                if offset % 2400 == 0:
                    layout.add("TreeColumnar", (x, y, -10), collision=False)
        # Mat trong cua collider trung dung ranh gioi choi, ke ca tren bien.
        layout.collider((0, side * (WORLD_EXTENT + 50), 15000),
                        (WORLD_EXTENT * 2 + 200, 100, 40000))
        layout.collider((side * (WORLD_EXTENT + 50), 0, 15000),
                        (100, WORLD_EXTENT * 2 + 200, 40000))
