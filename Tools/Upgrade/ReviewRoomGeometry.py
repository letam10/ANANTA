"""Five-view geometry review from exact saved-map placements, without launching UE gameplay."""

import ast
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]


def palette():
    source = ast.parse((ROOT / "Tools/Upgrade/coastal_materials.py").read_text(encoding="utf-8"))
    colors = next(ast.literal_eval(node.value) for node in source.body
                  if isinstance(node, ast.Assign) and any(
                      isinstance(target, ast.Name) and target.id == "COLORS" for target in node.targets))
    result = {}
    for name, rgba in colors.items():
        material = bpy.data.materials.new("Review_" + name)
        material.use_nodes = True
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (*rgba[:3], 1)
        shader.inputs["Roughness"].default_value = rgba[3]
        if name == "WindowGlass":
            shader.inputs["Alpha"].default_value = 0.12
        result["M_" + name] = material
    return result


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "Assets/CoastalUpgrade/CoastalModels.blend"))
    originals = {obj.name: obj for obj in list(bpy.context.scene.objects)}
    for obj in originals.values():
        obj.hide_render = True
    layout_path = ROOT / "Saved/Upgrade/city-layout.json"
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    output = ROOT / "Saved/Upgrade/RoomGeometry" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output.mkdir(parents=True, exist_ok=True)
    materials = palette()
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.world.color = (0.2, 0.2, 0.2)
    scene.view_settings.view_transform = "AgX"
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "PERSP"
    camera.data.lens = 18
    camera.data.clip_start = 0.03
    scene.camera = camera
    bpy.ops.object.light_add(type="SUN")
    sun = bpy.context.object
    sun.rotation_euler = (0.65, -0.45, -0.6)
    sun.data.energy = 2
    sun.data.angle = 0.08
    views = []
    for building in layout["buildings"]:
        if "rooms" not in building:
            continue
        center_x, center_y = building["center_m"]
        ground = building["ground_m"]
        instances = []
        for item in layout["placements"]:
            horizontal, depth, height = item["position_m"]
            if abs(horizontal - center_x) > building["width_m"] / 2 + 0.6:
                continue
            if abs(depth - center_y) > building["depth_m"] / 2 + 0.6:
                continue
            if item["mesh"] == "Cube":
                bpy.ops.mesh.primitive_cube_add(size=1)
                obj = bpy.context.object
                obj.data.materials.append(materials[item["material"]])
            elif item["mesh"] in originals:
                source = originals[item["mesh"]]
                obj = bpy.data.objects.new("Placed_" + item["mesh"], source.data)
                scene.collection.objects.link(obj)
            else:
                continue
            obj.location = (horizontal - center_x, depth - center_y, height - ground)
            obj.scale = item["scale"]
            # UE pitch dương nâng +X; Blender quay Y âm mới cùng chiều.
            obj.rotation_euler = (0, -math.radians(item.get("pitch", 0)), math.radians(item["yaw"]))
            instances.append(obj)
        for limits in building["rooms"].values():
            bpy.ops.object.light_add(type="AREA")
            light = bpy.context.object
            light.location = ((limits[0] + limits[1]) / 2, (limits[2] + limits[3]) / 2, 2.8)
            light.data.energy = 350
            light.data.shape = "DISK"
            light.data.size = 2
            instances.append(light)
        for view in layout["review_views"]:
            if not view["name"].startswith(building["name"] + "_"):
                continue
            position = Vector(view["position_m"]) - Vector((center_x, center_y, ground))
            target = Vector(view["target_m"]) - Vector((center_x, center_y, ground))
            camera.location = position
            camera.rotation_euler = (target - position).to_track_quat("-Z", "Y").to_euler()
            scene.render.filepath = str(output / (view["name"] + ".png"))
            bpy.ops.render.render(write_still=True)
            views.append(view)
        for obj in instances:
            bpy.data.objects.remove(obj, do_unlink=True)
    report = {"mode": "blender_exact_mesh_placement_geometry_only", "views": views,
              "folder": str(output), "lighting_verified_in_unreal": False,
              "source_layout": str(layout_path), "map_built_at": layout["built_at"]}
    (output / "coverage.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "Saved/Upgrade/latest-room-geometry.txt").write_text(str(output), encoding="utf-8")
    print(f"ROOM_GEOMETRY_VIEWS_OK {len(views)} views; not Unreal gameplay or lighting acceptance")


if __name__ == "__main__":
    main()
