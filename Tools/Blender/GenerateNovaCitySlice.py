"""Build a deterministic, original Nova City vertical-slice kit.

Run with Blender 4.5+ in background mode, for example:
  blender.exe --background --python Tools/Blender/GenerateNovaCitySlice.py \
    -- --output-dir Saved/Generated/NovaCitySlice --seed 17

The script deliberately produces a small, repeatable asset kit instead of a
large random city.  Every module has a stable name and is exported as GLB so
the Unreal import step can be automated by UE-MCP.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector


SCRIPT_VERSION = "0.1.0"


def parse_args() -> argparse.Namespace:
    # Blender passes its own arguments before the second ``--`` marker.
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="Directory for GLB, blend, preview and manifest")
    parser.add_argument("--seed", type=int, default=17, help="Stable layout seed")
    parser.add_argument("--no-preview", action="store_true", help="Skip the low-resolution EEVEE preview")
    return parser.parse_args(argv)


def clean_scene() -> None:
    """Remove only the current generated Blender scene, never project files."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        # Orphan purge is intentionally limited to data created in this run.
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def material(name: str, color: tuple[float, float, float, float], *, metallic=0.0, roughness=0.6,
             emission: tuple[float, float, float, float] | None = None, emission_strength=0.0) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    mat.diffuse_color = color
    return mat


def apply_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def set_transform(obj: bpy.types.Object, location: tuple[float, float, float], scale: tuple[float, float, float] = (1, 1, 1), rotation_z=0.0) -> None:
    obj.location = location
    obj.scale = scale
    obj.rotation_euler[2] = math.radians(rotation_z)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def aim_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    """Aim a camera or area light using its local -Z direction."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def cube(name: str, size: tuple[float, float, float], location: tuple[float, float, float], mat: bpy.types.Material,
         *, rotation_z=0.0, bevel=0.0, collection: bpy.types.Collection) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    set_transform(obj, location, size, rotation_z)
    apply_material(obj, mat)
    if bevel > 0:
        modifier = obj.modifiers.new("EdgeSoftness", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    link_to_collection(obj, collection)
    return obj


def cylinder(name: str, radius: float, depth: float, location: tuple[float, float, float], mat: bpy.types.Material,
             *, collection: bpy.types.Collection, vertices=16) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.location = location
    apply_material(obj, mat)
    link_to_collection(obj, collection)
    return obj


def link_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def add_building(collection: bpy.types.Collection, index: int, x: float, y: float, width: float, depth: float,
                 height: float, concrete: bpy.types.Material, glass: bpy.types.Material, neon: bpy.types.Material) -> list[dict]:
    """Create one facade module; windows are separate low-poly strips for easy UE material overrides."""
    created: list[dict] = []
    body = cube(f"Nova_Building_{index:02d}_Body", (width, depth, height), (x, y, height / 2), concrete, bevel=0.12, collection=collection)
    created.append(asset_record(body, "building_body"))

    floor_height = 3.4
    rows = max(1, int(height / floor_height) - 1)
    window_w = max(0.8, width / 7.0)
    window_h = 1.7
    side_offset = depth / 2 + 0.015
    front_y = y - side_offset
    rear_y = y + side_offset
    for row in range(rows):
        z = 1.5 + row * floor_height
        for col in range(4):
            px = x - width * 0.30 + col * width * 0.20
            for face, py, rot in (("F", front_y, 0.0), ("R", rear_y, 180.0)):
                win = cube(f"Nova_Building_{index:02d}_Window_{face}_{row:02d}_{col:02d}", (window_w, 0.08, window_h), (px, py, z), glass,
                           rotation_z=rot, collection=collection)
                created.append(asset_record(win, "window_panel"))
    roof = cube(f"Nova_Building_{index:02d}_RoofCap", (width * 0.88, depth * 0.88, 0.18), (x, y, height + 0.09), neon, collection=collection)
    created.append(asset_record(roof, "roof_cap"))
    return created


def asset_record(obj: bpy.types.Object, kind: str) -> dict:
    bounds = [list(round(v, 3) for v in corner) for corner in obj.bound_box]
    dims = [round(v, 3) for v in obj.dimensions]
    return {"name": obj.name, "kind": kind, "dimensions_m": dims, "bounds_local": bounds, "materials": [m.name for m in obj.data.materials]}


def create_scene(args: argparse.Namespace) -> dict:
    random.seed(args.seed)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 50
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium Low Contrast"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("NovaCityWorld")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.018, 0.045, 0.12, 1)
        background.inputs["Strength"].default_value = 0.55

    root = bpy.data.collections.new("NovaCitySlice")
    scene.collection.children.link(root)
    materials = {
        "concrete": material("M_Nova_Concrete", (0.12, 0.16, 0.24, 1), metallic=0.18, roughness=0.75),
        # Low-strength emission keeps the facade readable in the preview and in UE.
        "glass": material("M_Nova_Glass", (0.018, 0.13, 0.22, 1), metallic=0.55, roughness=0.2,
                           emission=(0.01, 0.09, 0.18, 1), emission_strength=0.9),
        "road": material("M_Nova_Road", (0.028, 0.04, 0.075, 1), metallic=0.1, roughness=0.78),
        "sidewalk": material("M_Nova_Sidewalk", (0.12, 0.14, 0.18, 1), metallic=0.0, roughness=0.9),
        "neon": material("M_Nova_Neon_Cyan", (0.005, 0.02, 0.025, 1), metallic=0.2, roughness=0.35, emission=(0.01, 0.8, 1.0, 1), emission_strength=8.0),
        "amber": material("M_Nova_Neon_Amber", (0.04, 0.018, 0.003, 1), metallic=0.15, roughness=0.3, emission=(1.0, 0.22, 0.02, 1), emission_strength=7.0),
        "foliage": material("M_Nova_Foliage", (0.015, 0.15, 0.075, 1), metallic=0.0, roughness=0.9),
        "fragment": material("M_Ananta_Fragment", (0.015, 0.25, 0.32, 1), metallic=0.65, roughness=0.22, emission=(0.1, 0.8, 1.0, 1), emission_strength=12.0),
    }
    records: list[dict] = []

    records.append(asset_record(cube("Nova_Ground", (72, 56, 0.25), (0, 0, -0.125), materials["road"], collection=root), "ground"))
    # Roads and sidewalks form a readable gameplay loop around the buildings.
    records.append(asset_record(cube("Nova_Road_Main", (72, 9, 0.12), (0, 0, 0.06), materials["road"], collection=root), "road"))
    records.append(asset_record(cube("Nova_Road_Cross", (9, 56, 0.13), (0, 0, 0.065), materials["road"], collection=root), "road"))
    for side in (-1, 1):
        records.append(asset_record(cube(f"Nova_Sidewalk_{side:+d}", (72, 3.0, 0.30), (0, side * 6.0, 0.15), materials["sidewalk"], collection=root), "sidewalk"))
        records.append(asset_record(cube(f"Nova_Sidewalk_Cross_{side:+d}", (3.0, 56, 0.30), (side * 6.0, 0, 0.15), materials["sidewalk"], collection=root), "sidewalk"))

    # Seeded positions keep the city stable while still allowing controlled variants.
    building_specs = [
        (-25, -18, 15, 12, 24), (-8, -18, 12, 12, 33), (13, -18, 16, 12, 28),
        (25, 16, 15, 13, 36), (8, 16, 12, 13, 22), (-12, 16, 16, 13, 31),
    ]
    for idx, (x, y, width, depth, height) in enumerate(building_specs, start=1):
        records.extend(add_building(root, idx, x, y, width, depth, height, materials["concrete"], materials["glass"], materials["neon"]))

    # Street furniture and gameplay landmark.
    for index, x in enumerate((-30, -15, 15, 30), start=1):
        pole = cylinder(f"Nova_StreetLamp_{index:02d}", 0.13, 4.5, (x, -4.4, 2.25), materials["concrete"], collection=root)
        records.append(asset_record(pole, "street_lamp"))
        lamp = cube(f"Nova_StreetLamp_{index:02d}_Glow", (0.65, 0.22, 0.18), (x, -4.4, 4.45), materials["amber"], collection=root)
        records.append(asset_record(lamp, "lamp_emissive"))
    for index, (x, y) in enumerate(((-30, 6), (30, 6), (0, 20)), start=1):
        tree = cylinder(f"Nova_Foliage_{index:02d}_Trunk", 0.30, 2.8, (x, y, 1.4), materials["concrete"], collection=root, vertices=12)
        records.append(asset_record(tree, "foliage_trunk"))
        crown = cylinder(f"Nova_Foliage_{index:02d}_Crown", 1.45, 2.6, (x, y, 3.8), materials["foliage"], collection=root, vertices=12)
        records.append(asset_record(crown, "foliage_crown"))

    # Main fragment landmark: simple geometry is intentional and easy to replace with a hero mesh later.
    base = cylinder("Nova_Fragment_Pedestal", 1.35, 0.65, (0, 3.0, 0.33), materials["concrete"], collection=root, vertices=8)
    shard = cube("Nova_Ananta_Fragment", (0.55, 0.30, 1.55), (0, 3.0, 1.45), materials["fragment"], rotation_z=35, bevel=0.06, collection=root)
    records.extend((asset_record(base, "fragment_pedestal"), asset_record(shard, "ananta_fragment")))

    # Lighting/camera live in the generated scene so the GLB and preview share a stable composition.
    bpy.ops.object.light_add(type="AREA", location=(0, -8, 28))
    key = bpy.context.object
    key.name = "Nova_KeyLight"
    key.data.energy = 5200
    key.data.shape = "DISK"
    key.data.size = 22
    aim_at(key, (0, 0, 0))
    link_to_collection(key, root)
    bpy.ops.object.light_add(type="AREA", location=(20, 12, 15))
    fill = bpy.context.object
    fill.name = "Nova_CyanFill"
    fill.data.energy = 2600
    fill.data.color = (0.05, 0.35, 1.0)
    fill.data.size = 16
    aim_at(fill, (0, 0, 7))
    link_to_collection(fill, root)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 28))
    sun = bpy.context.object
    sun.name = "Nova_MoonSun"
    sun.data.energy = 1.7
    sun.data.color = (0.35, 0.52, 1.0)
    aim_at(sun, (0, 0, 0))
    link_to_collection(sun, root)
    bpy.ops.object.light_add(type="POINT", location=(0, 3, 5))
    fragment_light = bpy.context.object
    fragment_light.name = "Nova_FragmentLight"
    fragment_light.data.energy = 850
    fragment_light.data.color = (0.02, 0.55, 1.0)
    fragment_light.data.shadow_soft_size = 3.0
    link_to_collection(fragment_light, root)
    bpy.ops.object.camera_add(location=(40, -42, 19))
    camera = bpy.context.object
    camera.name = "Nova_HeroCamera"
    target = Vector((0, 0, 5))
    aim_at(camera, tuple(target))
    camera.data.lens = 34
    scene.camera = camera
    link_to_collection(camera, root)

    return {"seed": args.seed, "script_version": SCRIPT_VERSION, "collection": root.name, "objects": records,
            "materials": sorted(m.name for m in materials.values()), "units": "meters", "object_count": len(records)}


def export_outputs(args: argparse.Namespace, manifest: dict) -> None:
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    blend_path = output_dir / "NovaCitySlice.blend"
    glb_path = output_dir / "NovaCitySlice.glb"
    manifest_path = output_dir / "NovaCitySlice.manifest.json"
    preview_path = output_dir / "NovaCitySlice.preview.png"

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    # Export only the generated collection, preserving stable names/materials for UE import.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.collections.get("NovaCitySlice").objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects.get("Nova_HeroCamera")
    try:
        bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB", use_selection=True,
                                  export_materials="EXPORT", export_cameras=False, export_lights=False)
    except TypeError:
        # Blender 5.x renamed some glTF options; the default exporter still preserves mesh/material data.
        bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB", use_selection=True)

    manifest.update({"blend": str(blend_path), "glb": str(glb_path), "preview": str(preview_path), "manifest": str(manifest_path)})
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    if not args.no_preview:
        bpy.context.scene.render.filepath = str(preview_path)
        bpy.ops.render.render(write_still=True)


def main() -> None:
    args = parse_args()
    clean_scene()
    manifest = create_scene(args)
    export_outputs(args, manifest)
    print(json.dumps({"ok": True, "object_count": manifest["object_count"], "output_dir": str(Path(args.output_dir).resolve()), "glb": manifest["glb"]}))


if __name__ == "__main__":
    main()
