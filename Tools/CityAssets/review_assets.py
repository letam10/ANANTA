"""Render every delivered mesh and record independent geometry measurements."""
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets/City"
QA = ROOT / "Saved/QA/CityAssets"


def point_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def measure(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    report = dict(id=obj.name, vertices=len(mesh.vertices), triangles=len(mesh.loop_triangles),
                  zeroAreaFaces=sum(face.calc_area() < 1e-12 for face in bm.faces),
                  boundaryEdges=sum(edge.is_boundary for edge in bm.edges),
                  nonManifoldEdges=sum(not edge.is_manifold for edge in bm.edges),
                  uvLayers=len(mesh.uv_layers), materialSlots=[s.material.name for s in obj.material_slots])
    bm.free()
    return report


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT / "CityKit.blend"))
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    objects = [bpy.data.objects[entry["id"]] for entry in manifest["meshes"]]
    reports = [measure(obj) for obj in objects]
    for obj in objects:
        obj.hide_render = True
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.resolution_x = 480
    scene.render.resolution_y = 420
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.20, 0.20, 0.20)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.24, 0.27, 0.31, 1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.65
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 4.1
    for name, loc, energy, size in [("Key", (-3, -4, 6), 1100, 4), ("Fill", (4, -1, 3), 600, 3),
                                     ("Rim", (1, 4, 5), 900, 3)]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        point_at(light, (0, 0, 1))
    floor_material = bpy.data.materials.new("Review ground")
    floor_material.diffuse_color = (0.12, 0.15, 0.19, 1)
    floor_material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.12, 0.15, 0.19, 1)
    floor_material.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.8
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.015))
    floor = bpy.context.object
    floor.data.materials.append(floor_material)
    for obj in objects:
        display = obj.copy()
        display.data = obj.data
        bpy.context.collection.objects.link(display)
        display.hide_render = False
        bpy.context.view_layer.update()
        corners = [Vector(c) for c in obj.bound_box]
        low = Vector([min(p[i] for p in corners) for i in range(3)])
        high = Vector([max(p[i] for p in corners) for i in range(3)])
        factor = 2.8 / max(high - low)
        display.scale = (factor,) * 3
        display.location = (-(low.x + high.x) * factor / 2,
                            -(low.y + high.y) * factor / 2, -low.z * factor)
        target = Vector((0, 0, (high.z - low.z) * factor / 2))
        direction = Vector((4, -7, 3.1))
        if obj.name.startswith("Facade") or "Entry" in obj.name or obj.name == "Storefront":
            direction = Vector((2.6, -8, 2.5))
        camera.location = target + direction
        point_at(camera, target)
        scene.render.filepath = str(QA / (obj.name + ".png"))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(display, do_unlink=True)
    result = dict(blenderVersion=bpy.app.version_string, engine="Cycles", samples=24, meshes=reports)
    (QA / "geometry_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("RESULT " + json.dumps(dict(rendered=len(objects), zeroAreaFaces=sum(r["zeroAreaFaces"] for r in reports))))


if __name__ == "__main__":
    main()
