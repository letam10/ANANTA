"""Room-specific dressing with deliberate gaps from walls and walking routes."""

import unreal

from coastal_home import furnish_home, room_light
from coastal_prop_actions import place_interactive_prop


def dress(scene, data, kind):
    x, y = data["center_m"]
    z = data["ground_m"]

    def prop(name, dx, dy, dz=0, yaw=0, scale=(1, 1, 1), interactive_message=None):
        position = (x + dx, y + dy, z + dz)
        if interactive_message:
            place_interactive_prop(
                scene,
                f"{data['name']}_{name}_Prop",
                name,
                position,
                interactive_message,
                yaw=yaw,
                scale=scale,
            )
        else:
            scene.model(name, position, yaw, scale)

    service_model = "FactoryControl"
    if kind in ("cafe", "restaurant", "bar"):
        for dx in (-4.2, 4.2):
            for dy in (-4, 3.8):
                prop("Table", dx, dy)
                prop("Mug", dx + 0.3, dy, 0.77)
                prop("Book", dx - 0.3, dy, 0.77)
                prop("Chair", dx, dy - 1, yaw=180)
                prop("Chair", dx, dy + 1)
        for dx in (-4.8, -3.2, -1.6, 0):
            prop("KitchenCounter", dx, 8)
        prop("Stove", 1.2, 8, interactive_message="Stove inspected.")
        prop("CookingPan", 1.15, 7.9, 0.89,
             interactive_message="Cooking pan inspected.")
        prop("CookingPot", 1.35, 8.2, 0.89,
             interactive_message="Cooking pot inspected.")
        prop("Fridge", 3.2, 8, interactive_message="Fridge inspected.")
        prop(
            "BarGlassRack",
            4.8,
            7.7,
            1.05,
            scale=(0.8, 0.8, 0.8),
            interactive_message="Glass rack inspected. The bar stock is ready.",
        )
        service_model = "Mug"
    elif kind in ("home", "hotel", "beauty"):
        furnish_home(scene, data)
        if kind == "beauty":
            prop(
                "MakeupKit",
                -5.2,
                9.2,
                0.86,
                scale=(0.7, 0.7, 0.7),
                interactive_message="Makeup kit inspected.",
            )
        east_limit = data["width_m"] / 2 - 0.11 - 0.01
        stove_x = east_limit - scene.model_data["Stove"]["bounds_max_m"][1]
        prop(
            "SaucePan",
            stove_x,
            -4.3,
            0.89,
            yaw=-90,
            scale=(0.85, 0.85, 0.85),
            interactive_message="Sauce pan inspected.",
        )
        prop(
            "BathroomTowel",
            7.2,
            8.2,
            0.8,
            scale=(0.8, 0.8, 0.8),
            interactive_message="Bathroom towel inspected.",
        )
        prop(
            "SofaCushion",
            -6.4,
            -7.2,
            0.8,
            yaw=180,
            scale=(0.8, 0.8, 0.8),
            interactive_message="Sofa cushion inspected.",
        )
        prop(
            "ToyDoll",
            -8.0,
            6.4,
            0.78,
            scale=(0.65, 0.65, 0.65),
            interactive_message="Toy doll inspected.",
        )
        if kind == "hotel":
            prop(
                "Laptop",
                -5.2,
                9.2,
                0.88,
                scale=(0.8, 0.8, 0.8),
                interactive_message="Laptop inspected.",
            )
    elif kind in ("cinema", "opera"):
        scene.box((x, y + 7.5, z + 0.3), (13, 4, 0.6), "Wood")
        scene.box((x, y + 9, z + 2.1), (12, 0.08, 2.8), "Glass", collision=False)
        for row in range(4):
            for column in range(6):
                dx = (column - 2.5) * 1.1
                dy = -5 + row * 1.5
                prop(
                    "Chair",
                    dx,
                    dy,
                    yaw=180,
                    interactive_message=(
                        "Auditorium seat inspected."
                        if row == 0 and column == 0
                        else None
                    ),
                )
    elif kind == "factory":
        for dx in (-5, 0, 5):
            prop("FactoryConveyor", dx, 2)
            prop(
                "FactoryControl",
                dx,
                6,
                yaw=90,
                interactive_message=(
                    "Factory control inspected." if dx == 0 else None
                ),
            )
            prop("FactoryCrate", dx, -3)
            for dy in (-4, -2, 0):
                prop("FactoryBarrel", -8, dy)
    elif kind == "arcade":
        for dx in (-6, -3, 3, 6):
            prop(
                "ArcadeCabinet",
                dx,
                6,
                interactive_message=(
                    "Arcade cabinet inspected." if dx == -3 else None
                ),
            )
            prop("ArcadeCabinet", dx, -3, yaw=180)
        prop("Table", 0, 2)
    else:
        for dx in (-4.5, 4.5):
            prop("Table", dx, 4)
            prop("Chair", dx, 5)
            prop("FactoryControl", dx, 7, yaw=90)
        prop("Sofa", -5, -5)
    prop("PotPlant", 8, -7, scale=(1.8, 1.8, 1.8))
    action_position = (x + 2.1, y - 5.5, z + (0.8 if service_model == "Mug" else 0))
    resident_position = (x - 2.8, y - 5, z)
    if kind in ("home", "hotel", "beauty"):
        # Đặt bảng ở mép hành lang, tránh chặn cửa bếp mới mở rộng.
        action_position = (x + 0.8, y - 2, z)
        resident_position = (x - 3, y - 8, z)
    scene.action(data["name"] + "_Service", action_position,
                 service_message(kind), model=service_model, yaw=90)
    scene.action(data["name"] + "_Resident", resident_position,
                 "Welcome. The station is north, the beach is east. E opens doors and boards vehicles.",
                 kind=2, model="Citizen", yaw=-90, schedule=True)
    if kind not in ("home", "hotel", "beauty"):
        for horizontal in (-5, 5):
            for depth in (-5, 5):
                room_light(scene, f"{data['name']}_Light_{horizontal}_{depth}",
                           (x + horizontal, y + depth, z + 2.8))


def service_message(kind):
    messages = {
        "cafe": "Coffee prepared. Enjoy the coastal promenade.",
        "restaurant": "Kitchen inspected. Cookware and dining tables are ready.",
        "bar": "Bar counter open. The entertainment district is nearby.",
        "hotel": "Room checked in. Use the lift control to visit the roof pool.",
        "home": "Living room, kitchen, bedroom and bathroom inspected.",
        "beauty": "Makeup and accessories inspected.",
        "police": "Dispatch board: patrol car available outside.",
        "fire": "Station equipment ready. Fire engine available outside.",
        "clinic": "First aid received. Ambulance parked outside.",
        "factory": "Conveyor control activated. Workshop supplies inspected.",
        "arcade": "Arcade session started. Machines available in the hall.",
        "cinema": "Cinema ticket checked. Auditorium open.",
        "opera": "Theatre ticket checked. Auditorium and roof terrace open.",
    }
    return messages.get(kind, "Facility inspected.")
