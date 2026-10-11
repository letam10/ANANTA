"""Build only expansion meshes and preserve the existing city kit."""
import hashlib
import json
import sys
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import build_city_assets as existing
import materials
import expansion_architecture as architecture
import expansion_nature as nature
import expansion_props as props

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "Expansion"
QA = ROOT / "Saved/QA/CityExpansionAssets"


def main():
    assert bpy.app.version >= (5, 2, 0), bpy.app.version_string
    for path in (OUT / "Meshes", OUT / "Sources", QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = "METRIC"
    catalog = json.loads((BASE / "source_catalog.json").read_text(encoding="utf-8"))
    materials.build(catalog["materials"], BASE)
    objects = [architecture.brick_arch(), architecture.bay(), architecture.art_deco(),
               architecture.industrial(), architecture.civic(), nature.tree(), nature.tree(True), props.bus_shelter(),
               props.market_stall(), props.trash_bin(), props.bike_rack(), props.street_sign()]
    existing.OUT = OUT
    records = []
    for obj in objects:
        entry = existing.export(obj, source="Original ANANTA expansion generator")
        entry["file"] = "Expansion/" + entry["file"]
        entry.pop("collision")
        if obj.name.startswith("Facade"):
            assert entry["triangles"] < 6000, entry
            assert abs(entry["boundsCm"]["size"][0] - 400) < 0.1, entry
            assert abs(entry["boundsCm"]["size"][2] - 320) < 0.1, entry
            assert entry["boundsCm"]["size"][1] < 150, entry
        elif obj.name.startswith("Tree"):
            assert entry["triangles"] < 15000, entry
            assert 600 <= entry["boundsCm"]["size"][2] <= 900, entry
            assert 350 <= max(entry["boundsCm"]["size"][:2]) <= 650, entry
        else:
            assert entry["triangles"] < 12000, entry
        records.append(entry)
    sources = []
    scripts = list(HERE.glob("expansion_*.py"))
    scripts += [HERE / name for name in ("geometry.py", "materials.py", "build_city_assets.py")]
    for script in sorted(scripts):
        target = OUT / "Sources" / script.name
        target.write_bytes(script.read_bytes())
        sources.append(dict(file=target.relative_to(BASE).as_posix(),
                            sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                            source="Original project generator", license="Original project asset"))
    doc = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=records,
               materials=[], sourceFiles=sources)
    (BASE / "expansion_manifest.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "CityExpansion.blend"))
    result = dict(passed=True, blender=bpy.app.version_string, meshes=len(records),
                  triangles={x["id"]: x["triangles"] for x in records})
    (QA / "build.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(result))


if __name__ == "__main__":
    main()
