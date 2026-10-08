"""Authored additions for the eight accessible interiors, in centimetres."""

from CityExpansionData import VENUES
from CityLayout import CAFE, APARTMENT
from CityInteriorFinishes import finish_items


ROOMS = ({"id": "Cafe", **CAFE}, {"id": "Apartment", **APARTMENT}) + VENUES
HOUSE = "House_"


def describe():
    result = []
    for room in ROOMS:
        name = room["id"]
        x, y = room["centre"]

        def add(label, mesh, dx, dy, z=15, yaw=0, scale=(1, 1, 1), collision=True, material=None):
            item = dict(label=f"Dressing_{name}_{label}", mesh=mesh, location=(x + dx, y + dy, z),
                        scale=scale, yaw=yaw, collision=collision)
            if material:
                item["material"] = material
            result.append(item)

        def box(label, dx, dy, z, size, material="City_oak_veneer_01", collision=True):
            add(label, "Cube", dx, dy, z, scale=tuple(v / 100 for v in size),
                collision=collision, material=material)

        def house(label, mesh, dx, dy, z=15, yaw=0, collision=True):
            add(label, HOUSE + mesh, dx, dy, z, yaw, collision=collision)

        def lounge(label, dx, dy, sofa="sofa_02"):
            house(label + "Sofa", sofa, dx, dy, yaw=180)
            house(label + "Table", "modern_coffee_table_01", dx, dy - 150, yaw=90)
            house(label + "Books", "book_encyclopedia_set_01", dx, dy - 150, 54, collision=False)

        def shelf(label, dx, dy, stock="book_encyclopedia_set_01"):
            box(label + "Back", dx, dy + 29, 115, (196, 8, 200))
            for side in (-1, 1):
                box(label + f"Side{side}", dx + side * 94, dy, 115, (8, 50, 200))
            for row, z in enumerate((38, 88, 138, 188)):
                box(label + f"Shelf{row}", dx, dy, z, (180, 50, 6))
                for column, offset in enumerate((-56, 16, 67)):
                    if stock == "book_encyclopedia_set_01" and column == 2:
                        continue
                    house(label + f"Stock{row}_{column}", stock, dx + offset, dy, z + 3,
                          collision=False)

        # Be mat do vat dich vu, khong tao va cham trong hanh lang giua phong.
        if name == "Cafe":
            sx, sy, top = 150, 0, 100
        elif name == "Apartment":
            sx, sy, top = -150, 100, 95
        else:
            sx = room["face"] * (room["size"][0] / 2 - 330)
            sy, top = 0, 80
        box("ServiceTop", sx, sy, top - 3, (110, 70, 6), collision=False)
        box("ServiceBase", sx, sy, (15 + top - 6) / 2, (60, 45, top - 21),
            "City_Dark", False)

        if name == "Cafe":
            lounge("Window", -330, 460)
            house("WindowChair", "dining_chair_02", -560, 360, yaw=90)
            house("CornerPlant", "potted_plant_02", -690, -460)
            house("WindowVase", "ceramic_vase_03", -280, 310, 54, collision=False)
            box("MenuFrame", -675, 540, 195, (180, 8, 120), "City_Brass", False)
            box("MenuPanel", -675, 534, 195, (162, 4, 102), "City_Teal", False)
            house("CounterPot", "brass_pot_01", -500, -220, 120, collision=False)
            house("TableBooks", "book_encyclopedia_set_01", 210, 380, 92, collision=False)
            house("WindowLamp", "hanging_industrial_lamp", -330, 430, 185, collision=False)
        elif name == "Apartment":
            add("DiningTable", "CafeTable", -530, -470)
            for index, (dx, dy, yaw) in enumerate(((-530, -600, 0), (-530, -340, 180),
                                                  (-680, -470, 90), (-380, -470, -90))):
                house(f"DiningChair{index}", "dining_chair_02", dx, dy, yaw=yaw)
            house("DiningPot", "brass_pot_01", -545, -470, 92, collision=False)
            house("DiningVase", "ceramic_vase_03", -490, -470, 92, collision=False)
            shelf("Study", -390, 710)
            add("StudyDesk", "CafeTable", -350, 410)
            house("DeskChair", "dining_chair_02", -350, 290, yaw=180)
            house("DeskBooks", "book_encyclopedia_set_01", -350, 410, 92, collision=False)
            house("BedroomTable", "modern_coffee_table_01", 850, 410)
            house("BedroomPlant", "potted_plant_02", 810, 670)
            house("BedroomVase", "ceramic_vase_03", 850, 410, 54, collision=False)
            box("DiningRug", -530, -475, 15.6, (450, 370, 1.2), "City_rough_linen", False)
        elif name == "Bookshop":
            shelf("Archive", -550, -610)
            lounge("Reading", 470, -460)
            house("ReadingChair", "mid_century_lounge_chair", 660, -330, yaw=-90)
            house("ArchivePlant", "potted_plant_02", -670, 370)
            add("NewArrivals", "CafeTable", -350, 320)
            house("NewBooks0", "book_encyclopedia_set_01", -380, 320, 92, collision=False)
            house("NewBooks1", "book_encyclopedia_set_01", -320, 320, 92, collision=False)
            house("NewArrivalsChair", "dining_chair_02", -530, 310, yaw=90)
            house("ReadingLamp", "hanging_industrial_lamp", 470, -440, 185, collision=False)
        elif name == "Clinic":
            lounge("Waiting", -410, 550)
            house("WaitingChair", "modern_arm_chair_01", -610, 380, yaw=90)
            house("WaitingPlant", "potted_plant_02", -590, -580)
            add("Reception", "CafeCounter", -410, -320)
            house("ReceptionChair", "dining_chair_02", -410, -600)
            house("ReceptionRecords", "book_encyclopedia_set_01", -435, -320, 120, collision=False)
            box("MedicalStorage", 410, 655, 107, (230, 65, 184), "City_white_plaster_rough_01")
            for index in range(3):
                box(f"StorageDoor{index}", 335 + index * 75, 619, 107,
                    (70, 5, 168), "City_Teal", False)
                box(f"StorageHandle{index}", 352 + index * 75, 615, 112,
                    (4, 3, 20), "City_Aluminium", False)
            house("StoragePot", "brass_pot_01", 350, 655, 199, collision=False)
            house("StorageRecords", "book_encyclopedia_set_01", 450, 655, 199, collision=False)
        elif name == "Market":
            shelf("Homewares", 600, -570, "brass_pot_01")
            add("StockIsland", "CafeCounter", -410, 340)
            for index, dx in enumerate((-505, -420, -335)):
                house(f"IslandPot{index}", "brass_pot_01", dx, 340, 120, collision=False)
            house("CashierChair", "dining_chair_02", 0, -490)
            house("CheckoutRecords", "book_encyclopedia_set_01", 0, -375, 120, collision=False)
            box("ProduceCrate0", -550, -540, 45, (95, 75, 60))
            box("ProduceCrate1", -430, -540, 45, (95, 75, 60))
            for index, dx in enumerate((-550, -430)):
                house(f"CratePot{index}", "brass_pot_01", dx, -540, 75, collision=False)
            house("ShopPlant", "potted_plant_02", 640, 360)
        elif name == "Gallery":
            for index, (dx, dy, height, asset) in enumerate(((420, 390, 95, "brass_pot_01"),
                                                          (-400, 390, 115, "ceramic_vase_03"),
                                                          (350, -530, 80, "ceramic_vase_03"))):
                box(f"ArtPlinth{index}", dx, dy, 15 + height / 2,
                    (100, 100, height), "City_white_plaster_rough_01")
                house(f"ArtObject{index}", asset, dx, dy, 15 + height, collision=False)
            lounge("Visitors", -440, -450)
            house("VisitorPlant", "potted_plant_02", -660, -550)
            house("GalleryChair", "mid_century_lounge_chair", 610, -460, yaw=-90)
            box("CatalogueRug", -440, -500, 15.6, (330, 330, 1.2), "City_denim_fabric", False)
        elif name == "Workshop":
            add("PartsBench", "CafeCounter", -500, 560, yaw=90)
            house("MechanicChair", "dining_chair_02", -300, 590, yaw=-90)
            house("Manuals", "book_encyclopedia_set_01", -500, 590, 120, yaw=90, collision=False)
            house("PartsPot", "brass_pot_01", -500, 510, 120, collision=False)
            house("BreakChair", "modern_arm_chair_01", -500, -510, yaw=90)
            house("BreakTable", "modern_coffee_table_01", -320, -550)
            house("BreakKettle", "vintage_electric_kettle", -320, -550, 54, collision=False)
            box("ToolBoard", 470, 835, 180, (280, 14, 140), "City_Dark", False)
            for index in range(6):
                box(f"ToolRail{index}", 360 + index * 44, 823, 180,
                    (12, 8, 65 + 10 * (index % 3)), "City_Aluminium", False)
            box("PartsCrate", 480, 680, 50, (140, 110, 70))
            house("CratePot", "brass_pot_01", 480, 680, 85, collision=False)
            house("WorkshopLamp", "hanging_industrial_lamp", -500, 560, 185, collision=False)
        else:
            lounge("Travellers", 460, 660, "sofa_03")
            house("TravelPlant", "potted_plant_02", 670, -640)
            house("DeskChair", "dining_chair_02", 0, -590)
            house("DeskTimetable", "book_encyclopedia_set_01", -60, -430, 120, collision=False)
            box("RouteFrame", -370, 795, 190, (370, 10, 150), "City_Brass", False)
            box("RouteBoard", -370, 787, 190, (350, 6, 130), "City_Teal", False)
            for index in range(4):
                box(f"RouteLine{index}", -370, 782, 151 + index * 25,
                    (275 - index * 24, 4, 5), "City_Aluminium", False)
                box(f"RouteStop{index}", -480 + index * 73, 778, 151 + index * 25,
                    (14, 4, 14), "City_Brass", False)
            add("TicketDesk", "CafeCounter", -500, -430, yaw=90)
            house("TicketChair", "dining_chair_02", -665, -430, yaw=90)
            house("TicketRecords", "book_encyclopedia_set_01", -500, -430, 120,
                  yaw=90, collision=False)
            house("TicketLamp", "hanging_industrial_lamp", -500, -430, 185, collision=False)
    return finish_items(result, ROOMS)


def dress():
    from CityScene import box, prop, material_asset

    actors = []
    for item in describe():
        if item["mesh"] == "Cube":
            actor = box(item["label"], item["location"], tuple(v * 100 for v in item["scale"]),
                        item["material"], item["collision"])
        else:
            actor = prop(item["mesh"], item["label"], item["location"], item["yaw"],
                         item["scale"], item["collision"])
            if item.get("material"):
                actor.static_mesh_component.set_material(0, material_asset(item["material"]))
        actors.append(actor)
    return actors
