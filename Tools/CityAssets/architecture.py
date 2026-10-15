"""Four metre facade bays with actual recesses, framing and open entry modules."""
from geometry import box, cylinder, combine


def window(x, z, width=1.48, height=1.92):
    box("Recess shadow", (x, 0.015, z), (width + 0.1, 0.09, height + 0.1), "Dark")
    box("Glazing", (x, -0.052, z), (width, 0.035, height), "Glass")
    for side in [-1, 1]:
        box("Window jamb", (x + side * width / 2, -0.10, z), (0.055, 0.14, height + 0.10), "Aluminium")
        box("Window rail", (x, -0.10, z + side * height / 2), (width + 0.08, 0.14, 0.06), "Aluminium")
    box("Window mullion", (x, -0.13, z), (0.035, 0.08, height), "Aluminium")
    box("Window transom", (x, -0.14, z + height * 0.22), (width, 0.08, 0.045), "Aluminium")
    box("Sill stone", (x, -0.17, z - height / 2 - 0.06), (width + 0.22, 0.38, 0.10), "Stone")
    box("Blind top", (x, -0.07, z + height * 0.39), (width - 0.06, 0.03, height * 0.18), "Linen")


def facade(kind):
    wall = "Brick" if kind == "Residential" else "Plaster"
    if kind == "Tower":
        for i in range(4):
            x = -1.5 + i
            box("Curtain glass", (x, 0.04, 1.62), (0.93, 0.06, 2.73), "Glass")
            box("Opaque spandrel", (x, 0.07, 0.15), (0.95, 0.16, 0.30), "Dark")
        for x in [-1.9775, -1, 0, 1, 1.9775]:
            box("Vertical fin", (x, -0.10, 1.60), (0.045, 0.40, 3.2), "Aluminium")
        for z in [0.03, 0.31, 1.2, 3.17]:
            box("Tower transom", (0, -0.055, z), (4, 0.19, 0.055), "Aluminium")
    else:
        for x in [-1.91, 0, 1.91]:
            width = 0.18 if x else 0.28
            box("Masonry pier", (x, 0.13, 1.60), (width, 0.32, 3.2), wall)
        for z, height in [(0.38, 0.76), (2.98, 0.44)]:
            box("Masonry spandrel", (0, 0.13, z), (4, 0.32, height), wall)
        for x in [-0.98, 0.98]:
            window(x, 1.77, 1.60, 1.92)
            box("Lintel", (x, -0.11, 2.81), (1.83, 0.26, 0.12), "Stone")
        box("Floor stringcourse", (0, -0.05, 0.08), (4, 0.43, 0.16), "Stone")
        if kind == "Commercial":
            for x in [-1.83, 0, 1.83]:
                box("Stone pilaster", (x, -0.06, 1.62), (0.12, 0.19, 2.92), "Stone")
    return combine("Facade" + kind)


def storefront(identifier="Storefront", apartment=False):
    for x in [-1.88, 1.88]:
        box("Entry pier", (x, 0.16, 1.6), (0.24, 0.38, 3.2), "Stone")
    box("Sign fascia", (0, 0.02, 2.86), (4, 0.42, 0.68), "Dark" if apartment else "Teal")
    box("Brass fascia line", (0, -0.205, 2.54), (3.7, 0.015, 0.025), "Brass")
    box("Brass fascia line", (0, -0.205, 3.12), (3.7, 0.015, 0.025), "Brass")
    # 140 cm cua di hoan toan mo, khong co kinh hay collision chan ngang.
    for x in [-1.26, 1.26]:
        box("Shop display glass", (x, 0.04, 1.27), (0.93, 0.055, 2.44), "Glass")
        for edge in [-0.49, 0.49]:
            box("Shop frame", (x + edge, -0.02, 1.26), (0.045, 0.17, 2.52), "Brass")
        box("Display plinth", (x, -0.04, 0.16), (1.0, 0.30, 0.32), "Stone")
    for x in [-0.73, 0.73]:
        box("Door casing", (x, 0.02, 1.25), (0.06, 0.30, 2.5), "Dark")
    box("Entry canopy", (0, -0.55, 2.57), (3.70, 1.30, 0.10), "Teal" if not apartment else "Aluminium")
    for x in [-1.65, 1.65]:
        box("Canopy bracket", (x, -0.35, 2.47), (0.05, 0.8, 0.10), "Dark")
    if apartment:
        box("Intercom", (0.86, -0.07, 1.42), (0.12, 0.07, 0.24), "Aluminium")
        for z in [1.38, 1.44, 1.50]:
            cylinder("Intercom key", (0.86, -0.115, z), 0.012, 0.014, "Brass", "Y", 12)
    return combine(identifier)


def cornice():
    for y, z, depth, height in [(0.0, 0.08, 0.32, 0.16), (-0.07, 0.22, 0.46, 0.12),
                                (-0.14, 0.35, 0.60, 0.14), (-0.17, 0.45, 0.66, 0.06)]:
        box("Cornice course", (0, y, z), (4, depth, height), "Stone", 0.015)
    for x in [-1.7, -1.1, -0.5, 0.1, 0.7, 1.3, 1.9]:
        box("Dentil", (x, -0.18, 0.11), (0.15, 0.25, 0.18), "Stone")
    return combine("Cornice")


def balcony():
    box("Balcony slab", (0, -0.65, 0.10), (3.6, 1.50, 0.20), "Stone")
    for x in [-1.7, 1.7]:
        box("Support bracket", (x, -0.40, -0.18), (0.10, 0.9, 0.45), "Dark")
        for z in [0.32, 1.14]:
            box("Side rail", (x, -0.68, z), (0.055, 1.35, 0.06), "Dark")
    for z in [0.32, 1.14]:
        box("Front rail", (0, -1.34, z), (3.45, 0.055, 0.06), "Dark")
    for i in range(19):
        box("Baluster", (-1.7 + i * 3.4 / 18, -1.34, 0.73), (0.025, 0.03, 0.84), "Dark", 0.003)
    return combine("Balcony")


def roof_equipment():
    for x in [-0.72, 0.72]:
        box("HVAC foot", (x, 0, 0.11), (0.13, 1.14, 0.22), "Dark")
    box("HVAC housing", (0, 0, 0.66), (1.8, 1.2, 0.92), "Aluminium", 0.035)
    for x in [-0.45, 0.45]:
        cylinder("Fan rim", (x, 0, 1.16), 0.34, 0.09, "Dark")
        cylinder("Fan motor", (x, 0, 1.20), 0.08, 0.08, "Aluminium")
        for i in range(9):
            y = -0.28 + i * 0.07
            box("Fan safety grille", (x, y, 1.224), (0.56, 0.014, 0.012), "Aluminium", 0.002)
    for i in range(12):
        box("HVAC louvre", (0, -0.62, 0.3 + i * 0.057), (1.58, 0.055, 0.022), "Dark", 0.003)
    return combine("RoofEquipment")
