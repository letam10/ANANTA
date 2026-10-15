"""Author and export the complete metre-authored mobility fleet in background Blender."""
import json
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Matrix

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from finishing_materials import digest
import mobility_materials
import mobility_roads
import mobility_boats
import mobility_props

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "Mobility"
QA = ROOT / "Saved/QA/CityMobilityAssets"
ROAD = ["Coach", "CityBus", "Taxi", "BoxTruck", "CargoTruck", "TankerTruck", "PoliceCar", "Ambulance"]
VESSELS = ["CargoShip", "Motorboat", "Sailboat"]
PROPS = ["DetailedPlanter", "DetailedStreetLamp", "TrafficSignal", "RoadBarrier", "HarborBollard", "BusStopSign"]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def export(obj):
    if obj.name in ROAD:
        offset = .05 - min(v.co.z for v in obj.data.vertices)
        obj.data.transform(Matrix.Translation((0, 0, offset)))
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    low = [round(min(v[i] for v in points) * 100, 4) for i in range(3)]
    high = [round(max(v[i] for v in points) * 100, 4) for i in range(3)]
    obj.data.calc_loop_triangles()
    budget = 25000 if obj.name in ROAD else 40000 if obj.name in VESSELS else 12000
    record = dict(id=obj.name, file=f"Mobility/Meshes/{obj.name}.fbx",
                  boundsCm=dict(min=low, max=high, size=[round(high[i] - low[i], 4) for i in range(3)]),
                  triangles=len(obj.data.loop_triangles), materialSlots=[m.name for m in obj.data.materials],
                  source="Original ANANTA mobility authored geometry", license="Original project asset",
                  lodRecommendation=dict(screenSizes=[1, .40, .16], triangleRatios=[1, .5, .2]),
                  triangleBudget=budget, forwardAxis="X", origin="waterline" if obj.name in VESSELS else "ground")
    assert record["triangles"] <= budget and len(record["materialSlots"]) <= 6, record
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.data.transform(Matrix.Scale(100, 4))
    bpy.context.scene.unit_settings.scale_length = .01
    path = BASE / record["file"]
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"},
                             axis_forward="X", axis_up="Z", use_space_transform=True,
                             global_scale=1, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             bake_space_transform=False, mesh_smooth_type="FACE", use_tspace=True,
                             add_leaf_bones=False, bake_anim=False, path_mode="STRIP")
    obj.data.transform(Matrix.Scale(.01, 4))
    bpy.context.scene.unit_settings.scale_length = 1
    record["sha256"] = digest(path)
    return record


def main():
    assert bpy.app.version >= (5, 2, 0)
    print("BLENDER_VERSION", bpy.app.version_string)
    for path in (OUT / "Meshes", OUT / "Sources/Generator", QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    materials = mobility_materials.prepare(BASE, OUT)
    entries = []
    for name in ROAD:
        if name in ("Coach", "CityBus"):
            obj = mobility_roads.bus(name)
        elif name in ("Taxi", "PoliceCar"):
            obj = mobility_roads.sedan(name)
        else:
            obj = mobility_roads.truck(name)
        entries.append(export(obj))
    for builder in (mobility_boats.cargo_ship, mobility_boats.motorboat, mobility_boats.sailboat,
                    mobility_props.planter, mobility_props.lamp, mobility_props.signal,
                    mobility_props.barrier, mobility_props.bollard, mobility_props.bus_stop):
        entries.append(export(builder()))
    provenance = dict(geometry="Original shaped profiles, multi-chine hulls, manufactured components and trim",
                      textures="Original deterministic NumPy enamel palette, rubber tread, steel grain, seat weave",
                      typography="Windows Arial outlines converted to mesh; font binary is not redistributed",
                      license="Original project asset", thirdPartyAssets=[],
                      authoring="Blender 5.2 metres; FBX vertices converted to centimetres with unit metadata",
                      lods="Recommendations only; engine mesh reduction generates lower LODs during import",
                      glass="opacity .23, twoSided true; visible upholstered passenger seating")
    write_json(OUT / "Sources/Provenance.json", provenance)
    for source in list(HERE.glob("mobility_*.py")) + [HERE / "geometry.py", HERE / "finishing_materials.py"]:
        shutil.copy2(source, OUT / "Sources/Generator" / source.name)
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "Mobility.blend"))
    sources = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and "Meshes" not in path.parts:
            sources.append(dict(file=path.relative_to(BASE).as_posix(), sha256=digest(path),
                                source="Original ANANTA mobility source", license="Original project asset"))
    manifest = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=entries,
                    materials=materials, sourceFiles=sources)
    write_json(BASE / "mobility_manifest.json", manifest)
    write_json(QA / "build.json", dict(status="PASS", blender=bpy.app.version_string, meshes=entries))
    print("RESULT " + json.dumps(dict(status="PASS", counts=len(entries),
                                      triangles={e["id"]: e["triangles"] for e in entries})))


if __name__ == "__main__":
    main()
