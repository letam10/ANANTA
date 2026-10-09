"""Accessible civic rooms and a pedestrian amusement court; coordinates in cm."""

# Cac diem trong hop dong la moc duong; nha nam trong o dat phia dong.
SITES = (
    ("Police", -60000, 6000, "DistrictLimestone", "CENTRAL / POLICE"),
    ("Fire", -48000, 6000, "DistrictFireBrick", "NOVA / FIRE STATION"),
    ("Bar", -36000, -6000, "DistrictTimber", "LOW TIDE / SOCIAL CLUB"),
    ("Arcade", -24000, -6000, "DistrictNavy", "PIXEL PIER / ARCADE"),
    ("AmusementPark", -12000, -6000, "DistrictTeal", "LANTERN / PLAY GARDEN"),
)
RESERVES = tuple((x + 1350, y - 4500, x + 10350, y + 4500) for _, x, y, _, _ in SITES)
SERVICES = (
    ("Police", "Neighbourhood desk: report lost property and read the district safety notices."),
    ("Fire", "Station notes: leave the appliance apron clear and use marked pedestrian crossings."),
    ("Bar", "Low Tide hosts local musicians beside the canal every evening."),
    ("Arcade", "Pixel Pier preserves classic cabinets and the neighbourhood high score archive."),
)
ENTRY_CLEAR_WIDTH = 480
FLOOR_Z = 15


def access_lanes():
    return [(name, (x + 1380, y - 240, 16), (x + 4720, y + 240, 240))
            for name, x, y, _, _ in SITES[:4]]


def shell(layout, x, y, wall):
    cx = x + 3500
    # Nen ngoai thap hon san go 1 cm de hai be mat khong tranh depth.
    layout.box("DistrictPaving", (x + 3400, y, 7), (4100, 4400, 14))
    layout.box("DistrictTimber", (cx, y, 7.5), (3400, 3600, 15))
    layout.box(wall, (x + 5200, y, 260), (35, 3600, 490))
    for side in (-1, 1):
        layout.box(wall, (cx, y + side * 1800, 260), (3400, 35, 490))
        # Cua that rong 480 cm, khong co mesh cua kinh chan duong di.
        layout.box(wall, (x + 1800, y + side * 1020, 75), (35, 1560, 120))
        layout.box(wall, (x + 1800, y + side * 1020, 455), (35, 1560, 110))
        layout.box("DistrictSteel", (x + 1760, y + side * 265, 185), (80, 50, 340))
        layout.box("DistrictLimestone", (x + 1730, y + side * 1050, 70), (100, 1480, 110))
        layout.box("InteriorGlass", (x + 1777, y + side * 1045, 267), (4, 1490, 264))
        for offset in (300, 670, 1040, 1410, 1790):
            layout.box("DistrictSteel", (x + 1770, y + side * offset, 267), (12, 14, 270))
    layout.box(wall, (x + 1800, y, 430), (45, 480, 150))
    layout.box("DistrictSteel", (cx, y, 532), (3540, 3740, 45))
    layout.box("DistrictPlaster", (cx, y, 502), (3350, 3550, 12))
    layout.box("DistrictSteel", (x + 1580, y, 372), (440, 1300, 35))
    for yy in (-1600, 1600):
        layout.add("DetailedPlanter", (x + 1480, y + yy, FLOOR_Z))
        layout.add("RoofEquipment", (x + 4500, y + yy / 2, 555), collision=False)
    for yy in (-2800, 2800):
        layout.add("DetailedStreetLamp", (x + 1580, y + yy, FLOOR_Z), yaw=0)
        layout.add("Bench", (x + 2400, y + yy, FLOOR_Z))
    layout.add("BusStopSign", (x + 1420, y - 3600, 0))
    layout.add("BusShelter", (x + 1900, y - 3700, 0), yaw=90)


def room_details(layout, name, x, y):
    layout.add("InteriorServiceDesk", (x + 4850, y, FLOOR_Z), yaw=90)
    layout.add("TransitRouteDisplay", (x + 5090, y + 700, 135), yaw=90, collision=False)
    for side in (-1, 1):
        layout.add("InteriorSlatPanel", (x + 4200, y + side * 1760, 80), yaw=180 if side > 0 else 0)
        layout.add("House_hanging_industrial_lamp", (x + 3000, y + side * 900, 330), collision=False)
    if name == "Police":
        for yy in (-1100, 1100):
            layout.add("House_sofa_02", (x + 2600, y + yy, FLOOR_Z), yaw=90)
            layout.add("InteriorGalleryFrame", (x + 3400, y + yy * 1.60, 170), collision=False)
            layout.add("ClinicSupplyCabinet", (x + 4650, y + yy, FLOOR_Z), yaw=90)
        layout.box("DistrictNavy", (x + 1738, y, 440), (18, 1500, 90), False)
        layout.box("DistrictLimestone", (x + 5400, y + 2800, 130), (220, 800, 260))
    elif name == "Fire":
        for yy in (-1350, -850, 850, 1350):
            layout.add("WorkshopToolBoard", (x + 4200, y + yy, 140), yaw=90, collision=False)
            layout.add("WorkshopPartsCrate", (x + 4650, y + yy, FLOOR_Z))
        fire_apron(layout, x + 7400, y)
    elif name == "Bar":
        for xx in (2800, 3250, 3700):
            layout.add("CafeCounter", (x + xx, y + 1300, FLOOR_Z))
            layout.add("House_vintage_electric_kettle", (x + xx, y + 1300, 120), collision=False)
        for xx in (2600, 3550, 4400):
            layout.add("CafeTable", (x + xx, y - 1050, FLOOR_Z))
            for yy in (-1300, -800):
                layout.add("House_dining_chair_02", (x + xx, y + yy, FLOOR_Z))
        layout.add("InteriorSlatPanel", (x + 3500, y + 1760, 180), yaw=180, collision=False)
    elif name == "Arcade":
        for xx in (2550, 3300, 4050):
            for side in (-1, 1):
                arcade_cabinet(layout, x + xx, y + side * 1250, side)
        layout.box("DistrictNeon", (x + 1740, y, 443), (15, 1500, 65), False)


def fire_apron(layout, x, y):
    layout.box("DistrictPaving", (x, y, 7.5), (4300, 3500, 15))
    for side in (-1, 1):
        layout.box("DistrictFireBrick", (x + 1000, y + side * 1600, 390), (1700, 55, 750))
        layout.box("DistrictSteel", (x + 1850, y + side * 820, 400), (45, 1570, 770))
        for z in range(80, 741, 80):
            layout.box("DistrictSteel", (x + 100, y + side * 820, z), (15, 1300, 12), False)
        layout.add("RoadBarrier", (x - 1300, y + side * 1700, FLOOR_Z), yaw=90)
        layout.box("RoadMark", (x - 300, y + side * 790, 16), (3100, 20, 1), False)
    layout.box("DistrictSteel", (x + 1000, y, 795), (1850, 3300, 60))
    layout.box("DistrictFireBrick", (x + 100, y, 785), (70, 3300, 170))
    layout.box("DistrictFireBrick", (x + 100, y, 400), (100, 100, 770))
    layout.add("TrafficSignal", (x - 1850, y + 2050, FLOOR_Z), yaw=-90)


def arcade_cabinet(layout, x, y, side):
    layout.box("DistrictNavy", (x, y, 110), (125, 85, 190))
    layout.box("DistrictSteel", (x, y - side * 46, 110), (140, 50, 12))
    layout.box("DistrictNeon", (x, y - side * 44, 164), (95, 4, 62), False)
    layout.box("DistrictPink", (x, y - side * 45, 220), (130, 6, 30), False)
    for dx in (-30, 10, 35):
        layout.box("DistrictYellow", (x + dx, y - side * 55, 120), (12, 12, 8), False)


def park(layout, x, y):
    layout.box("DistrictPaving", (x + 5600, y, 7.5), (8500, 8400, 15))
    for yy in (-3650, 3650):
        for xx in range(2100, 9901, 1300):
            layout.add("TreeBroadleaf", (x + xx, y + yy, 15), collision=False)
            layout.add("DetailedPlanter", (x + xx, y + yy, 15))
    for yy in (-1300, 1300):
        layout.box("DistrictYellow", (x + 1850, y + yy, 430), (120, 120, 830))
    layout.box("DistrictTeal", (x + 1850, y, 860), (190, 3000, 170))
    cx, cy = x + 7450, y + 1700
    layout.add("FerrisWheel", (cx, cy, 15))
    for side in (-1, 1):
        layout.add("RoadBarrier", (cx + side * 650, cy, 15), yaw=90)
    for xx in (3200, 4300, 5400):
        layout.add("MarketStall", (x + xx, y - 2550, 15))
        layout.add("Bench", (x + xx, y - 1700, 15))
        layout.add("DetailedStreetLamp", (x + xx, y + 3000, 15))
    for xx in (3500, 4500, 5500):
        for yy in (900, 1800):
            layout.box("DistrictPink", (x + xx, y + yy, 45), (650, 650, 60))
            layout.add("CafeTable", (x + xx, y + yy, 75))
            layout.add("House_mid_century_lounge_chair", (x + xx + 200, y + yy, 75), yaw=90)


def generate(layout):
    for name, x, y, wall, _ in SITES:
        if name == "AmusementPark":
            park(layout, x, y)
        else:
            shell(layout, x, y, wall)
            room_details(layout, name, x, y)


def furnish():
    import unreal
    from CityScene import spawn, text, mesh_asset

    descriptions = dict(SERVICES)
    for name, x, y, _, title in SITES:
        text("District_" + name + "_Sign", title, (x + 1720, y, 444), 180, 60)
        if name not in descriptions:
            continue
        actor = spawn(unreal.CityServiceInteractable, "District_" + name + "_Read", (x + 4730, y, 115))
        actor.set_editor_property("interaction_id", name + "_Read")
        actor.set_editor_property("service_kind", unreal.CityServiceKind.READ)
        actor.set_editor_property("display_name", title)
        actor.set_editor_property("description", descriptions[name])
        actor.visual_mesh.set_static_mesh(mesh_asset("Bollard"))
        actor.visual_mesh.set_collision_profile_name("NoCollision")
        actor.visual_mesh.set_relative_scale3d(unreal.Vector(0.3, 0.3, 0.3))
        actor.set_editor_property("is_spatially_loaded", True)
