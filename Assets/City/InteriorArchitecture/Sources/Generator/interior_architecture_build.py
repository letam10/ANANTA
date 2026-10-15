"""Build and export architecture fixtures without editing Unreal Content."""
import json
import shutil
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import build_city_assets as existing
import finishing_materials as materials
import interior_architecture_geometry as geometry

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "InteriorArchitecture"
QA = ROOT / "Saved/QA/CityInteriorArchitectureAssets"
TARGETS = {
    "InteriorServiceDesk": ([110, 70, 85], 6000),
    "InteriorSlatPanel": ([240, 8, 220], 5000),
    "InteriorGalleryFrame": ([140, 6, 110], 3000),
    "InteriorBotanicalFrame": ([140, 6, 110], 3000),
}


def material_records():
    records = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))["materials"]
    oak = dict(next(item for item in records if item["id"] == "City_wood_floor"))
    oak["id"] = "Arch_Oak"
    oak["source"] = "https://polyhaven.com/a/wood_floor"
    oak["license"] = "CC0-1.0"
    for role, filename in (("baseColor", "color"), ("normal", "normal"), ("roughness", "roughness")):
        oak[role] = f"InteriorArchitecture/Textures/Oak/{filename}.png"
    records = [oak,
               materials.entry("Arch_Graphite", (0.018, 0.024, 0.027, 1), 0.7),
               materials.entry("Arch_Brass", (0.61, 0.43, 0.20, 1), 0.3, 1),
               materials.entry("Arch_Stone", (0.57, 0.55, 0.48, 1), 0.4),
               materials.entry("Arch_Matboard", (0.81, 0.78, 0.69, 1), 0.94)]
    for name in ("Gallery", "Botanical"):
        records.append(materials.entry("Arch_" + name, (1, 1, 1, 1), 0.88,
                       baseColor=f"InteriorArchitecture/Textures/{name}Original.png"))
    for record in records:
        record.setdefault("source", "Original ANANTA interior architecture design")
        record.setdefault("license", "Original project asset")
    return records


def prepare_uv(obj):
    uv = obj.data.uv_layers.active
    # UV go theo toa do X/Z, giu van doc tren nan va canh tu.
    assert all(abs(value) < 100 for loop in uv.data for value in loop.uv)


def main():
    assert bpy.app.version >= (5, 2, 0)
    for path in (OUT / "Meshes", OUT / "Sources/Generator", QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    records = material_records()
    materials.build_materials(records, BASE)
    objects = [geometry.service_desk(), geometry.slat_panel(),
               geometry.art_frame("InteriorGalleryFrame", "Arch_Gallery"),
               geometry.art_frame("InteriorBotanicalFrame", "Arch_Botanical")]
    existing.OUT = OUT
    entries = []
    for obj in objects:
        prepare_uv(obj)
        entry = existing.export(obj, "Original ANANTA interior architecture geometry and art")
        entry["file"] = "InteriorArchitecture/" + entry["file"]
        entry["visibleFront"] = "-Y"
        entry.pop("collision")
        target, budget = TARGETS[obj.name]
        assert entry["triangles"] <= budget, entry
        assert max(abs(a - b) for a, b in zip(entry["boundsCm"]["size"], target)) < 0.1, entry
        entries.append(entry)
    sources = []
    for source in sorted(HERE.glob("interior_architecture_*.py")):
        dest = OUT / "Sources/Generator" / source.name
        shutil.copy2(source, dest)
    for source in (HERE / "geometry.py", HERE / "build_city_assets.py", HERE / "finishing_materials.py"):
        shutil.copy2(source, OUT / "Sources/Generator" / source.name)
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.suffix != ".blend" and "Meshes" not in path.parts:
            is_wood = "Oak" in path.parts
            source = records[0]["source"] if is_wood else "Original ANANTA architecture generator or print"
            license_name = "CC0-1.0" if is_wood else "Original project asset"
            sources.append(dict(file=path.relative_to(BASE).as_posix(), sha256=materials.digest(path),
                                source=source, license=license_name))
    catalog = json.loads((BASE / "source_catalog.json").read_text(encoding="utf-8"))
    sources += [record for record in catalog["sourceFiles"] if "/wood_floor/" in record["file"]]
    manifest = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=entries,
                    materials=records, sourceFiles=sources)
    (BASE / "interior_architecture_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "InteriorArchitecture.blend"))
    (QA / "build.json").write_text(json.dumps(dict(passed=True, meshes=entries), indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(dict(passed=True, meshes=entries)))


if __name__ == "__main__":
    main()
