"""Deterministic finishing overrides and window dressing, in centimetres."""

from CityInteriorArchitecture import apply_architecture

FLOORS = {
    "Expansion_Clinic_Floor": "InteriorTerrazzo",
    "Expansion_Market_Floor": "InteriorTerrazzo",
    "Expansion_Transit_Floor": "InteriorTerrazzo",
    "Expansion_Workshop_Floor": "InteriorWorkshopConcrete",
}
SOFAS = {"Dressing_Bookshop_ReadingSofa", "Dressing_Gallery_VisitorsSofa"}
RUGS = {
    "Dressing_Apartment_DiningRug": (450, 370),
    "Dressing_Gallery_CatalogueRug": (330, 330),
}
CURTAIN_ROOMS = {"Apartment", "Clinic", "Bookshop"}


def finish_items(items, rooms):
    result = []
    for original in items:
        item = dict(original)
        if item["label"] in SOFAS:
            item["mesh"] = "House_GlamVelvetSofa"
        elif item["label"] in RUGS:
            width, depth = RUGS[item["label"]]
            item["mesh"] = "InteriorWovenRug"
            item["scale"] = (width / 300, depth / 200, 1)
            item["location"] = (*item["location"][:2], 15.05)
            item.pop("material", None)
        result.append(item)
    for room in rooms:
        if room["id"] not in CURTAIN_ROOMS:
            continue
        x, y = room["centre"]
        width, depth = room["size"]
        face = room["face"]
        bay = (depth - 400) / 2
        # Dat trong khung cua so, ngoai hanh lang giua phong rong 440 cm.
        for side in (-1, 1):
            result.append(dict(label=f"Dressing_{room['id']}_Curtain{side}",
                               mesh="InteriorLinenCurtain",
                               location=(x + face * (width / 2 - 42), y + side * (200 + bay / 2), 48),
                               yaw=90 * face, scale=(1, 1, 1), collision=False))
    return apply_architecture(result, rooms)
