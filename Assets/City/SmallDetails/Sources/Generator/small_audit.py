"""Reopen all exported FBXs and independently audit geometry, UVs, hashes and views."""
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from finishing_materials import digest, build_materials
from small_build import BASE, OUT, QA, IDS, write_json
from small_review import render

DIMENSIONS = dict(CookingPot=(0, 22), Saucepan=(0, 36), KitchenBowl=(0, 17),
                  CoffeeMug=(2, 10), MakeupCompact=(1, 7), ToyBlocks=(0, 20),
                  RoomVase=(2, 22), BathroomSoap=(0, 12))


def inspect(obj, record):
    bpy.context.view_layer.update()
    data = obj.data
    points = [obj.matrix_world @ vertex.co for vertex in data.vertices]
    low = [min(p[i] for p in points) * 100 for i in range(3)]
    high = [max(p[i] for p in points) * 100 for i in range(3)]
    expected = record["boundsCm"]["min"] + record["boundsCm"]["max"]
    error = max(abs(a - b) for a, b in zip(low + high, expected))
    data.calc_loop_triangles()
    uv = data.uv_layers.active
    assert uv is not None
    zero_uv = 0
    degenerate = 0
    for tri in data.loop_triangles:
        a, b, c = [uv.data[index].uv.copy() for index in tri.loops]
        zero_uv += abs((b - a).cross(c - a)) < 1e-14
        a, b, c = [data.vertices[index].co for index in tri.vertices]
        degenerate += (b - a).cross(c - a).length < 1e-12
    topology = bmesh.new()
    topology.from_mesh(data)
    nonmanifold = sum(not edge.is_manifold for edge in topology.edges)
    consistent_winding = all(edge.is_contiguous for edge in topology.edges)
    topology.free()
    axis, dimension = DIMENSIONS[record["id"]]
    size_error = abs(high[axis] - low[axis] - dimension)
    report = dict(id=record["id"], triangles=len(data.loop_triangles), boundsMaxErrorCm=error,
                  specifiedDimensionCm=dimension, specifiedDimensionErrorCm=size_error,
                  materialSlots=[mat.name for mat in data.materials], zeroAreaUvTriangles=zero_uv,
                  degenerateTriangles=degenerate, nonmanifoldEdges=nonmanifold,
                  consistentWinding=consistent_winding,
                  triangulated=all(len(p.vertices) == 3 for p in data.polygons),
                  finiteVertices=all(math.isfinite(v) for p in points for v in p),
                  finiteNormals=all(math.isfinite(v) for n in data.corner_normals for v in n.vector),
                  unitNormals=all(abs(n.vector.length - 1) < .001 for n in data.corner_normals),
                  finiteUvs=all(math.isfinite(v) for p in uv.data for v in p.uv),
                  validateChanged=data.validate(verbose=False))
    assert error < .02 and size_error < .02, report
    assert zero_uv == degenerate == nonmanifold == 0, report
    assert consistent_winding and report["unitNormals"] and len(data.corner_normals) == len(data.loops), report
    assert report["triangles"] == record["triangles"] < 2000, report
    assert report["materialSlots"] == record["materialSlots"] and len(data.materials) <= 3, report
    assert all(report[k] for k in ("triangulated", "finiteVertices", "finiteNormals", "finiteUvs")), report
    assert not report["validateChanged"] and obj.location.length < .00001, report
    assert abs(low[2]) < .02 and abs(high[0] + low[0]) < .02 and abs(high[1] + low[1]) < .02, report
    return report


def main():
    manifest = json.loads((BASE / "small_manifest.json").read_text(encoding="utf-8"))
    assert set(r["id"] for r in manifest["meshes"]) == set(IDS)
    assert len(list((OUT / "Meshes").glob("*.fbx"))) == 8
    selected = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--rerender=")), [])
    rendering = "--render" in sys.argv or bool(selected)
    previous = json.loads((QA / "render_audit.json").read_text()) if selected else None
    reports = []
    for record in manifest["meshes"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path = BASE / record["file"]
        assert digest(path) == record["sha256"]
        bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
        assert len(meshes) == 1
        report = inspect(meshes[0], record)
        if rendering and (not selected or record["id"] in selected):
            build_materials(manifest["materials"], BASE)
            report["renders"] = render(record, QA)
        elif rendering:
            report["renders"] = next(r["renders"] for r in previous["meshes"] if r["id"] == record["id"])
        reports.append(report)
        print("AUDIT", record["id"], report["triangles"], flush=True)
    for source in manifest["sourceFiles"]:
        assert digest(BASE / source["file"]) == source["sha256"], source["file"]
    living = json.loads((BASE / "living_manifest.json").read_text(encoding="utf-8"))
    for material in manifest["materials"]:
        assert material in living["materials"]
        for role in ("baseColor", "normal", "roughness"):
            image = bpy.data.images.load(str(BASE / material[role]), check_existing=True)
            assert tuple(image.size) == (1024, 1024)
    assert not (OUT / "Textures").exists(), "Existing textures must be reused"
    result = dict(status="PASS", blender=bpy.app.version_string, meshes=reports,
                  sourceHashesVerified=len(manifest["sourceFiles"]),
                  reusedTextureChannels=9, runtime="Unreal integration is owned by main agent",
                  visualAcceptance="Render creation does not establish visual acceptance")
    if rendering:
        assert len(list(QA.glob("*_yaw*.png"))) == 64
        assert sum(len(r["renders"]) for r in reports) == 64
        for report in reports:
            for frame in report["renders"]:
                assert digest(Path(frame["file"])) == frame["sha256"]
        write_json(QA / "render_audit.json", result)
    write_json(QA / "audit.json", result)
    print("RESULT " + json.dumps(dict(status="PASS", meshes=8, renderCount=64 if rendering else 0)))


if __name__ == "__main__":
    main()
