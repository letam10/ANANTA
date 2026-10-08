"""Validate actual texture exports; emissive is required only for window-bearing samples."""

import argparse
import json
from pathlib import Path
from PIL import Image, ImageStat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="City_HLOD/ANANTA_City_City_L0_X0_Y0")
    parser.add_argument("--require-emissive", action="store_true")
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[2]
    folder = project / "Saved/QA/CityHLODProxy" / args.label.split("/")[-1]
    readback = json.loads((folder / "Readback.json").read_text(encoding="utf-8"))
    if readback["errors"] or readback["label"] != args.label:
        raise RuntimeError("Proxy readback failed or selected label differs")
    report = dict(label=args.label, requireEmissive=args.require_emissive, textures=[], errors=[])
    emissive = []
    for component in readback["components"]:
        if component["triangles"] <= 0:
            report["errors"].append("Proxy has no rendered triangles")
        for material in component["materials"]:
            for binding in material["textures"]:
                path = Path(binding["export"])
                with Image.open(path) as source:
                    image = source.convert("RGB")
                stats = ImageStat.Stat(image)
                entry = dict(file=path.name, size=image.size, extrema=image.getextrema(),
                             mean=stats.mean, stddev=stats.stddev)
                report["textures"].append(entry)
                if list(image.size) != binding["size"]:
                    report["errors"].append(f"Texture export dimensions differ: {path.name}")
                if path.stem.endswith("_EmissiveColor"):
                    emissive.append(entry)
    # Cum khong co cua so co the bake emissive den hop le.
    if args.require_emissive:
        if not emissive:
            report["errors"].append("No emissive export")
        for entry in emissive:
            if max(high for low, high in entry["extrema"]) == 0:
                report["errors"].append("Window-bearing proxy emissive is black")
            if max(entry["stddev"]) == 0:
                report["errors"].append("Emissive texture has no spatial variation")
    (folder / "Pixels.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if report["errors"]:
        raise RuntimeError("\n".join(report["errors"]))
    print(f"CITY_HLOD_PROXY_PIXELS_OK textures={len(report['textures'])}")


if __name__ == "__main__":
    main()
