"""Seeded shell architecture: no hidden furnished floors in background buildings."""

STYLES = ("FacadeResidential", "FacadeCommercial", "FacadeTower", "FacadeBrickArch",
          "FacadeBay", "FacadeArtDeco", "FacadeIndustrial")
TINTS = ("ShellIvory", "ShellTerracotta", "ShellSage", "ShellSlate", "ShellSand", "ShellBlue")


def floor_band(layout, x, y, columns, rows, first, count, style, tint, podium=False):
    width, depth = columns * 400, rows * 400
    height = count * 320
    base = first * 320 + 15
    layout.box(tint, (x, y, base + height / 2), (width - 32, depth - 32, height))
    for floor in range(first, first + count):
        z = 15 + floor * 320
        variant = f"V_{style}_{tint}" if style != "FacadeTower" else None
        for column in range(columns):
            xx = x - width / 2 + 200 + column * 400
            front = "Storefront" if floor == 0 and podium else style
            layout.add(front, (xx, y - depth / 2, z), material=variant if front == style else None, collision=False)
            layout.add(style, (xx, y + depth / 2, z), yaw=180, material=variant, collision=False)
        for row in range(rows):
            yy = y - depth / 2 + 200 + row * 400
            layout.add(style, (x - width / 2, yy, z), yaw=-90, material=variant, collision=False)
            layout.add(style, (x + width / 2, yy, z), yaw=90, material=variant, collision=False)
        if floor % 3 == 2:
            layout.box(tint, (x, y, z + 312), (width + 36, depth + 36, 18), False)
    roof = (first + count) * 320 + 30
    layout.box("Roof", (x, y, roof), (width + 50, depth + 50, 30))
    for side in (-1, 1):
        layout.box(tint, (x, y + side * depth / 2, roof + 40), (width + 30, 22, 80), False)
        layout.box(tint, (x + side * width / 2, y, roof + 40), (22, depth + 30, 80), False)
    return roof


def building(layout, x, y, columns, rows, floors, style, rng):
    width, depth = columns * 400, rows * 400
    tint = rng.choice(TINTS)
    form = rng.choice(("slab", "stepped", "corner", "terrace"))
    layout.building_centre = (x, y)
    layout.buildings.append(dict(centre=[x, y], width=width, depth=depth, height=floors * 320,
                                 style=style, tint=tint, form=form, interior=False))
    lower = min(floors, rng.choice((2, 3, 4))) if form != "slab" else floors
    floor_band(layout, x, y, columns, rows, 0, lower, style, tint, podium=True)
    top_x, top_y = x, y
    top_columns, top_rows = columns, rows
    if floors > lower:
        top_columns = max(2, columns - (2 if form == "terrace" else 1))
        top_rows = max(2, rows - 1)
        if form == "corner":
            top_x += 200
            top_y += 200
        top_style = rng.choice((style, "FacadeTower")) if form == "stepped" else style
        floor_band(layout, top_x, top_y, top_columns, top_rows, lower, floors - lower,
                   top_style, tint)
        for side in (-1, 1):
            layout.add("Planter", (x + side * (width / 2 - 150), y, lower * 320 + 45),
                       collision=False)
    if style in ("FacadeResidential", "FacadeBay"):
        for floor in range(1, floors, 2):
            layout.add("Balcony", (top_x, top_y - top_rows * 200, floor * 320 + 15), collision=False)
    layout.add("RoofEquipment", (top_x, top_y, floors * 320 + 45),
               yaw=rng.choice((0, 90, 180, 270)), collision=False)
    # Cot va mai hien tao nhip doc pho ma khong them noi that vao vo nha.
    if floors < 9:
        layout.box(tint, (x, y - depth / 2 - 100, 300), (width + 40, 220, 24), False)
    layout.building_centre = None
