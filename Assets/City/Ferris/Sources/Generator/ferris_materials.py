"""Original 1K PBR paint, brushed stainless and blue glazing microstructure."""
import bpy
import numpy as np


def save_image(path, rgb, colour):
    pixels = np.ones((1024, 1024, 4), dtype=np.float32)
    pixels[:, :, :3] = np.clip(rgb, 0, 1)
    image = bpy.data.images.new(path.stem, 1024, 1024, alpha=False)
    image.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
    image.pixels.foreach_set(pixels.ravel())
    image.filepath_raw = str(path)
    image.file_format = 'PNG'
    image.save()
    return image


def prepare(base, out):
    directory = out / 'Textures'
    directory.mkdir(parents=True, exist_ok=True)
    y, x = np.mgrid[0:1024, 0:1024].astype(np.float32)
    noise = np.random.default_rng(881024).normal(0, 1, x.shape).astype(np.float32)
    grain = .5 * noise + .3 * np.sin(x * .1) * np.cos(y * .021)
    records = []
    for name, tint, rough, metallic in (
            ('Ivory', (.79, .77, .66), .38, 0), ('Teal', (.025, .26, .28), .34, 0),
            ('Coral', (.67, .075, .038), .35, 0), ('Steel', (.67, .69, .71), .27, 1),
            ('Glass', (.075, .23, .30), .14, 0)):
        mat = bpy.data.materials.new('Ferris_' + name)
        mat.diffuse_color = (*tint, 1)
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Metallic'].default_value = metallic
        uv = mat.node_tree.nodes.new('ShaderNodeUVMap')
        uv.uv_map = 'UVMap'
        height = np.sin(y * 1.1) * .003 if name == 'Steel' else grain * .002
        dy, dx = np.gradient(height)
        normal = np.stack([-dx, -dy, np.ones_like(dx)], axis=2)
        normal /= np.linalg.norm(normal, axis=2, keepdims=True)
        colour = np.stack([c * (1 + grain * .025) for c in tint], axis=2)
        roughness = np.stack([rough + grain * .018] * 3, axis=2)
        record = dict(id=mat.name, baseColorFactor=[1, 1, 1, 1], metallicFactor=metallic,
                      roughnessFactor=rough, normalConvention='OpenGL',
                      source='Original ANANTA deterministic procedural PBR', license='Original project asset')
        for role, pixels in (('baseColor', colour), ('roughness', roughness), ('normal', normal * .5 + .5)):
            path = directory / f'{name}_{role}.png'
            image = save_image(path, pixels, role == 'baseColor')
            record[role] = path.relative_to(base).as_posix()
            tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex.image = image
            mat.node_tree.links.new(uv.outputs['UV'], tex.inputs['Vector'])
            if role == 'normal':
                node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
                mat.node_tree.links.new(tex.outputs['Color'], node.inputs['Color'])
                mat.node_tree.links.new(node.outputs['Normal'], bsdf.inputs['Normal'])
            else:
                socket = 'Base Color' if role == 'baseColor' else 'Roughness'
                mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs[socket])
        if name == 'Glass':
            record.update(opacity=.40, twoSided=True)
            bsdf.inputs['Alpha'].default_value = .40
            bsdf.inputs['IOR'].default_value = 1.45
        records.append(record)
    return records
