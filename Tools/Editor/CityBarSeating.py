"""Grouped bar seating using measured existing meshes; coordinates in cm."""

from CityCivicDistrict import FLOOR_Z, SITES


def generate(layout):
    _, x, y, _, _ = next(site for site in SITES if site[0] == "Bar")
    tables = [(xx, yy) for xx in (2300, 3150, 4000, 4850) for yy in (-1550, -550)]
    tables.extend((xx, 650) for xx in (2300, 3150, 4000))
    # Cac cum ngoi nam ngoai hanh lang trung tam rong 480 cm.
    for xx, yy in tables:
        layout.add("CafeTable", (x + xx, y + yy, FLOOR_Z))
        for side in (-1, 1):
            layout.add("House_dining_chair_02", (x + xx + side * 115, y + yy, FLOOR_Z),
                       yaw=90 * side)
        layout.box("Finish_Woven", (x + xx, y + yy, 15.6), (360, 300, 1.0), collision=False)
    for xx, yy, yaw in ((2200, 1150, -90), (2200, 1550, -90), (4850, 750, 90), (4850, 1100, 90)):
        layout.add("House_sofa_02", (x + xx, y + yy, FLOOR_Z), yaw=yaw)
