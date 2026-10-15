"""Deterministic living props grounded in existing apartment and civic layouts."""

from CityLayout import APARTMENT
from CityCivicDistrict import SITES


REQUIRED = (
    "CeilingFan", "TableLamp", "WallAirConditioner", "Refrigerator", "Microwave",
    "KitchenSink", "FireExtinguisher", "CivicMonument", "PlaygroundSlide",
    "PlaygroundSwing", "ArcadeCabinet",
)


def describe():
    items = []

    def add(site, name, mesh, location, yaw=0, collision=True, scale=(1, 1, 1), material=None):
        items.append(dict(label=f"Living_{site}_{name}", site=site, mesh=mesh,
                          location=location, yaw=yaw, scale=scale, collision=collision,
                          material=material))

    ax, ay = APARTMENT["centre"]
    add("Apartment", "Fan", "CeilingFan", (ax, ay + 250, 327), collision=False)
    add("Apartment", "AirConditioner", "WallAirConditioner", (ax + 300, ay + 775, 270),
        yaw=-90, collision=False)
    for name, x, y, _, _ in SITES[:4]:
        add(name, "Extinguisher", "FireExtinguisher", (x + 1880, y - 650, 15))
        if name == "Police":
            add(name, "Monument", "CivicMonument", (x + 6200, y + 3000, 0))
        elif name == "Bar":
            add(name, "Fridge", "Refrigerator", (x + 4650, y + 1450, 15), yaw=-90)
            # Mat quay vao phong; tach lo vi song khoi am nuoc o giua quay hien co.
            add(name, "Microwave", "Microwave", (x + 2700, y + 1300, 120), yaw=-90)
            add(name, "TableLamp", "TableLamp", (x + 3550, y - 1050, 92), collision=False)
            add(name, "Sink", "KitchenSink", (x + 4300, y + 1450, 85), yaw=-90)
            # Khung do bon rua de ho long bon, khong dat mat hop kin xuyen qua day bon.
            for index, (dx, dy) in enumerate(((-32, -27), (-32, 27), (32, -27), (32, 27))):
                add(name, f"SinkLeg{index}", "Cube", (x + 4300 + dx, y + 1450 + dy, 60.875),
                    scale=(0.05, 0.05, 0.9175), material="Living_Steel")
        elif name == "Arcade":
            for side in (-1, 1):
                add(name, f"Cabinet{side}", "ArcadeCabinet", (x + 4700, y + side * 1250, 15),
                    yaw=-90 * side)
    _, x, y, _, _ = SITES[4]
    add("AmusementPark", "Slide", "PlaygroundSlide", (x + 8200, y - 2400, 15))
    add("AmusementPark", "Swing", "PlaygroundSwing", (x + 9350, y - 2000, 15), yaw=90)
    return items


def furnish():
    from CityScene import box, prop

    actors = []
    for item in describe():
        if item["mesh"] == "Cube":
            actor = box(item["label"], item["location"], tuple(v * 100 for v in item["scale"]),
                        item["material"], item["collision"])
        else:
            actor = prop(item["mesh"], item["label"], item["location"], item["yaw"],
                         item["scale"], item["collision"])
        actor.set_editor_property("is_spatially_loaded", True)
        actors.append(actor)
    return actors
