"""Import only the new expansion kit and textured architectural colour variants."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from ImportCityAssets import import_mesh
from CityMaterials import create_material
from CityExpansionBuildings import TINTS, STYLES


def main():
    root = PROJECT / "Assets/City"
    base = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    extra = json.loads((root / "expansion_manifest.json").read_text(encoding="utf-8"))
    source = {item["id"]: item for item in base["materials"] + extra["materials"]}
    report = dict(materials=[], meshes=[])
    for item in extra["materials"]:
        report["materials"].append(create_material(item, root))
    colours = ((0.82, 0.76, 0.61), (0.61, 0.30, 0.19), (0.35, 0.48, 0.36),
               (0.26, 0.31, 0.38), (0.65, 0.52, 0.33), (0.32, 0.46, 0.53))
    for name, tint in zip(TINTS, colours):
        item = {**source["City_white_plaster_rough_01"], "id": name, "baseColorFactor": tint,
                "textureSetId": "City_white_plaster_rough_01"}
        report["materials"].append(create_material(item, root))
    for mesh in base["meshes"] + extra["meshes"]:
        if mesh["id"] not in STYLES or mesh["id"] == "FacadeTower":
            continue
        original = source[mesh["materialSlots"][0]]
        for name, tint in zip(TINTS, colours):
            item = {**original, "id": f"V_{mesh['id']}_{name}", "textureSetId": original["id"],
                    "baseColorFactor": tint}
            report["materials"].append(create_material(item, root))
    soil = {**source["City_stone_wall_02"], "id": "GardenSoil", "worldTileCm": 300,
            "baseColorFactor": [0.11, 0.20, 0.085]}
    report["materials"].append(create_material(soil, root))
    for item in extra["meshes"]:
        report["meshes"].append(import_mesh(item, root))
    (PROJECT / "Saved/QA/CityExpansionImport.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_EXPANSION_IMPORT_OK meshes={len(report['meshes'])}")


if __name__ == "__main__":
    main()
