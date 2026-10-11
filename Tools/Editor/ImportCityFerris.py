"""Import the audited Ferris wheel and generate the three recommended LODs."""
import hashlib
import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / 'Tools/Editor'))
from CityMaterials import create_material
from ImportCityAssets import import_mesh


def main():
    source = PROJECT / 'Assets/City'
    manifest = json.loads((source / 'ferris_manifest.json').read_text(encoding='utf-8'))
    assert manifest['schemaVersion'] == 1 and manifest['units'] == 'cm'
    assert manifest['upAxis'] == 'Z' and manifest['forwardAxis'] == 'X'
    assert [item['id'] for item in manifest['meshes']] == ['FerrisWheel']
    for entry in manifest['meshes'] + manifest['sourceFiles']:
        actual = hashlib.sha256((source / entry['file']).read_bytes()).hexdigest()
        assert actual == entry['sha256'], entry['file']
    report = dict(materials=[], meshes=[], runtimeVerified=False)
    for entry in manifest['materials']:
        report['materials'].append(create_material(entry, source))
    entry = manifest['meshes'][0]
    result = import_mesh(entry, source)
    mesh = unreal.load_asset(result['asset'])
    bounds = mesh.get_bounding_box()
    minimum, maximum = entry['boundsCm']['min'], entry['boundsCm']['max']
    for actual, expected in ((bounds.min, (minimum[0], -maximum[1], minimum[2])),
                             (bounds.max, (maximum[0], -minimum[1], maximum[2]))):
        assert max(abs(a - b) for a, b in zip((actual.x, actual.y, actual.z), expected)) < 1
    editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if not editor:
        editor = unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
    recommendation = entry['lodRecommendation']
    reductions = [unreal.StaticMeshReductionSettings(percent_triangles=ratio, screen_size=screen)
                  for ratio, screen in zip(recommendation['triangleRatios'], recommendation['screenSizes'])]
    editor.set_lods(mesh, unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,
                                                          reduction_settings=reductions))
    assert editor.get_lod_count(mesh) == 3
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    result.update(lods=editor.get_lod_count(mesh), collisionAcceptance='Root placement owns collision')
    report['meshes'].append(result)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    path = PROJECT / 'Saved/QA/CityFerrisAssets/import.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    unreal.log('CITY_FERRIS_IMPORT_OK meshes=1 lods=3')


if __name__ == '__main__':
    main()
