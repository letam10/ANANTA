"""Create the labelled original fleet CPU review sheet from audited renders."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "Saved/QA/CityMobilityAssets"
ORDER = ["Coach", "CityBus", "Taxi", "PoliceCar", "BoxTruck", "CargoTruck", "TankerTruck", "Ambulance",
         "CargoShip", "Motorboat", "Sailboat", "DetailedPlanter", "DetailedStreetLamp", "TrafficSignal",
         "RoadBarrier", "HarborBollard", "BusStopSign"]
sheet = Image.new("RGB", (2400, 2180), (27, 33, 43))
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 23)
for index, name in enumerate(ORDER):
    x = index % 4 * 600
    y = index // 4 * 436
    image = Image.open(QA / f"{name}_threequarter.png").convert("RGB")
    sheet.paste(image, (x, y))
    draw.text((x + 16, y + 404), name, font=font, fill=(230, 237, 239))
sheet.save(QA / "mobility_contact_sheet.jpg", quality=94)
print(QA / "mobility_contact_sheet.jpg")
