"""Authored outer-city facilities; static shells and public exterior access only."""

import math

AIRPORT = (180000, 180000, 276000, 228000)
SITES = (
    ("Station", -66000, 198000, 0, "DistrictSteel"),
    ("Hotel", -18000, 198000, 4500, "DistrictLimestone"),
    ("Restaurant", 6000, 198000, 800, "DistrictTimber"),
    ("Theater", 30000, 198000, 1400, "DistrictLimestone"),
    ("Cinema", 54000, 198000, 1700, "DistrictNavy"),
    ("Cafe", 78000, 198000, 650, "DistrictFireBrick"),
    ("Pool", 102000, 198000, 0, "DistrictTeal"),
    ("Factory", -42000, 222000, 1400, "DistrictFireBrick"),
)
RESERVES = tuple((x - 4700, y - 5100, x + 4700, y + 4700) for _, x, y, _, _ in SITES)
RESERVES += (AIRPORT, (-336000, 249950, 336000, 254050))
FACILITIES = [dict(id=name, centre=(x, y), bounds=RESERVES[index], shellOnly=True,
                   gameplay=False, entryWidthCm=300 if name == "Station" else 600)
              for index, (name, x, y, _, _) in enumerate(SITES)]
FACILITIES += [dict(id="Airport", centre=(228000, 204000), bounds=AIRPORT,
                    shellOnly=True, gameplay=False, entryWidthCm=1200),
               dict(id="Highway", centre=(0, 252000), bounds=RESERVES[-1],
                    shellOnly=False, gameplay=False, entryWidthCm=3000)]


def access_lanes():
    result = []
    for name, x, y, _, _ in SITES:
        if name == "Station":
            x -= 4500
            end = y + 2100
            width = 300
        else:
            end = y - 2040
            width = 600
        result.append(dict(id=name, min=(x - width / 2, y - 5100, 21),
                           max=(x + width / 2, end, 260), widthCm=width))
    result.append(dict(id="Airport", min=(185400, 180900, 21), max=(186600, 185940, 260),
                       widthCm=1200))
    return result


def cube_yaw(layout, material, location, size, yaw, collision=True):
    layout.add("Cube", location, tuple(value / 100 for value in size), yaw, material, collision)


def shell(layout, x, y, height, material):
    layout.box("DistrictPaving", (x, y, 8), (9200, 9200, 16))
    layout.box("DistrictPaving", (x, y - 3550, 10), (1200, 3100, 20))
    layout.box(material, (x, y, height / 2 + 20), (6600, 4000, height))
    layout.box("DistrictSteel", (x, y, height + 50), (6800, 4200, 60))
    # Mai don va cua lom doc ro tu pho; khoi nha kin khong co noi that gia.
    layout.box("InteriorGlass", (x, y - 2015, 240), (600, 12, 440))
    layout.box("DistrictSteel", (x, y - 2390, 520), (1600, 900, 45))
    for side in (-1, 1):
        layout.box("DistrictLimestone", (x + side * 740, y - 2660, 270), (70, 70, 500))
        layout.add("DetailedPlanter", (x + side * 1700, y - 3300, 16))
    for z in range(800, height - 100, 420):
        for xx in range(-2700, 2701, 600):
            for side in (-1, 1):
                layout.box("InteriorGlass", (x + xx, y + side * 2006, z), (390, 8, 230), False)


def hospitality(layout, name, x, y, height, material):
    shell(layout, x, y, height, material)
    if name == "Hotel":
        layout.box("DistrictLimestone", (x, y + 500, height + 350), (3900, 2400, 600))
        for xx in (-2700, -2100, 2100, 2700):
            layout.box("DistrictSteel", (x + xx, y - 2130, 2400), (80, 240, 4200), False)
        layout.box("DistrictNeon", (x + 2850, y - 2140, 3350), (250, 30, 1800), False)
    elif name in ("Restaurant", "Cafe"):
        for xx in (-2600, -1500, 1500, 2600):
            layout.box("InteriorGlass", (x + xx, y - 2010, 270), (900, 10, 380), False)
            layout.box("DistrictTeal", (x + xx, y - 2280, 540), (980, 600, 45))
            layout.add("CafeTable", (x + xx, y - 3400, 16))
            for yy in (-3100, -3670):
                layout.add("House_dining_chair_02", (x + xx, y + yy, 16), yaw=180 if yy == -3100 else 0)
        if name == "Restaurant":
            layout.add("RoofEquipment", (x + 2200, y + 600, height + 85), collision=False)
    elif name == "Cinema":
        layout.box("DistrictPink", (x, y - 2450, 740), (6000, 1100, 260))
        for xx in (-2400, -1400, 1400, 2400):
            layout.box("DistrictNeon", (x + xx, y - 3030, 735), (800, 18, 130), False)
            layout.box("DistrictYellow", (x + xx, y - 2025, 270), (680, 15, 330), False)
        for xx in range(-2800, 2801, 400):
            layout.box("DistrictNeon", (x + xx, y - 3010, 580), (90, 40, 30), False)
    elif name == "Theater":
        # Cac canh mai bac giat tao hinh quat, dung chung Cube thay vi mesh rieng.
        for wing, yaw in ((-1, -24), (0, 0), (1, 24)):
            for step in range(9):
                width = 2000 - step * 150
                cube_yaw(layout, "DistrictLimestone", (x + wing * 1850, y + 350, height + 90 + step * 100),
                         (width, 3500 - step * 230, 130), yaw)
        for xx in (-2700, -1800, 1800, 2700):
            layout.box("DistrictLimestone", (x + xx, y - 2400, 550), (150, 150, 1060))


def station(layout, x, y):
    layout.box("DistrictPaving", (x, y, 10), (9300, 9200, 20))
    layout.box("DistrictPaving", (x - 4400, y - 3550, 10), (500, 3100, 20))
    for side in (-1, 1):
        track_y = y + side * 500
        layout.box("DistrictSteel", (x, track_y, 24), (8300, 360, 8), False)
        for offset in range(-3900, 3901, 150):
            layout.box("DistrictTimber", (x + offset, track_y, 32), (22, 300, 16), False)
        for rail_y in (-72, 72):
            layout.box("DistrictSteel", (x, track_y + rail_y, 44), (8100, 8, 14), False)
        for xx in (-4110, 4110):
            layout.box("DistrictYellow", (x + xx, track_y, 90), (50, 280, 140))
        platform_y = y + side * 1370
        layout.box("DistrictPaving", (x, platform_y, 60), (8000, 940, 80))
        layout.box("DistrictYellow", (x, y + side * 925, 101), (8000, 25, 2), False)
        for xx in range(-3600, 3601, 1200):
            layout.box("DistrictSteel", (x + xx, y + side * 1700, 380), (45, 45, 560))
        for band in range(7):
            z = 720 - abs(band - 3) * 45
            layout.box("DistrictTeal", (x, platform_y - 480 + band * 160, z), (8200, 180, 35))
        # Bac 20 cm o dau tay, noi hai san ga bang loi ngang ngoai dau ray.
        for step in range(4):
            layout.box("DistrictPaving", (x - 4260 + step * 75, platform_y, 20 + (step + 1) * 10),
                       (75, 940, (step + 1) * 20))
    # Sanh transit doc lap nam phia tay nam, cach loi vao ga va khong chen ray.
    layout.add("FacadeTransit", (x - 3900, y - 3900, 15), yaw=90, collision=False)
    layout.add("BusStopSign", (x - 3400, y - 3600, 15), yaw=90, collision=False)
    layout.add("TransitRouteDisplay", (x - 2400, y - 1700, 160), collision=False)


def pool(layout, x, y):
    from CityRoofPool import generate
    generate(layout, x, y)


def factory(layout, x, y, height, material):
    shell(layout, x, y, height, material)
    for xx in (-2200, 0, 2200):
        for tier in range(5):
            layout.box("DistrictSteel", (x + xx, y, height + 100 + tier * 110),
                       (2000 - tier * 330, 4100, 140))
    for xx in (-3000, -2200, -1400):
        layout.box("DistrictSteel", (x + xx, y + 3300, 770), (620, 620, 1500))
        layout.box("DistrictLimestone", (x + xx, y + 3300, 1540), (690, 690, 100))
        layout.box("DistrictContainerRed", (x + xx, y + 3300, 1060), (650, 650, 160), False)
    for xx in (2000, 3000):
        layout.box("DistrictSteel", (x + xx, y + 1200, 2400), (330, 330, 2000))
        layout.box("DistrictFireBrick", (x + xx, y + 1200, 2900), (360, 360, 160), False)
    # Dock loading faces the street side (-Y), so the apron and shutters share one alignment.
    dock_y = y - 2520
    layout.box("DistrictPaving", (x + 2100, dock_y, 20), (3600, 1200, 40))
    layout.box("DistrictYellow", (x + 2100, dock_y - 620, 68), (3600, 90, 136), False)
    for xx in (900, 1800, 2700, 3600):
        layout.box("DistrictSteel", (x + xx, dock_y - 680, 350), (70, 70, 700), False)
    for xx in (1400, 2600):
        layout.box("DistrictSteel", (x + xx, y - 2042, 700), (920, 54, 1160), False)
        layout.box("DistrictYellow", (x + xx, y - 2085, 1310), (980, 72, 80), False)
        layout.box("DistrictSteel", (x + xx, y - 2115, 1325), (1080, 55, 70), False)
    layout.box("DistrictSteel", (x + 2100, y - 2070, 1510), (3900, 110, 120), False)
    for xx in (400, 1100, 1800, 2500, 3200, 3900):
        layout.box("DistrictYellow", (x + xx, y - 2125, 1530), (420, 32, 28), False)


def airport(layout):
    layout.box("DistrictPaving", (211000, 190000, 10), (58000, 16000, 20))
    layout.box("Asphalt", (228000, 213000, 3), (85000, 2400, 6))
    layout.box("Asphalt", (227000, 203000, 3), (75000, 1200, 6))
    for xx in (190000, 264000):
        layout.box("Asphalt", (xx, 208000, 3), (1200, 11200, 6))
    for xx in range(187000, 270001, 2500):
        layout.box("RoadMark", (xx, 213000, 7), (1300, 30, 2), False)
    for end in (187000, 269000):
        for yy in range(212200, 213801, 400):
            layout.box("RoadMark", (end, yy, 7), (1700, 120, 2), False)
    shell(layout, 186000, 188000, 750, "DistrictLimestone")
    layout.box("DistrictPaving", (186000, 182500, 10), (1200, 4400, 20))
    layout.box("DistrictSteel", (197000, 188000, 1600), (900, 900, 3200))
    layout.box("InteriorGlass", (197000, 188000, 3380), (1900, 1700, 360))
    layout.box("DistrictSteel", (197000, 188000, 3620), (2200, 2000, 120))
    for xx in (207000, 220000):
        layout.box("DistrictSteel", (xx, 185000, 700), (8500, 4700, 1400))
        layout.box("DistrictTeal", (xx, 185000, 1450), (8800, 5000, 100))
        layout.box("InteriorGlass", (xx, 187370, 570), (7600, 20, 1080), False)
    layout.add("CivilianPlane", (218000, 193000, 20), yaw=180)
    layout.box("DistrictNavy", (231000, 192000, 21), (4800, 4800, 2), False)
    for offset in (-600, 600):
        layout.box("RoadMark", (231000 + offset, 192000, 23), (100, 1500, 2), False)
    layout.box("RoadMark", (231000, 192000, 23), (1200, 100, 2), False)
    for index in range(24):
        angle = index * 15
        x = 231000 + math.cos(math.radians(angle)) * 1900
        y = 192000 + math.sin(math.radians(angle)) * 1900
        cube_yaw(layout, "RoadMark", (x, y, 23), (520, 70, 2), angle + 90, False)
    layout.add("Helicopter", (231000, 192000, 24))


def highway(layout):
    # Cao toc mat dat noi luoi pho; de trong giao lo 2400 cm, khong chan duong cat ngang.
    for start in range(-336000, 336000, 12000):
        x = start + 6000
        layout.box("Asphalt", (x, 252000, 4), (12000, 3000, 8))
        layout.box("Curb", (x, 252000, 42), (9600, 45, 68))
        for side in (-1, 1):
            layout.box("Sidewalk", (x, 252000 + side * 1770, 10), (9600, 500, 20))
            for lane in (470, 940):
                for offset in range(-4200, 4201, 1400):
                    layout.box("RoadMark", (x + offset, 252000 + side * lane, 9), (650, 15, 2), False)


def generate(layout):
    for name, x, y, height, material in SITES:
        if name == "Station":
            station(layout, x, y)
        elif name == "Pool":
            pool(layout, x, y)
        elif name == "Factory":
            factory(layout, x, y, height, material)
        else:
            hospitality(layout, name, x, y, height, material)
    airport(layout)
    highway(layout)
    layout.add("FireEngine", (-41700, 5220, 15), yaw=180)
    from CityInteractiveTransit import rowboat_dock
    rowboat_dock(layout)
