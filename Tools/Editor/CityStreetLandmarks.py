"""Authored public spaces; deterministic placement data without an Unreal dependency."""


SPACES = {
    "WestCafe": (-29600, 5800),
    "CentralGarden": (6000, 6150),
    "EastTransit": (27000, 9500),
}


def describe():
    items = []

    def add(space, name, mesh, dx, dy, z=12, yaw=0, scale=(1, 1, 1), collision=False, material=None):
        x, y = SPACES[space]
        item = dict(label=f"Landmark_{space}_{name}", mesh=mesh, location=(x + dx, y + dy, z),
                    scale=scale, yaw=yaw, collision=collision)
        if material:
            item["material"] = material
        items.append(item)

    def box(space, name, dx, dy, z, size, material, collision=False):
        add(space, name, "Cube", dx, dy, z, scale=tuple(v / 100 for v in size),
            material=material, collision=collision)

    def grove(space, name, dx, dy, broad=True, size=1):
        box(space, name + "Bed", dx, dy, 14, (420, 420, 4), "City_Soil")
        add(space, name + "Tree", "TreeBroadleaf" if broad else "TreeColumnar", dx, dy, 16,
            yaw=23 if broad else 0, scale=(size, size, size))
        for side in (-1, 1):
            add(space, name + f"Plant{side}", "Planter", dx + side * 140, dy + 150, 16,
                scale=(0.65, 0.65, 0.65))

    # De trong truc giua va cua vao; ghe, cay va quay hang tao cac canh san.
    space = "WestCafe"
    box(space, "Paving", 0, 0, 6, (2400, 2800, 12), "City_Paving")
    for index, (dx, dy) in enumerate(((-1000, -1050), (1000, -1050), (1000, 1050))):
        grove(space, f"Grove{index}", dx, dy, size=0.85)
    add(space, "FlowerStand", "MarketStall", -850, 1080, yaw=180)
    add(space, "StandPlanter", "Planter", -1100, 1000)
    for index, (dx, dy) in enumerate(((-450, -1050), (450, 1000))):
        add(space, f"Table{index}", "CafeTable", dx, dy)
        for side in (-1, 1):
            add(space, f"Chair{index}_{side}", "House_dining_chair_02", dx + side * 125, dy,
                yaw=90 * side, collision=True)
    add(space, "Seat", "Bench", 1040, -350, yaw=90, collision=True)
    add(space, "Bikes", "BikeRack", -1080, -400, yaw=90)
    add(space, "Bin", "TrashBin", -1080, -650)
    add(space, "Sign", "StreetSign", 1090, 520, yaw=90)
    box(space, "SeatWall", 500, -1310, 42, (500, 45, 60), "City_stone_wall_02", True)

    space = "CentralGarden"
    box(space, "Paving", 0, 0, 6, (3100, 3400, 12), "City_Paving")
    for index, (dx, dy) in enumerate(((-1250, -1350), (1250, -1350), (-1250, 1350), (1250, 1350))):
        grove(space, f"Grove{index}", dx, dy, broad=index % 2 == 0, size=0.9)
    for side in (-1, 1):
        add(space, f"ReadingSeat{side}", "Bench", side * 650, 1250, yaw=180, collision=True)
        box(space, f"LowWall{side}", side * 650, 1520, 47, (650, 50, 70), "City_stone_wall_02", True)
        add(space, f"Planter{side}", "Planter", side * 1400, side * 500, yaw=90)
    add(space, "BikeStand", "BikeRack", 1200, -650, yaw=90)
    add(space, "Bin", "TrashBin", -1200, -650)
    add(space, "GardenSign", "StreetSign", -1200, 650, yaw=-90)

    space = "EastTransit"
    box(space, "Paving", 0, 0, 6, (3000, 1900, 12), "City_Paving")
    for index, dx in enumerate((-1200, 1200)):
        grove(space, f"Grove{index}", dx, 580, broad=False, size=0.8)
        add(space, f"Shelter{index}", "BusShelter", dx, -550)
        add(space, f"WaitingSeat{index}", "Bench", dx / 2, -80, yaw=180, collision=True)
        add(space, f"Bin{index}", "TrashBin", dx + (-270 if dx < 0 else 270), -550)
    for index, dx in enumerate((-650, -450, 450, 650)):
        add(space, f"BikeStand{index}", "BikeRack", dx, 660)
    add(space, "RouteSign", "StreetSign", 700, -650, yaw=180)
    add(space, "Kiosk", "MarketStall", -650, -650)
    # Dai di bo rong 500 cm xuyen san, noi ve phia nhiem vu ma khong chen vao vung danh nhau.
    return items


def dress():
    from CityScene import material_asset, prop

    actors = []
    for item in describe():
        actor = prop(item["mesh"], item["label"], item["location"], item["yaw"],
                     item["scale"], item["collision"])
        if item.get("material"):
            actor.static_mesh_component.set_material(0, material_asset(item["material"]))
        actors.append(actor)
    return actors
