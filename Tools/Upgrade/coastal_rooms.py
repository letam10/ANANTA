"""Room-specific dressing with deliberate gaps from walls and walking routes."""

import unreal


def dress(scene, data, kind):
    x, y = data["center_m"]
    z = data["ground_m"]

    def prop(name, dx, dy, dz=0, yaw=0, scale=(1, 1, 1)):
        scene.model(name, (x + dx, y + dy, z + dz), yaw, scale)

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
        prop("Stove", 1.2, 8)
        prop("CookingPan", 1.15, 7.9, 0.89)
        prop("CookingPot", 1.35, 8.2, 0.89)
        prop("Fridge", 3.2, 8)
        service_model = "Mug"
    elif kind in ("home", "hotel", "beauty"):
        prop("Sofa", -4.2, -4)
        prop("Table", -4.2, -1.8)
        prop("Book", -4, -1.8, 0.77)
        prop("Bed", -5, 5)
        prop("TeddyToy", -5, 5.35, 0.75, scale=(0.65, 0.65, 0.65))
        prop("KitchenCounter", 5, -5)
        prop("Stove", 6.1, -5)
        prop("CookingPot", 6.1, -5, 0.89)
        prop("Fridge", 7.4, -5)
        prop("Table", -5, 8)
        prop("Perfume", -4.7, 8, 0.77)
        prop("Lipstick", -5.2, 8, 0.77)
        prop("Toilet", 6.8, 7.7, yaw=0)
        prop("Washbasin", 4.5, 7.7)
        # Hai vách phòng tắm để vật nhỏ không lộ ra từ lối vào chính.
        scene.box((x + 3.3, y + 7, z + 1.5), (0.16, 5.4, 3), "White")
        scene.box((x + 6.5, y + 4.3, z + 1.5), (4.2, 0.16, 3), "White")
    elif kind in ("cinema", "opera"):
        scene.box((x, y + 7.5, z + 0.3), (13, 4, 0.6), "Wood")
        scene.box((x, y + 9, z + 2.1), (12, 0.08, 2.8), "Glass", collision=False)
        for row in range(4):
            for column in range(6):
                dx = (column - 2.5) * 1.1
                dy = -5 + row * 1.5
                prop("Chair", dx, dy, yaw=180)
    elif kind == "factory":
        for dx in (-5, 0, 5):
            prop("FactoryConveyor", dx, 2)
            prop("FactoryControl", dx, 6, yaw=90)
            prop("FactoryCrate", dx, -3)
            for dy in (-4, -2, 0):
                prop("FactoryBarrel", -8, dy)
    elif kind == "arcade":
        for dx in (-6, -3, 3, 6):
            prop("ArcadeCabinet", dx, 6)
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
    scene.action(data["name"] + "_Service", action_position,
                 service_message(kind), model=service_model, yaw=90)
    scene.action(data["name"] + "_Resident", (x - 2.8, y - 5, z),
                 "Welcome. The station is north, the beach is east. E opens doors and boards vehicles.",
                 kind=2, model="Citizen", yaw=-90)
    light = scene.spawn(unreal.PointLight, data["name"] + "_RoomLight", (x, y, z + 2.7))
    light.point_light_component.set_intensity(900)
    light.point_light_component.set_editor_property("attenuation_radius", 1350)
    light.point_light_component.set_editor_property("cast_shadows", False)
    light.point_light_component.set_light_color(unreal.LinearColor(1, 0.88, 0.7, 1))


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
