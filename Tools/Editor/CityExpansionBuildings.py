"""Seeded shell architecture: no hidden furnished floors in background buildings."""

STYLES = ("FacadeResidential", "FacadeCommercial", "FacadeTower", "FacadeBrickArch",
          "FacadeBay", "FacadeArtDeco", "FacadeIndustrial", "FacadeCivic")
TINTS = ("ShellIvory", "ShellTerracotta", "ShellSage", "ShellSlate", "ShellSand", "ShellBlue")

# Quy tac vat lieu va diem nhan nhe cho tung phong cach, dung chung mesh de giu instancing.
STYLE_QUALITY = {
    "FacadeResidential": dict(accent="City_oak_veneer_01", vertical=True, balcony=True),
    "FacadeCommercial": dict(accent="City_Brass", vertical=True, balcony=False),
    "FacadeTower": dict(accent="City_Aluminium", vertical=True, balcony=False),
    "FacadeBrickArch": dict(accent="City_stone_wall_02", vertical=False, balcony=False),
    "FacadeBay": dict(accent="City_oak_veneer_01", vertical=True, balcony=True),
    "FacadeArtDeco": dict(accent="City_Brass", vertical=True, balcony=False),
    "FacadeIndustrial": dict(accent="City_Dark", vertical=False, balcony=False),
    "FacadeCivic": dict(accent="City_Brass", vertical=True, balcony=False),
}

DISTRICT_PROFILES = {
    "west": dict(forms=("slab", "terrace", "pavilion", "lantern")),
    "core": dict(forms=("stepped", "corner", "twin", "crown", "lantern")),
    "east": dict(forms=("slab", "stepped", "twin", "crown", "pavilion")),
}


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


def building(layout, x, y, columns, rows, floors, style, rng, district="core"):
    width, depth = columns * 400, rows * 400
    tint = rng.choice(TINTS)
    quality = STYLE_QUALITY[style]
    district_profile = DISTRICT_PROFILES.get(district, DISTRICT_PROFILES["core"])
    form = rng.choice(district_profile["forms"])
    layout.building_centre = (x, y)
    layout.buildings.append(dict(centre=[x, y], width=width, depth=depth, height=floors * 320,
                                 style=style, tint=tint, form=form, interior=False, district=district,
                                 quality=dict(profile=style, accent=quality["accent"],
                                              vertical=quality["vertical"],
                                              balcony=quality["balcony"])))
    lower = min(floors, rng.choice((2, 3, 4))) if form != "slab" else floors
    floor_band(layout, x, y, columns, rows, 0, lower, style, tint, podium=True)
    top_x, top_y = x, y
    top_columns, top_rows = columns, rows
    if floors > lower and form == "twin" and columns >= 5:
        tower_columns = max(2, (columns - 1) // 2)
        for side in (-1, 1):
            offset = side * (width / 2 - tower_columns * 200)
            floor_band(layout, x + offset, y, tower_columns, max(2, rows - 1), lower,
                       floors - lower, style, tint)
    elif floors > lower:
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
    if quality["balcony"]:
        for floor in range(1, floors, 2):
            layout.add("Balcony", (top_x, top_y - top_rows * 200, floor * 320 + 15), collision=False)
    layout.add("RoofEquipment", (top_x, top_y, floors * 320 + 45),
               yaw=rng.choice((0, 90, 180, 270)), collision=False)
    trim = rng.choice(tuple(name for name in TINTS if name != tint))
    if form in ("crown", "lantern"):
        crown_z = floors * 320 + 160
        layout.box(trim, (top_x, top_y, crown_z), (width * .55, depth * .55, 250), False)
        for offset in (-.28, .28):
            layout.box("City_Brass", (top_x + width * offset, top_y, crown_z + 180),
                       (28, depth * .6, 120), False)
    elif form == "pavilion":
        for step in range(4):
            layout.box("Roof", (top_x, top_y, floors * 320 + 45 + step * 55),
                       (width * (1 - step * .18), depth + 80, 65), False)
    # Nhip cot, bien mai va chan de thay doi theo tung toa; van chi la vo nha.
    if quality["vertical"]:
        for offset in (-.46, .46):
            layout.box(quality["accent"], (x + width * offset, y - depth / 2 - 12, lower * 160 + 15),
                       (60, 40, lower * 320), False)
    if rng.random() < .55:
        for offset in (-.3, .3):
            layout.box(trim, (x + width * offset, y - depth / 2 - 25, 360),
                       (width * .26, 30, 70), False)
    # Cot va mai hien tao nhip doc pho ma khong them noi that vao vo nha.
    if floors < 9:
        layout.box(tint, (x, y - depth / 2 - 100, 300), (width + 40, 220, 24), False)
    layout.building_centre = None
