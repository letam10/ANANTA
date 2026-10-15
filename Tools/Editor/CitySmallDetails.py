"""Sparse recognizable props on authored counters and a compact apartment washstand."""

from CityLayout import APARTMENT
from CityCivicDistrict import SITES

REQUIRED = ("CookingPot", "Saucepan", "KitchenBowl", "CoffeeMug",
            "MakeupCompact", "ToyBlocks", "RoomVase", "BathroomSoap")

def describe():
    ax, ay = APARTMENT["centre"]
    _, bx, by, _, _ = next(site for site in SITES if site[0] == "Bar")
    values = (
        ("CookingPot", (bx + 2770, by + 1300, 120), 0),
        ("Saucepan", (bx + 2850, by + 1320, 120), 0),
        ("KitchenBowl", (bx + 3320, by + 1280, 120), 0),
        ("CoffeeMug", (bx + 3580, by - 1025, 92), 0),
        ("MakeupCompact", (ax + 850, ay + 450, 54), 0),
        ("ToyBlocks", (ax + 420, ay + 500, 15), 0),
        ("RoomVase", (ax - 565, ay - 440, 92), 0),
        ("BathroomSoap", (ax + 830, ay - 590, 95), 0),
    )
    return [dict(mesh=name, label=f"Living_Small_{name}", location=location, yaw=yaw,
                 scale=(1, 1, 1), collision=False) for name, location, yaw in values]

def furnish():
    from CityScene import prop, box

    ax, ay = APARTMENT["centre"]
    actors = []
    # Flange bon rua cao 21.75 cm so voi origin; de ho phan long bon thay vi hop dac xuyen qua.
    for index, (dx, dy) in enumerate(((-27, -31), (-27, 31), (27, -31), (27, 31))):
        actors.append(box(f"Living_Small_WashstandLeg{index}", (ax + 720 + dx, ay - 585 + dy, 55),
                          (5, 5, 80), "City_oak_veneer_01"))
    actors.append(prop("KitchenSink", "Living_Small_Washbasin", (ax + 720, ay - 585, 73.25)))
    actors.append(box("Living_Small_SoapShelf", (ax + 815, ay - 590, 93),
                      (60, 90, 4), "City_oak_veneer_01"))
    for side in (-1, 1):
        actors.append(box(f"Living_Small_ShelfLeg{side}", (ax + 815 + side * 24, ay - 590, 53),
                          (5, 80, 76), "City_oak_veneer_01"))
    for item in describe():
        actor = prop(item["mesh"], item["label"], item["location"], item["yaw"], collision=False)
        actor.static_mesh_component.set_editor_property("affect_distance_field_lighting", False)
        actors.append(actor)
    for actor in actors:
        actor.set_editor_property("is_spatially_loaded", True)
    return actors
