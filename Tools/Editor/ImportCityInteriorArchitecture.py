"""Import four audited interior fixtures after the root agent's HLOD job completes."""
import hashlib
import json
from pathlib import Path
import sys

import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityMaterials import create_material
from ImportCityAssets import import_mesh


def main():
    source = PROJECT / "Assets/City"
    manifest = json.loads((source / "interior_architecture_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1 and manifest["units"] == "cm"
    assert len(manifest["meshes"]) == 4
    for entry in manifest["meshes"]:
        assert hashlib.sha256((source / entry["file"]).read_bytes()).hexdigest() == entry["sha256"]
    report = dict(materials=[], meshes=[], runtimeVerified=False)
    for entry in manifest["materials"]:
        assert entry["id"].startswith("Arch_")
        report["materials"].append(create_material(entry, source))
    for entry in manifest["meshes"]:
        result = import_mesh(entry, source)
        mesh = unreal.load_asset(result["asset"])
        bounds = mesh.get_bounding_box()
        actual_low = [bounds.min.x, bounds.min.y, bounds.min.z]
        actual_high = [bounds.max.x, bounds.max.y, bounds.max.z]
        expected = entry["boundsCm"]
        assert max(abs(a - b) for a, b in zip(actual_low, expected["min"])) < 0.1
        assert max(abs(a - b) for a, b in zip(actual_high, expected["max"])) < 0.1
        assert result["slots"] == len(entry["materialSlots"])
        report["meshes"].append(result)
    path = PROJECT / "Saved/QA/CityInteriorArchitectureAssets/import.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_INTERIOR_ARCHITECTURE_IMPORT_OK meshes=4")


if __name__ == "__main__":
    main()
