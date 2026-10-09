"""PBR district finishes sharing the existing city texture sets."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FINISHES = (
    ("DistrictLimestone", "City_stone_wall_02", (0.72, 0.77, 0.78)),
    ("DistrictFireBrick", "City_brick_wall_001", (0.80, 0.34, 0.24)),
    ("DistrictNavy", "City_white_plaster_rough_01", (0.07, 0.17, 0.26)),
    ("DistrictTeal", "City_white_plaster_rough_01", (0.08, 0.45, 0.43)),
    ("DistrictPlaster", "City_white_plaster_rough_01", (0.82, 0.77, 0.65)),
    ("DistrictTimber", "City_oak_veneer_01", (0.52, 0.34, 0.20)),
    ("DistrictPaving", "City_Paving", (0.58, 0.60, 0.58)),
    ("DistrictSand", "City_white_plaster_rough_01", (0.83, 0.68, 0.43)),
    ("DistrictContainerRed", "City_white_plaster_rough_01", (0.62, 0.12, 0.07)),
    ("DistrictContainerBlue", "City_white_plaster_rough_01", (0.06, 0.28, 0.42)),
    ("DistrictYellow", "City_white_plaster_rough_01", (0.91, 0.58, 0.08)),
    ("DistrictPink", "City_white_plaster_rough_01", (0.21, 0.035, 0.055)),
)
SOLIDS = (
    dict(id="DistrictSteel", baseColorFactor=[0.13, 0.17, 0.20], metallicFactor=0.8, roughnessFactor=0.36),
    dict(id="DistrictWater", baseColorFactor=[0.025, 0.17, 0.23], roughnessFactor=0.17),
    dict(id="DistrictNeon", baseColorFactor=[0.06, 0.50, 0.55], emissiveFactor=[0.05, 1.9, 2.3]),
)
MATERIAL_IDS = tuple(item[0] for item in FINISHES) + tuple(item["id"] for item in SOLIDS)


def definitions():
    catalogue = json.loads((ROOT / "Assets/City/manifest.json").read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in catalogue["materials"]}
    result = []
    for name, source_id, tint in FINISHES:
        source = sources[source_id]
        # Dung lai texture, khong nhan ban tep anh cho tung mau son.
        item = {**source, "id": name, "textureSetId": source_id, "baseColorFactor": list(tint)}
        if name in ("DistrictPaving", "DistrictSand"):
            item["worldTileCm"] = 220 if name == "DistrictPaving" else 350
        elif name in ("DistrictTimber", "DistrictPink", "DistrictFireBrick", "DistrictLimestone"):
            item["worldBoxTileCm"] = 200
        result.append(item)
    return result + [dict(item) for item in SOLIDS]


def create():
    from CityMaterials import create_material
    from RefineCityCoastalMaterials import main as refine_coast

    result = [create_material(item, ROOT / "Assets/City") for item in definitions()]
    refine_coast()
    return result
