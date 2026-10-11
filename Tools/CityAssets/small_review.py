"""Eight actual Cycles CPU views of each imported small FBX asset."""
import math
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from finishing_materials import digest


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render(record, directory):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.resolution_x = 480
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("Small prop QA studio")
    scene.world.color = (.22, .22, .22)
    dimensions = [v / 100 for v in record["boundsCm"]["size"]]
    extent = max(dimensions)
    target = Vector((0, 0, dimensions[2] * .5))
    bpy.ops.mesh.primitive_plane_add(size=extent * 200, location=(0, 0, -.001))
    floor = bpy.context.object
    mat = bpy.data.materials.new("QA neutral floor")
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.10, .12, .14, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
    floor.data.materials.append(mat)
    for index, (position, energy) in enumerate([((.8, -.8, 1.3), 100), ((-.6, .8, .8), 75)]):
        data = bpy.data.lights.new("Softbox" + str(index), "AREA")
        data.energy = extent * extent * energy
        data.size = extent * 1.0
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = Vector(position) * extent + target
        aim(light, target)
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    diagonal = math.hypot(dimensions[0], dimensions[1])
    elevation = math.atan2(1.2, 2)
    vertical = dimensions[2] * math.cos(elevation) + diagonal * math.sin(elevation)
    camera.data.ortho_scale = max(diagonal * 1.18, vertical * 1.18 / .75)
    scene.camera = camera
    frames = []
    for yaw in range(0, 360, 45):
        angle = math.radians(yaw)
        camera.location = target + Vector((math.cos(angle) * 2, math.sin(angle) * 2, 1.2)) * extent
        aim(camera, target)
        bpy.context.view_layer.update()
        # Kiem khung bang tam goc hop bao de khong cat mieng coc hay nap hop.
        for x in (-dimensions[0] / 2, dimensions[0] / 2):
            for y in (-dimensions[1] / 2, dimensions[1] / 2):
                for z in (0, dimensions[2]):
                    point = world_to_camera_view(scene, camera, Vector((x, y, z)))
                    assert .03 < point.x < .97 and .03 < point.y < .97, (record["id"], yaw, point)
        path = directory / f"{record['id']}_yaw{yaw:03d}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        frames.append(dict(yaw=yaw, file=str(path), sha256=digest(path),
                           width=480, height=360, engine="CYCLES", device="CPU", threads=2,
                           boundsInsideFrame=True))
    return frames
