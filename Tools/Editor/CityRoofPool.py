"""Two-storey pool building with a supported exterior stair and a guarded roof deck."""

def generate(layout, x, y):
    layout.box("DistrictPaving", (x, y, 10), (9200, 9200, 20))
    layout.box("DistrictPaving", (x, y - 3550, 10), (1200, 3100, 20))
    layout.box("DistrictTeal", (x, y, 420), (6600, 4000, 800))
    layout.box("DistrictLimestone", (x, y, 830), (6800, 4200, 20))
    for level in (270, 620):
        for xx in (-2700, -1800, -900, 900, 1800, 2700):
            layout.box("InteriorGlass", (x + xx, y - 2008, level), (600, 10, 210), False)
    layout.box("DistrictSteel", (x, y - 2320, 420), (1500, 650, 40))
    layout.box("InteriorGlass", (x, y - 2010, 220), (600, 12, 400))
    # Bac cao 20 cm, rong 5 m; moi bac co than dac do capsule, khong chi la mat trang tri.
    for step in range(41):
        height = (step + 1) * 20
        layout.box("DistrictPaving", (x - 3650, y - 2200 + step * 100, 20 + height / 2),
                   (500, 100, height))
    # Landing bat dau sau bac cuoi, khong che ba bac truoc hoac chong mat mai.
    layout.box("DistrictPaving", (x - 3650, y + 1975, 830), (500, 250, 20))
    for side in (-1, 1):
        layout.box("DistrictSteel", (x, y + side * 2070, 890), (6750, 35, 100))
    layout.box("DistrictSteel", (x + 3370, y, 890), (35, 4100, 100))
    layout.box("DistrictSteel", (x - 3370, y - 350, 890), (35, 3300, 100))
    layout.box("DistrictLimestone", (x, y + 300, 850), (5200, 2800, 20))
    layout.box("DistrictWater", (x, y + 300, 936), (4900, 2500, 8), False)
    for side in (-1, 1):
        layout.box("DistrictLimestone", (x, y + 300 + side * 1340, 910), (5200, 160, 140))
        layout.box("DistrictLimestone", (x + side * 2520, y + 300, 910), (160, 2800, 140))
    for xx in (-2400, -1200, 0, 1200, 2400):
        layout.add("House_mid_century_lounge_chair", (x + xx, y - 1600, 840), yaw=90)
    for side in (-1, 1):
        layout.add("DetailedStreetLamp", (x + side * 2750, y - 1500, 840),
                   yaw=180 if side > 0 else 0, collision=False)
        layout.add("DetailedPlanter", (x + side * 2500, y + 1500, 840), collision=False)
    layout.add("BusStopSign", (x, y - 1950, 840), yaw=90, collision=False)
    for lane in range(-1800, 1801, 900):
        layout.box("DistrictYellow", (x + lane, y + 300, 940.1), (12, 2500, .2), False)
