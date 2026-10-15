"""Render eight equally spaced viewpoints of every owned model."""

import json
import math
import hashlib
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]


def main():
    source = ROOT / "Assets" / "CoastalUpgrade" / "CoastalModels.blend"
    output = ROOT / "Saved" / "Upgrade" / "ModelViews"
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    models = sorted(list(bpy.context.scene.objects), key=lambda obj: obj.name)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 8
    scene.render.resolution_x = 400
    scene.render.resolution_y = 400
    scene.render.resolution_percentage = 100
    scene.world.color = (0.14, 0.14, 0.14)
    scene.view_settings.view_transform = "AgX"
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(4, -4, 8))
    light = bpy.context.object
    light.data.energy = 1500
    light.data.shape = "DISK"
    light.data.size = 7
    coverage = []
    for obj in models:
        for candidate in models:
            candidate.hide_render = candidate != obj
        extent = max(obj.dimensions.length, 0.3)
        center = Vector((0, 0, obj.dimensions.z / 2))
        camera.data.ortho_scale = extent * 1.22
        light.location = center + Vector((extent, -extent, extent * 1.5))
        light.data.energy = 250 * extent * extent
        light.data.size = extent
        light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
        paths = []
        for index in range(8):
            angle = index * math.tau / 8
            camera.location = center + Vector((math.cos(angle), math.sin(angle), 0.5)) * extent * 2
            camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
            scene.render.filepath = str(output / f"{obj.name}_{index}.png")
            bpy.ops.render.render(write_still=True)
            paths.append(scene.render.filepath)
        mesh_source = ROOT / "Assets" / "CoastalUpgrade" / f"{obj.name}.fbx"
        coverage.append({"model": obj.name, "azimuth_degrees": list(range(0, 360, 45)), "views": paths,
                         "source_sha256": hashlib.sha256(mesh_source.read_bytes()).hexdigest()})
    (output / "coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    print(f"MODEL_VIEW_COVERAGE_OK {len(coverage)} models x 8 views")


if __name__ == "__main__":
    main()
