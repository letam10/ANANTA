"""Forty independent orbit renders of the saved asset scene, CPU only."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from finishing_materials import digest

ROOT = HERE.parents[1]
OUT = ROOT / "Saved/QA/CityMetroAssets"


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "Assets/City/MetroDetails/MetroDetails.blend"))
    scene = bpy.context.scene
    assets = [o for o in scene.objects if o.type == "MESH"]
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("Review studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.17, .21, .28, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .7
    scene.view_settings.view_transform = "AgX"
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    scene.camera = camera
    lights = []
    for name, xyz, energy, size in [("Key", (5, -8, 12), 2200, 8), ("Fill", (0, 8, 8), 1500, 7),
                                   ("Rim", (-7, -2, 10), 1800, 6)]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = xyz
        point_at(obj, (0, 0, 1))
        lights.append(obj)
    records = []
    for obj in assets:
        for other in assets:
            other.hide_render = other != obj
        size = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
        target = Vector((0, 0, obj.dimensions.z * .45))
        camera.data.ortho_scale = size * 1.36
        for light in lights:
            light.data.energy *= (size / 8) ** 2
            light.location *= size / 8
            light.data.size *= size / 8
            point_at(light, target)
        for yaw in range(0, 360, 45):
            angle = math.radians(yaw)
            camera.location = target + Vector((math.cos(angle) * size, math.sin(angle) * size, size * .56))
            point_at(camera, target)
            path = OUT / f"{obj.name}_{yaw:03}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            records.append(dict(id=obj.name, yaw=yaw, elevationDegrees=29.25, file=path.name,
                                sha256=digest(path), cameraLocation=list(camera.location),
                                source="Actual Cycles CPU render of saved mesh"))
        for light in lights:
            light.data.energy /= (size / 8) ** 2
            light.location /= size / 8
            light.data.size /= size / 8
    assert len(records) == 40 and len({r["sha256"] for r in records}) == 40
    (OUT / "render_audit.json").write_text(json.dumps(dict(status="PASS", count=40,
        engine="Cycles CPU", samples=20, resolution=[800, 600], views=records,
        acceptance="Rendered evidence; visual acceptance must be recorded after inspecting images"), indent=2))
    print("METRO_RENDER_PASS 40")


if __name__ == "__main__":
    main()
