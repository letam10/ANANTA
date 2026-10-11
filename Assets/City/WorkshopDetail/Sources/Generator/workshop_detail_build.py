"""Build portable workshop source assets without editing Unreal Content."""
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
import workshop_detail_geometry as geometry

ROOT = HERE.parents[1]
BASE = ROOT / 'Assets/City'
OUT = BASE / 'WorkshopDetail'
QA = ROOT / 'Saved/QA/CityWorkshopDetailAssets'
TARGETS = {'WorkshopToolBoard': ([280, 14, 140], 8000), 'WorkshopPartsCrate': ([140, 110, 70], 5000)}


def material_records():
    prefix = 'WorkshopDetail/Textures/'
    records = [materials.entry('Workshop_Wood', (1, 1, 1, 1), .78,
               baseColor=prefix + 'Wood/color.png', normal=prefix + 'Wood/normal.png',
               roughness=prefix + 'Wood/roughness.png'),
               materials.entry('Workshop_Panel', (.037, .072, .065, 1), .55),
               materials.entry('Workshop_Steel', (.53, .56, .58, 1), .34, 1),
               materials.entry('Workshop_Grip', (.38, .14, .026, 1), .58),
               materials.entry('Workshop_Markings', (1, 1, 1, 1), .88,
                               baseColor=prefix + 'WorkshopLabels.png')]
    for item in records:
        wood = item['id'] == 'Workshop_Wood'
        item['source'] = 'https://polyhaven.com/a/wood_floor' if wood else 'Original ANANTA workshop design'
        item['license'] = 'CC0-1.0' if wood else 'Original project asset'
    return records


def main():
    assert bpy.app.version >= (5, 2, 0)
    for path in (OUT / 'Meshes', OUT / 'Sources/Generator', QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    records = material_records()
    materials.build_materials(records, BASE)
    objects = [geometry.toolboard(), geometry.crate()]
    existing.OUT = OUT
    entries = []
    for obj in objects:
        entry = existing.export(obj, 'Original ANANTA workshop geometry and labels')
        entry['file'] = 'WorkshopDetail/' + entry['file']
        entry['visibleFront'] = '-Y'
        entry.pop('collision')
        target, budget = TARGETS[obj.name]
        assert len(entry['materialSlots']) <= 4, entry
        assert entry['triangles'] <= budget, entry
        assert max(abs(a - b) for a, b in zip(entry['boundsCm']['size'], target)) < .01, entry
        entries.append(entry)
    for source in sorted(HERE.glob('workshop_detail_*.py')):
        shutil.copy2(source, OUT / 'Sources/Generator' / source.name)
    for name in ('geometry.py', 'build_city_assets.py', 'finishing_materials.py'):
        shutil.copy2(HERE / name, OUT / 'Sources/Generator' / name)
    sources = []
    for path in sorted(OUT.rglob('*')):
        if path.is_file() and path.suffix != '.blend' and 'Meshes' not in path.parts:
            wood = 'Wood' in path.parts
            sources.append(dict(file=path.relative_to(BASE).as_posix(), sha256=materials.digest(path),
                           source='https://polyhaven.com/a/wood_floor' if wood else 'Original ANANTA workshop source',
                           license='CC0-1.0' if wood else 'Original project asset'))
    manifest = dict(schemaVersion=1, units='cm', upAxis='Z', forwardAxis='X', meshes=entries,
                    materials=records, sourceFiles=sources)
    (BASE / 'workshop_detail_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'WorkshopDetail.blend'))
    blend = OUT / 'WorkshopDetail.blend'
    sources.append(dict(file=blend.relative_to(BASE).as_posix(), sha256=materials.digest(blend),
                        source='Original ANANTA workshop authoring scene', license='Original project asset'))
    (BASE / 'workshop_detail_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (QA / 'build.json').write_text(json.dumps(dict(passed=True, meshes=entries), indent=2), encoding='utf-8')
    print('RESULT ' + json.dumps(dict(passed=True, meshes=entries)))


if __name__ == '__main__':
    main()
