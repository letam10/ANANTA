"""Shared authored dimensions and venues for the expanded continuous city."""

import math

BLOCK = 12000
GRID_EXTENT = 336000
WORLD_EXTENT = 240000 * math.sqrt(2)
GRID_BLOCKS = GRID_EXTENT * 2 // BLOCK
ROAD_LINES = tuple(range(-GRID_EXTENT, GRID_EXTENT + 1, BLOCK))
SEED = 81026

# Cua quay ve truc duong doc gan nhat; khong doi cac moc nhiem vu cu.
VENUES = (
    dict(id="Bookshop", centre=(-38150, 2700), size=(1600, 1400), face=1,
         title="PAPER LANTERN / BOOKS", service="Read", serviceId="Bookshop_Read",
         description="The Eastline archive records an unusual signal beneath the old station."),
    dict(id="Clinic", centre=(-9750, 2550), size=(1600, 1500), face=-1,
         title="AOBA / NEIGHBOURHOOD CLINIC", service="Heal", serviceId="Clinic_Heal",
         description="Neighbourhood medical station. Health restored."),
    dict(id="Market", centre=(-21750, -2800), size=(1700, 1400), face=-1,
         title="EVERYDAY / CORNER MARKET", service="Supplies", serviceId="Market_Supplies",
         description="A sealed neighbourhood supply parcel has been added to your bag."),
    dict(id="Gallery", centre=(14200, 2550), size=(1700, 1500), face=-1,
         title="FRAME / CITY GALLERY", service="Read", serviceId="Gallery_Read",
         description="These city studies trace the river district before the transit expansion."),
    dict(id="Workshop", centre=(38200, 2500), size=(1700, 1800), face=-1,
         title="NORTHSTAR / MOTOR WORKS", service="Read", serviceId="Workshop_Read",
         description="Workshop notes: brake before leaving the car and keep junctions clear."),
    dict(id="Transit", centre=(62200, 2500), size=(1700, 1700), face=-1,
         title="EASTLINE / VISITOR CENTRE", service="Read", serviceId="Transit_Read",
         description="Eastline connects the market streets, gardens and eastern business district."),
)


def reserved_rectangles():
    result = [(-27800, 1100, -24800, 3800), (700, 1200, 3900, 4000),
              (21500, 1000, 30500, 8400)]
    for item in VENUES:
        x, y = item["centre"]
        w, d = item["size"]
        result.append((x - w / 2 - 350, y - d / 2 - 350,
                       x + w / 2 + 350, y + d / 2 + 350))
    from CityCivicDistrict import RESERVES as CIVIC
    from CityCoastalDistrict import RESERVES as COAST
    from CityMetroDistrict import RESERVES as METRO
    result.extend(CIVIC)
    result.extend(COAST)
    result.extend(METRO)
    return result


def coastal_cutout(x, y):
    return x >= 120000 and y <= -120000


def street_cutout(x, y):
    from CityMetroDistrict import AIRPORT

    left, bottom, right, top = AIRPORT
    return coastal_cutout(x, y) or left < x < right and bottom < y < top


def overlaps_reserved(x, y, width, depth, margin=0):
    return any(x + width / 2 + margin > left and x - width / 2 - margin < right
               and y + depth / 2 + margin > bottom and y - depth / 2 - margin < top
               for left, bottom, right, top in reserved_rectangles())
