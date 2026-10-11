"""Detailed service desks and authored accents on solid interior walls."""


# Moi bo tri dung tuong dac; mat truoc co cua so duoc de trong.
WALL_DETAILS = {
    "Cafe": (
        ("SouthPrint", "Gallery", "south", 120, 150),
        ("SouthBotanical", "Botanical", "south", 360, 150),
        ("WindowSlats", "Slat", "north", 320, 62),
        ("NorthPrint", "Gallery", "north", 60, 155),
    ),
    "Apartment": (
        ("DiningPrint", "Botanical", "south", -530, 150),
        ("LivingSlats", "Slat", "south", 350, 62),
        ("LivingPrint", "Gallery", "south", 70, 150),
        ("BedroomPrint", "Botanical", "back", 480, 155),
        ("StudyPrint", "Gallery", "north", 10, 150),
    ),
    "Bookshop": (
        ("ReadingPrint", "Gallery", "south", 450, 155),
        ("ReadingBotanical", "Botanical", "south", 190, 155),
        ("ArchiveSlats", "Slat", "back", -440, 62),
        ("ArrivalsPrint", "Botanical", "back", 330, 155),
    ),
    "Clinic": (
        ("WaitingBotanical", "Botanical", "north", -410, 155),
        ("WaitingPrint", "Gallery", "north", -650, 155),
        ("ReceptionSlats", "Slat", "south", -410, 62),
        ("ReceptionBotanical", "Botanical", "south", -100, 155),
        ("RecoveryPrint", "Botanical", "back", -410, 155),
    ),
    "Market": (
        ("ProduceBotanical", "Botanical", "south", -490, 155),
        ("CheckoutPrint", "Gallery", "south", -180, 155),
        ("HomewaresSlats", "Slat", "back", -400, 62),
        ("StockPrint", "Botanical", "back", 380, 155),
    ),
    "ToyShop": (
        ("ToyShopSlats", "Slat", "back", -420, 62),
        ("ToyPoster", "Gallery", "south", -120, 155),
        ("ToyPosterTwo", "Gallery", "south", 220, 155),
        ("ToyBotanical", "Botanical", "north", 380, 155),
    ),
    "Gallery": (
        ("VisitorSlats", "Slat", "south", -440, 62),
        ("CataloguePrint", "Gallery", "south", -110, 155),
        ("CityStudyPrint", "Gallery", "south", 220, 155),
        ("GardenStudyPrint", "Botanical", "south", 510, 155),
        ("SculpturePrint", "Gallery", "back", 400, 155),
    ),
    "Workshop": (
        ("BreakSlats", "Slat", "south", -500, 62),
        ("MotorStudyPrint", "Gallery", "south", 10, 150),
        ("PartsStudyPrint", "Gallery", "north", -500, 150),
        ("MotorSlats", "Slat", "back", 440, 62),
    ),
    "Transit": (
        ("VisitorSlats", "Slat", "north", 460, 62),
        ("TicketPrint", "Gallery", "south", -500, 155),
        ("InformationPrint", "Gallery", "south", 0, 155),
        ("GardenPrint", "Botanical", "south", 330, 155),
        ("TravelPrint", "Gallery", "back", 440, 155),
    ),
    "Library": (
        ("ArchiveSlats", "Slat", "back", -420, 62),
        ("ReadingPrint", "Gallery", "south", -360, 155),
        ("MapPrint", "Gallery", "south", 20, 155),
        ("BotanicalPrint", "Botanical", "north", 380, 155),
    ),
    "Restaurant": (
        ("KitchenSlats", "Slat", "north", -420, 62),
        ("MenuPrint", "Gallery", "south", -360, 155),
        ("DiningPrint", "Gallery", "south", 20, 155),
        ("NightBotanical", "Botanical", "back", 380, 155),
    ),
    "Cinema": (
        ("LobbySlats", "Slat", "north", -430, 62),
        ("PosterPrint", "Gallery", "south", -360, 155),
        ("PosterPrintTwo", "Gallery", "south", 20, 155),
        ("ProjectionPrint", "Gallery", "back", 380, 155),
    ),
    "Hotel": (
        ("LobbySlats", "Slat", "south", -430, 62),
        ("LobbyPrint", "Gallery", "north", -360, 155),
        ("ReceptionPrint", "Gallery", "north", 20, 155),
        ("RoomBotanical", "Botanical", "back", 380, 155),
    ),
}
DETAIL_MESHES = {
    "Slat": "InteriorSlatPanel",
    "Gallery": "InteriorGalleryFrame",
    "Botanical": "InteriorBotanicalFrame",
}


def wall_detail(room, name, kind, wall, offset, height):
    x, y = room["centre"]
    width, depth = room["size"]
    face = room["face"]
    # Mat quay vao phong; bounds cach mep trong 22 cm de tranh len chan tuong.
    if wall == "back":
        location = (x - face * (width / 2 - 28), y + offset, height)
        yaw = -90 * face
    else:
        side = 1 if wall == "north" else -1
        location = (x + offset, y + side * (depth / 2 - 28), height)
        yaw = 180 if side > 0 else 0
    return dict(label=f"Dressing_{room['id']}_{name}", mesh=DETAIL_MESHES[kind],
                location=location, yaw=yaw, scale=(1, 1, 1), collision=False)


def apply_architecture(items, rooms):
    result = []
    for original in items:
        if original["label"].endswith("_ServiceBase"):
            continue
        item = dict(original)
        if item["label"].endswith("_ServiceTop"):
            top = item["location"][2] + item["scale"][2] * 50
            item.update(label=item["label"].replace("_ServiceTop", "_ServiceDesk"),
                        mesh="InteriorServiceDesk", location=(*item["location"][:2], 15),
                        scale=(1, 1, (top - 15) / 85), collision=False)
            item.pop("material", None)
        result.append(item)
    for room in rooms:
        for detail in WALL_DETAILS[room["id"]]:
            result.append(wall_detail(room, *detail))
    return result
