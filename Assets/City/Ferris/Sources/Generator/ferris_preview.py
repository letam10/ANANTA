"""CPU-only three-view contact sheet including a cabin closeup."""
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ferris_build import OUT, QA, write_json


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT / 'FerrisWheel.blend'))
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.render.resolution_x = 640
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    scene.world = bpy.data.worlds.new('Neutral preview world')
    scene.world.color = (.33, .33, .33)
    bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, -.02))
    mat = bpy.data.materials.new('Preview floor')
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.12, .14, .16, 1)
    bpy.context.object.data.materials.append(mat)
    for position, energy, size in (((25, -20, 48), 100000, 22), ((-25, 0, 35), 65000, 18)):
        data = bpy.data.lights.new('Softbox', 'AREA')
        data.energy = energy
        data.size = size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0, 0, 16))
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = 'ORTHO'
    scene.camera = camera
    frames = []
    views = [('front', (70, 0, 19), (0, 0, 17), 40),
             ('threequarter', (58, -40, 31), (0, 0, 17), 40),
             ('cabin', (6, -2, 2.8), (0, 0, 1.75), 4.8)]
    for name, position, target, scale in views:
        camera.location = position
        camera.data.ortho_scale = scale
        aim(camera, target)
        path = QA / f'{name}.png'
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        image = bpy.data.images.load(str(path), check_existing=False)
        values = np.empty(640 * 720 * 4, dtype=np.float32)
        image.pixels.foreach_get(values)
        frames.append(values.reshape(720, 640, 4))
    pixels = np.concatenate(frames, axis=1)
    sheet = bpy.data.images.new('Ferris CPU contact sheet', 1920, 720, alpha=False)
    sheet.pixels.foreach_set(pixels.ravel())
    sheet.filepath_raw = str(QA / 'contact-sheet.png')
    sheet.file_format = 'PNG'
    sheet.save()
    write_json(QA / 'render.json', dict(status='PASS', engine='Cycles CPU', samples=16,
               views=[v[0] for v in views], contactSheet='contact-sheet.png', runtimeVerified=False))
    print('RESULT CPU_RENDER_PASS', flush=True)


if __name__ == '__main__':
    main()
