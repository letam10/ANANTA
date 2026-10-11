"""Import the validated sofa, rug and curtain after the active HLOD job ends."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from ImportCityAssets import import_mesh
from CityMaterials import create_material


def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "finishing_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1 and manifest["units"] == "cm"
    assert len(manifest["meshes"]) == 3
    report = dict(materials=[], meshes=[])
    for original in manifest["materials"]:
        item = dict(original)
        # Cac bien the vai dung chung texture, tranh nhan ban bo nho GPU.
        paths = [item.get(role) or "" for role in ("baseColor", "normal", "roughness", "ao")]
        if any("/Linen/" in path for path in paths):
            item["textureSetId"] = "Finish_Linen"
        elif any("/Velvet/" in path for path in paths):
            item["textureSetId"] = "Finish_VelvetNavy"
        report["materials"].append(create_material(item, source))
    for item in manifest["meshes"]:
        report["meshes"].append(import_mesh(item, source))
    report["runtimeVerified"] = False
    path = PROJECT / "Saved/QA/CityFinishingImport.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_FINISHING_IMPORT_OK meshes=3")


if __name__ == "__main__":
    main()
