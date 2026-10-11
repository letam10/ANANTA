"""Six distinct accessible venues and useful interactions in the continuous map."""

import unreal
from CityExpansionData import VENUES
from CityRooms import room
from CityScene import box, prop, text, spawn, mesh_asset


def service(identifier, kind, title, description, location, mesh="Bollard"):
    actor = spawn(unreal.CityServiceInteractable, "Expansion_Service_" + identifier, location)
    actor.set_editor_property("interaction_id", identifier)
    actor.set_editor_property("service_kind", getattr(unreal.CityServiceKind, kind.upper()))
    actor.set_editor_property("display_name", title)
    actor.set_editor_property("description", description)
    actor.visual_mesh.set_static_mesh(mesh_asset(mesh))
    actor.set_editor_property("is_spatially_loaded", True)
    return actor


def shelves(prefix, x, y, count=3):
    for index in range(count):
        xx = x + index * 270
        box(f"{prefix}_ShelfBack{index}", (xx, y, 130), (240, 30, 230), "City_oak_veneer_01")
        for row in range(4):
            z = 40 + row * 50
            box(f"{prefix}_Shelf{index}_{row}", (xx, y - 35, z), (240, 90, 8), "City_oak_veneer_01")
            for offset in (-75, 0, 75):
                prop("House_book_encyclopedia_set_01", f"{prefix}_Books{index}_{row}_{offset}",
                     (xx + offset, y - 35, z + 4))


def chairs(prefix, x, y, count=3):
    for index in range(count):
        prop("House_modern_arm_chair_01", f"{prefix}_Chair{index}", (x + index * 180, y, 15))


def furnish_venue(item):
    prefix = "Expansion_" + item["id"]
    x, y = item["centre"]
    width, depth = item["size"]
    front, _ = room(prefix, item["centre"], item["size"], item["face"], "CafeEntry")
    porch_x = front + item["face"] * 150
    box(prefix + "_Porch", (porch_x, y, 6), (350, 480, 12), "Sidewalk")
    text(prefix + "_Name", item["title"], (front + item["face"] * 38, y, 302),
         0 if item["face"] > 0 else 180, 24)
    prop("House_potted_plant_02", prefix + "_Plant", (front - item["face"] * 150, y + depth / 2 - 180, 15))
    back = x - item["face"] * (width / 2 - 180)
    if item["id"] == "Bookshop":
        shelves(prefix, x - 350, y + depth / 2 - 100)
        prop("CafeTable", prefix + "_ReadingTable", (x, y - 270, 15))
        prop("House_book_encyclopedia_set_01", prefix + "_ReadingBooks", (x, y - 270, 92))
        chairs(prefix, x - 200, y - 470, 2)
    elif item["id"] == "Clinic":
        prop("ApartmentBed", prefix + "_ExaminationBed", (back, y + 200, 15), 90)
        prop("CafeCounter", prefix + "_MedicalCabinet", (x, y + depth / 2 - 110, 15))
        chairs(prefix, x - 150, y - 490)
        box(prefix + "_Screen", (x + 200, y + 300, 130), (25, 420, 230), "InteriorPlaster")
        box(prefix + "_CrossVertical", (back + 40, y + 330, 225), (10, 25, 100), "ShellSage", False)
        box(prefix + "_CrossHorizontal", (back + 40, y + 330, 225), (10, 100, 25), "ShellSage", False)
    elif item["id"] == "Market":
        shelves(prefix, x - 380, y + depth / 2 - 100)
        prop("CafeCounter", prefix + "_Checkout", (x, y - 350, 15))
        for index in range(3):
            prop("House_ceramic_vase_03", prefix + f"_Goods{index}", (x - 90 + index * 90, y - 350, 121))
        prop("MarketStall", prefix + "_OutdoorStand", (front + item["face"] * 180, y - 1050, 15), 90)
    elif item["id"] == "ToyShop":
        shelves(prefix, x - 420, y + depth / 2 - 100, count=3)
        prop("CafeCounter", prefix + "_Checkout", (x, y - 350, 15))
        for index, (xx, yy) in enumerate(((-420, -820), (0, -760), (420, -820))):
            prop("ToyBlocks", prefix + f"_ToyBlocks{index}", (x + xx, y + yy, 45),
                 scale=(0.8, 0.8, 0.8), collision=False)
        prop("ToyBlocks", prefix + "_WindowDisplay", (front + item["face"] * 180, y - 860, 55),
             scale=(0.7, 0.7, 0.7), collision=False)
    elif item["id"] == "Salon":
        prop("CafeCounter", prefix + "_Reception", (x, y - 360, 15))
        for index, xx in enumerate((-360, 0, 360)):
            prop("MakeupCompact", prefix + f"_Compact{index}", (x + xx, y - 360, 82),
                 collision=False)
        prop("House_modern_arm_chair_01", prefix + "_ChairLeft", (x - 480, y + 360, 15), 90)
        prop("House_modern_arm_chair_01", prefix + "_ChairRight", (x + 480, y + 360, 15), 270)
        prop("House_potted_plant_02", prefix + "_Plant", (x + 650, y + 520, 15))
        prop("House_hanging_industrial_lamp", prefix + "_Lamp",
             (x, y + 250, 185), collision=False)
    elif item["id"] == "Gallery":
        for index, tint in enumerate(("ShellTerracotta", "ShellBlue", "ShellSage")):
            xx = x - 480 + index * 480
            box(prefix + f"_Frame{index}", (xx, y + depth / 2 - 35, 195), (310, 16, 190), "City_Brass")
            box(prefix + f"_Panel{index}", (xx, y + depth / 2 - 46, 195), (282, 8, 162), tint, False)
            # Phu dieu kien truc ba lop tao tac pham co chieu sau, khong can texture ban quyen.
            for step in range(4):
                box(prefix + f"_Relief{index}_{step}", (xx - 90 + step * 60, y + depth / 2 - 57, 170),
                    (35, 15, 70 + ((index + step) % 3) * 25), "City_stone_wall_02", False)
        prop("Bench", prefix + "_ViewingBench", (x, y - 250, 15))
        prop("House_ceramic_vase_03", prefix + "_Sculpture", (back, y, 120))
        box(prefix + "_Plinth", (back, y, 65), (90, 90, 100), "InteriorPlaster")
    elif item["id"] == "Workshop":
        prop("CarBody", prefix + "_DisplayCar", (x, y + 250, 15), 90, collision=True)
        prop("CafeCounter", prefix + "_Workbench", (x, y - depth / 2 + 110, 15))
        prop("RoofEquipment", prefix + "_Compressor", (back, y - 450, 15), scale=(0.65, 0.65, 0.65))
        prop("BikeRack", prefix + "_Rack", (front + item["face"] * 160, y - 1200, 15))
    elif item["id"] == "Library":
        shelves(prefix, x - 420, y + depth / 2 - 100, count=4)
        prop("CafeTable", prefix + "_ReadingTable", (x + 260, y - 280, 15))
        chairs(prefix, x - 60, y - 500, 3)
        prop("House_hanging_industrial_lamp", prefix + "_ReadingLamp",
             (x + 260, y - 280, 185), collision=False)
    elif item["id"] == "Restaurant":
        prop("CafeCounter", prefix + "_KitchenCounter", (x, y + depth / 2 - 120, 15))
        for index, xx in enumerate((x - 560, x, x + 560)):
            prop("CafeTable", prefix + f"_Table{index}", (xx, y - 360, 15))
            chairs(prefix, xx - 110, y - 560, 2)
        prop("House_vintage_electric_kettle", prefix + "_KitchenKettle",
             (x + 350, y + depth / 2 - 120, 120), collision=False)
    elif item["id"] == "Cinema":
        box(prefix + "_Screen", (x, y + depth / 2 - 45, 320),
            (width - 260, 18, 430), "DistrictNavy", False)
        for index, xx in enumerate((x - 560, x, x + 560)):
            prop("House_mid_century_lounge_chair", prefix + f"_Seat{index}",
                 (xx, y - 420, 15), yaw=180)
        prop("CafeCounter", prefix + "_TicketDesk", (x - 500, y, 15))
        prop("House_hanging_industrial_lamp", prefix + "_HallLamp",
             (x, y - 100, 185), collision=False)
    elif item["id"] == "Hotel":
        prop("House_sofa_03", prefix + "_LobbySofa", (x - 350, y - 360, 15), yaw=90)
        prop("CafeTable", prefix + "_LobbyTable", (x + 260, y - 360, 15))
        prop("ApartmentBed", prefix + "_RoomBed", (x + 380, y + 430, 15), 90)
        prop("House_hanging_industrial_lamp", prefix + "_LobbyLamp",
             (x - 350, y - 360, 185), collision=False)
    else:
        chairs(prefix, x - 350, y + 500, 4)
        prop("CafeCounter", prefix + "_InformationDesk", (x, y - 430, 15))
        text(prefix + "_Routes", "WEST MARKET / CENTRAL GARDENS / EASTLINE", (back + 20, y, 235), 0, 13)
        prop("BusShelter", prefix + "_Shelter", (x, y - 1300, 15), 90, collision=False)
    # Marker dat tren lo di, cach vat trang tri de tia kiem tra khong bi chan.
    service(item["serviceId"], item["service"], item["title"], item["description"],
            (front - item["face"] * 330, y, 80), mesh="House_book_encyclopedia_set_01"
            if item["service"] == "Read" else "House_ceramic_vase_03")


def furnish():
    for item in VENUES:
        furnish_venue(item)
    service("Cafe_Rest", "Rest", "NOVA coffee break", "Rested at NOVA. Health and progress restored.",
            (-26000, 2400, 100), "House_ceramic_vase_03")
    service("Apartment_Rest", "Rest", "Rest at home", "Home is a quiet place to recover and save progress.",
            (2200, 2600, 95), "House_book_encyclopedia_set_01")
