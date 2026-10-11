"""Build the original clinic and visitor fixtures; never invoke Unreal."""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Matrix

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import finishing_materials as materials
import venue_fixture_geometry as geometry

ROOT = HERE.parents[1]
BASE = ROOT / "Assets/City"
OUT = BASE / "VenueFixtures"
QA = ROOT / "Saved/QA/CityVenueFixtureAssets"
TARGETS = {"ClinicSupplyCabinet": ([230, 74, 184], 7000), "TransitRouteDisplay": ([370, 24, 150], 4000)}

def write_json(path, value):
    serialized = json.dumps(value, indent=2)
    serialized = re.sub(r"\[\s*([-\d.,\s]+)\]",
                        lambda match: "[" + re.sub(r"\s+", " ", match.group(1)).strip() + "]", serialized)
    path.write_text(serialized + "\n", encoding="utf-8")

def material_records():
    prefix = "VenueFixtures/Textures/"
    records = [materials.entry("VenueFixture_Enamel", (.64, .71, .67, 1), .48),
               materials.entry("VenueFixture_Teal", (.025, .115, .119, 1), .62),
               materials.entry("VenueFixture_Steel", (.59, .63, .65, 1), .32, 1),
               materials.entry("VenueFixture_SupplyLabels", (1, 1, 1, 1), .80,
                               baseColor=prefix + "SupplyLabels.png"),
               materials.entry("VenueFixture_Guide", (1, 1, 1, 1), .83,
                               baseColor=prefix + "NeighborhoodGuide.png")]
    for item in records:
        item["source"] = "Original ANANTA venue fixture geometry, material design and vector artwork"
        item["license"] = "Original project asset"
    return records

def export(obj):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = [round(min(v[i] for v in points) * 100, 4) for i in range(3)]
    hi = [round(max(v[i] for v in points) * 100, 4) for i in range(3)]
    obj.data.calc_loop_triangles()
    entry = dict(id=obj.name, file=f"VenueFixtures/Meshes/{obj.name}.fbx",
                 boundsCm=dict(min=lo, max=hi, size=[round(hi[i] - lo[i], 4) for i in range(3)]),
                 materialSlots=[s.material.name for s in obj.material_slots],
                 triangles=len(obj.data.loop_triangles), visibleFront="-Y",
                 source="Original ANANTA venue fixture design", license="Original project asset")
    size, budget = TARGETS[obj.name]
    assert len(entry["materialSlots"]) <= 4 and entry["triangles"] <= budget, entry
    assert max(abs(a - b) for a, b in zip(entry["boundsCm"]["size"], size)) < .01, entry
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.data.transform(Matrix.Scale(100, 4))
    bpy.context.scene.unit_settings.scale_length = .01
    path = BASE / entry["file"]
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"},
                             axis_forward="X", axis_up="Z", use_space_transform=True,
                             global_scale=1, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             bake_space_transform=False, mesh_smooth_type="FACE", use_tspace=True,
                             add_leaf_bones=False, bake_anim=False, path_mode="STRIP")
    obj.data.transform(Matrix.Scale(.01, 4))
    bpy.context.scene.unit_settings.scale_length = 1
    entry["sha256"] = materials.digest(path)
    entry["lodRecommendation"] = dict(screenSizes=[1, .4, .15], triangleRatios=[1, .5, .2])
    return entry

def main():
    assert bpy.app.version >= (5, 2, 0)
    for path in (OUT / "Meshes", OUT / "Sources/Generator", QA):
        path.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    records = material_records()
    materials.build_materials(records, BASE)
    for mat in bpy.data.materials:
        if mat.name.startswith("VenueFixture_"):
            uv = mat.node_tree.nodes.new("ShaderNodeUVMap")
            uv.uv_map = "UVMap"
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    mat.node_tree.links.new(uv.outputs["UV"], node.inputs["Vector"])
    entries = [export(geometry.cabinet()), export(geometry.display())]
    scripts = list(HERE.glob("venue_fixture_*.py"))
    scripts += [HERE / name for name in ("geometry.py", "workshop_detail_geometry.py", "finishing_materials.py")]
    scripts.append(ROOT / "Tools/Editor/ImportCityVenueFixtures.py")
    for source in scripts:
        shutil.copy2(source, OUT / "Sources/Generator" / source.name)
    provenance = dict(geometry="Original authored geometry; planar folded parts and applied micro bevels",
                      artwork="Original Pillow vector artwork; Windows Arial glyph rasterization",
                      pbr="Original constant coated enamel, matte print and brushed steel parameters",
                      coordinateSource="Tools/Editor/CityVenueDressing.py ROOMS",
                      license="Original project asset", thirdPartyTextures=[])
    write_json(OUT / "Sources/Provenance.json", provenance)
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(OUT))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "VenueFixtures.blend"))
    sources = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and "Meshes" not in path.parts:
            sources.append(dict(file=path.relative_to(BASE).as_posix(), sha256=materials.digest(path),
                                source="Original venue fixture source", license="Original project asset"))
    guide = json.loads((OUT / "Sources/GuideCoordinates.json").read_text())
    manifest = dict(schemaVersion=1, units="cm", upAxis="Z", forwardAxis="X", meshes=entries,
                    materials=records, sourceFiles=sources, guideVenueCoordinates=guide)
    write_json(BASE / "venue_fixture_manifest.json", manifest)
    write_json(QA / "build.json", dict(status="PASS", meshes=entries))
    print("RESULT " + json.dumps(dict(status="PASS", meshes=entries)))

if __name__ == "__main__":
    main()
