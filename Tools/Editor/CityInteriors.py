"""Only the cafe and apartment contain rooms and furnishings."""

from CityScene import box, prop, text, spawn, mesh_asset, material_asset
from CityRooms import room
from CityLayout import CAFE, APARTMENT
import unreal


def furniture(available, prefix, asset, location, yaw=0):
    name = f"House_{asset}"
    if name not in available:
        raise RuntimeError(f"Interior furniture absent from manifest: {name}")
    return prop(name, prefix + "_" + asset, location, yaw)


def furnish(manifest):
    available = {item["id"] for item in manifest["meshes"]}
    room("City_Cafe", **CAFE, entry="CafeEntry")
    box("City_Cafe_Terrace", (-25125, 2400, 6), (450, 2300, 12), "Sidewalk")
    text("City_Cafe_Name", "NOVA / COFFEE", (-25318, 2400, 294), 0, 31)
    for index, yy in enumerate((2020, 2780)):
        prop("CafeTable", f"City_Cafe_Table{index}", (-25950, yy, 15))
        furniture(available, f"City_Cafe_Seat{index}", "mid_century_lounge_chair", (-26110, yy, 15), 90)
        furniture(available, f"City_Cafe_Chair{index}", "mid_century_lounge_chair", (-25790, yy, 15), -90)
    furniture(available, "City_Cafe", "sofa_03", (-26400, 2000, 15))
    furniture(available, "City_Cafe", "potted_plant_02", (-25470, 2900, 15))
    furniture(available, "City_Cafe", "ceramic_vase_03", (-25950, 2020, 92))
    for index, yy in enumerate((2280, 2574)):
        prop("CafeCounter", f"City_Cafe_Counter{index}", (-26650, yy, 15), 90)
    furniture(available, "City_Cafe", "vintage_electric_kettle", (-26650, 2400, 120))
    room("City_Apartment", **APARTMENT, entry="ApartmentEntry")
    box("City_Apartment_Porch", (1125, 2500, 6), (450, 450, 12), "Sidewalk")
    text("City_Apartment_Name", "RESIDENCE / 01", (1318, 2500, 294), 180, 30)
    furniture(available, "City_Apartment", "sofa_02", (2700, 1930, 15))
    furniture(available, "City_Apartment", "modern_coffee_table_01", (2700, 2200, 15))
    furniture(available, "City_Apartment", "modern_arm_chair_01", (2300, 2200, 15), 90)
    furniture(available, "City_Apartment", "potted_plant_02", (1520, 3180, 15))
    furniture(available, "City_Apartment", "book_encyclopedia_set_01", (2700, 2200, 65))
    prop("ApartmentBed", "City_Apartment_Bed", (3000, 2870, 15))


def mission():
    giver = spawn(unreal.ANANTACityInteractable, "City_MissionGiver", (-25000, 2400, 110))
    giver.set_editor_property("interaction_id", "Giver_Cafe")
    giver.set_editor_property("interaction_kind", unreal.CityInteractionKind.GIVER)
    giver.visual_mesh.set_static_mesh(mesh_asset("Bollard"))
    positions = ((-12000, 1800, 100), (1000, 1800, 100), (24500, 2400, 100))
    for index, position in enumerate(positions, 1):
        clue = spawn(unreal.ANANTACityInteractable, f"City_Clue_{index:02}", position)
        clue.set_editor_property("interaction_id", f"Clue_{index:02}")
        clue.set_editor_property("interaction_kind", unreal.CityInteractionKind.CLUE)
        clue.visual_mesh.set_static_mesh(mesh_asset("Bollard"))
        clue.visual_mesh.set_material(0, material_asset("Anomaly"))
    for index, offset in enumerate(((-400, 0), (400, 0), (0, 450)), 1):
        enemy = spawn(unreal.ANANTACityEnemy, f"City_Enemy_{index:02}",
                      (26000 + offset[0], 4500 + offset[1], 110))
        enemy.set_editor_property("enemy_id", f"Enemy_{index:02}")
    shard = spawn(unreal.ANANTACityInteractable, "City_AnomalyFragment", (26000, 4500, 100))
    shard.set_editor_property("interaction_id", "Fragment_Anomaly")
    shard.set_editor_property("interaction_kind", unreal.CityInteractionKind.FRAGMENT)
    shard.visual_mesh.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cone"))
    shard.visual_mesh.set_material(0, material_asset("Anomaly"))
    text("City_Transit_Name", "EASTLINE / TRANSIT", (26000, 7200, 500), -90, 110)
    car = spawn(unreal.ANANTACityVehicle, "City_PlayerCar", (-22000, 500, 70))
    car.set_editor_property("vehicle_id", "PlayerCar")
    car.set_editor_property("is_spatially_loaded", False)
    car.body_mesh.set_static_mesh(mesh_asset("CarBody"))
    crowd = spawn(unreal.ANANTACityCrowd, "City_Crowd")
    crowd.set_editor_property("traffic_mesh", mesh_asset("CarBody"))
    crowd.set_editor_property("is_spatially_loaded", False)
    start = spawn(unreal.PlayerStart, "City_PlayerStart", (-25000, 1500, 120), 90)
    start.set_editor_property("is_spatially_loaded", False)
