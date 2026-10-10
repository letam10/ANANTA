"""Write five real-scene camera directions for each new vehicle placement."""

import json
import argparse
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityExpansionLayout import generate
from CityInteractiveTransit import ROWBOAT
from CitySmallDetails import describe as small_placements
from CityMetroDistrict import FACILITIES
from CityLayout import APARTMENT


def cameras(name, location, size, yaw, minimum=400):
    radius = max(minimum, math.hypot(size[0], size[1]) * .9)
    target = [location[0], location[1], location[2] + size[2] * .45]
    if name == "Rowboat":
        target[2] -= 25
    result = []
    for direction, angle, elevation in (("front", 0, .35), ("rear", 180, .35),
                                         ("left", -90, .35), ("right", 90, .35), ("upper", 45, 1.1)):
        if name == "Rowboat" and direction == "upper":
            angle = -45
        radians = math.radians(yaw + angle)
        eye_z = target[2] + radius * elevation
        if name == "PassengerTrain":
            # Mai ga thap nhat 567,5 cm; giu camera duoi mai, tren muc san ga.
            eye_z = 530 if direction == "upper" else 350
        elif name == "Rowboat" and direction == "right":
            # Goc phia cau tau can cao hon de tia nhin khong cat qua mat ben.
            eye_z = location[2] + 1000
        eye = [target[0] + math.cos(radians) * radius,
               target[1] + math.sin(radians) * radius, eye_z]
        delta = [target[i] - eye[i] for i in range(3)]
        pitch = math.degrees(math.atan2(delta[2], math.hypot(delta[0], delta[1])))
        facing = math.degrees(math.atan2(delta[1], delta[0]))
        result.append(dict(id=name, direction=direction, location=eye, rotation=[pitch, facing, 0]))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("metro", "small", "facilities"), default="metro")
    parser.add_argument("--diagnostic", choices=("None", "NaniteShadowAsyncOn"), default="None")
    parser.add_argument("--asset", choices=("All", "Rowboat"), default="All")
    args = parser.parse_args()
    scope = args.scope
    if args.asset != "All" and scope != "metro":
        parser.error("Selected asset capture requires metro scope")
    placements = []
    views = []
    if scope == "metro":
        manifest = json.loads((ROOT / "Assets/City/metro_manifest.json").read_text(encoding="utf-8"))
        meshes = {item["id"]: item for item in manifest["meshes"]}
        layout = generate()
        for group in layout["groups"]:
            if group["mesh"] in meshes:
                for item in group["instances"]:
                    placements.append((group["mesh"], item["location"], item["yaw"]))
        placements += [("Rowboat", ROWBOAT, 90),
                       ("PassengerTrain", (-68000, 198500, 51), 0),
                       ("PassengerTrain", (-64000, 197500, 51), 180)]
        if args.asset != "All":
            placements = [item for item in placements if item[0] == args.asset]
        for name, location, yaw in placements:
            views.extend(cameras(name, location, meshes[name]["boundsCm"]["size"], yaw))
    elif scope == "small":
        source = json.loads((ROOT / "Assets/City/small_manifest.json").read_text(encoding="utf-8"))
        meshes = {item["id"]: item for item in source["meshes"]}
        placements = small_placements()
        living = json.loads((ROOT / "Assets/City/living_manifest.json").read_text(encoding="utf-8"))
        meshes.update({item["id"]: item for item in living["meshes"]})
        ax, ay = APARTMENT["centre"]
        placements.append(dict(mesh="KitchenSink", location=(ax + 720, ay - 585, 73.25), yaw=0))
        for item in placements:
            name = item["mesh"]
            views.extend(cameras(name, item["location"], meshes[name]["boundsCm"]["size"], item["yaw"], 100))
    else:
        placements = FACILITIES
        for item in placements:
            left, bottom, right, top = item["bounds"]
            height = 4800 if item["id"] == "Hotel" else 1800
            size = (right - left, top - bottom, height)
            if item["id"] == "Highway":
                size = (8000, top - bottom, 300)
            views.extend(cameras(item["id"], (*item["centre"], 0), size, 0))
    assert 0 < len(views) <= 200 and len(views) == len(placements) * 5
    for index, view in enumerate(views):
        view["image"] = f"View_{index:02d}.png"
    result = dict(schemaVersion=1, placements=len(placements), views=views,
                  scope="Real scene camera plan; visual inspection pending", accepted=False,
                  diagnostic=args.diagnostic, asset=args.asset)
    suffix = "" if args.asset == "All" else f"_{args.asset}"
    suffix += "" if args.diagnostic == "None" else f"_{args.diagnostic}"
    path = ROOT / f"Saved/QA/CityPlacement_{scope}{suffix}/Manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(dict(placements=len(placements), views=len(views), manifest=str(path))))


if __name__ == "__main__":
    main()
