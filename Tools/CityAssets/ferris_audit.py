"""Independent FBX roundtrip geometry, UV, physical bounds and source-hash audit."""
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ferris_build import BASE, OUT, QA, digest, write_json


def main():
    manifest = json.loads((BASE / 'ferris_manifest.json').read_text(encoding='utf-8'))
    record = manifest['meshes'][0]
    for entry in manifest['meshes'] + manifest['sourceFiles']:
        assert digest(BASE / entry['file']) == entry['sha256'], entry['file']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(BASE / record['file']), use_custom_normals=True)
    objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    assert len(objects) == 1
    obj = objects[0]
    data = obj.data
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ vertex.co for vertex in data.vertices]
    low = [min(p[i] for p in points) * 100 for i in range(3)]
    high = [max(p[i] for p in points) * 100 for i in range(3)]
    error = max(abs(a - b) for a, b in zip(low + high, record['boundsCm']['min'] + record['boundsCm']['max']))
    data.calc_loop_triangles()
    uv = data.uv_layers.active
    assert uv
    degenerate = 0
    zero_uv = 0
    for tri in data.loop_triangles:
        a, b, c = [data.vertices[i].co for i in tri.vertices]
        degenerate += (b - a).cross(c - a).length < 1e-12
        a, b, c = [uv.data[i].uv.copy() for i in tri.loops]
        zero_uv += abs((b - a).cross(c - a)) < 1e-14
    topology = bmesh.new()
    topology.from_mesh(data)
    nonmanifold = sum(not edge.is_manifold for edge in topology.edges)
    loose = sum(not vertex.link_faces for vertex in topology.verts)
    topology.free()
    report = dict(status='PASS', triangles=len(data.loop_triangles), boundsMaxErrorCm=error,
                  materialSlots=[m.name for m in data.materials], degenerateTriangles=degenerate,
                  zeroAreaUvTriangles=zero_uv, nonmanifoldEdges=nonmanifold, looseVertices=loose,
                  finiteVertices=all(math.isfinite(v) for p in points for v in p),
                  finiteNormals=all(math.isfinite(v) for p in data.corner_normals for v in p.vector),
                  finiteUvs=all(math.isfinite(v) for p in uv.data for v in p.uv),
                  allFacesTriangulated=all(len(p.vertices) == 3 for p in data.polygons),
                  hashesVerified=len(manifest['sourceFiles']) + 1,
                  intersections='Intended manufactured overlapping joints; no boolean union requirement',
                  runtimeVerified=False)
    assert error < .02 and degenerate == zero_uv == nonmanifold == loose == 0, report
    assert report['triangles'] == record['triangles'] <= 60000, report
    assert report['materialSlots'] == record['materialSlots'] and len(data.materials) == 5, report
    assert all(report[k] for k in ('finiteVertices', 'finiteNormals', 'finiteUvs', 'allFacesTriangulated'))
    assert obj.location.length < .00001 and abs(low[2]) < .02 and abs(high[2] - 3385) < .02
    for item in manifest['materials']:
        for role in ('baseColor', 'normal', 'roughness'):
            image = bpy.data.images.load(str(BASE / item[role]), check_existing=True)
            assert tuple(image.size) == (1024, 1024)
    report['texturesVerified'] = 15
    write_json(QA / 'audit.json', report)
    print('RESULT ' + json.dumps(report))


if __name__ == '__main__':
    main()
