"""Build three deterministic hero facade variants for the Nova City slice.

The kit is deliberately authored as modular geometry rather than a single
background mesh. Each facade keeps a stable prefix and a material slot so the
UE-MCP import/placement pass can replace or instance individual pieces later.

Run from the ANANTA project root with Blender 4.5+:
  blender.exe --background --python Tools/Blender/GenerateNovaHeroFacadeKit.py -- \
    --output-dir Saved/Generated/NovaHeroFacadeKit --seed 17
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT_VERSION = "0.1.0"


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--no-preview", action="store_true")
    return parser.parse_args(argv)


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def link_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def aim_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_material(name: str, color: tuple[float, float, float, float], *, metallic=0.0, roughness=0.6,
                  emission: tuple[float, float, float, float] | None = None, emission_strength=0.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission is not None and "Emission Color" in shader.inputs:
        shader.inputs["Emission Color"].default_value = emission
        shader.inputs["Emission Strength"].default_value = emission_strength
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    mat.diffuse_color = color
    return mat


def apply_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def apply_scale(obj: bpy.types.Object, size: tuple[float, float, float]) -> None:
    obj.scale = size
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def cube(name: str, size: tuple[float, float, float], location: tuple[float, float, float], mat: bpy.types.Material,
         collection: bpy.types.Collection, *, bevel=0.0, rotation=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    apply_scale(obj, size)
    apply_material(obj, mat)
    if bevel > 0:
        modifier = obj.modifiers.new("EdgeSoftness", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    link_to_collection(obj, collection)
    return obj


def cylinder(name: str, radius: float, depth: float, location: tuple[float, float, float], mat: bpy.types.Material,
             collection: bpy.types.Collection, *, vertices=16, rotation=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    apply_material(obj, mat)
    link_to_collection(obj, collection)
    return obj


def record(obj: bpy.types.Object, variant: str, role: str, placement_hint: str = "") -> dict:
    return {
        "name": obj.name,
        "variant": variant,
        "role": role,
        "placement_hint": placement_hint,
        "dimensions_m": [round(float(v), 4) for v in obj.dimensions],
        "materials": [mat.name for mat in obj.data.materials],
    }


def add_window_grid(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict],
                    variant: str, prefix: str, x: float, width: float, height: float, *, rows=3, cols=3, y=-0.78,
                    start_z=2.6) -> None:
    cell_w = (width - 1.4) / cols
    cell_h = (height - 3.0) / rows
    for row in range(rows):
        for col in range(cols):
            px = x - width / 2 + 0.7 + cell_w * (col + 0.5)
            pz = start_z + cell_h * row
            glass = cube(f"{prefix}_Window_{row:02d}_{col:02d}", (cell_w - 0.24, 0.10, cell_h - 0.28), (px, y, pz), materials["glass"], collection, bevel=0.025)
            records.append(record(glass, variant, "window_panel"))
            frame = cube(f"{prefix}_WindowFrame_{row:02d}_{col:02d}", (cell_w - 0.12, 0.045, 0.055), (px, y - 0.065, pz - cell_h / 2 + 0.13), materials["metal"], collection, bevel=0.01)
            records.append(record(frame, variant, "window_sill"))


def add_balcony_variant(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material], records: list[dict], x: float) -> None:
    variant = "balcony"
    prefix = "Nova_HeroFacade_Balcony"
    body = cube(f"{prefix}_Body", (9.0, 1.45, 13.0), (x, 0, 6.5), mats["concrete"], collection, bevel=0.10)
    records.append(record(body, variant, "facade_body", "block_grid_12m"))
    add_window_grid(collection, mats, records, variant, prefix, x, 8.4, 13.0, rows=3, cols=3, start_z=2.1)
    for level, z in enumerate((3.0, 6.7, 10.4), start=1):
        slab = cube(f"{prefix}_Balcony_{level:02d}_Slab", (3.55, 1.40, 0.22), (x - 1.2, -1.18, z), mats["concrete_dark"], collection, bevel=0.05)
        records.append(record(slab, variant, "balcony_slab", "player_traversal_edge"))
        rail = cube(f"{prefix}_Balcony_{level:02d}_Rail", (3.35, 0.08, 0.95), (x - 1.2, -1.88, z + 0.55), mats["metal"], collection, bevel=0.03)
        records.append(record(rail, variant, "balcony_rail"))
        for post in range(4):
            px = x - 2.75 + post * 1.05
            post_obj = cylinder(f"{prefix}_Balcony_{level:02d}_Post_{post}", 0.035, 1.05, (px, -1.88, z + 0.55), mats["metal"], collection, vertices=10)
            records.append(record(post_obj, variant, "balcony_post"))
        planter = cube(f"{prefix}_Balcony_{level:02d}_Planter", (1.25, 0.30, 0.24), (x + 0.55, -1.84, z + 0.22), mats["planter"], collection, bevel=0.04)
        records.append(record(planter, variant, "balcony_planter"))
        foliage = cylinder(f"{prefix}_Balcony_{level:02d}_Foliage", 0.32, 0.55, (x + 0.55, -1.84, z + 0.60), mats["foliage"], collection, vertices=12)
        records.append(record(foliage, variant, "balcony_foliage"))
    roofline = cube(f"{prefix}_Roofline", (9.35, 1.65, 0.30), (x, 0, 13.15), mats["metal"], collection, bevel=0.05)
    records.append(record(roofline, variant, "roofline"))


def add_awning_variant(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material], records: list[dict], x: float) -> None:
    variant = "awning"
    prefix = "Nova_HeroFacade_Awning"
    body = cube(f"{prefix}_Body", (9.0, 1.50, 12.0), (x, 0, 6.0), mats["concrete_dark"], collection, bevel=0.10)
    records.append(record(body, variant, "facade_body", "block_grid_12m"))
    # The street-level storefront is intentionally distinct from the upper office bays.
    shop = cube(f"{prefix}_StorefrontGlass", (8.0, 0.10, 2.25), (x, -0.83, 1.55), mats["glass_warm"], collection, bevel=0.03)
    records.append(record(shop, variant, "commercial_storefront", "interaction_frontage"))
    for bay in range(3):
        px = x - 2.65 + bay * 2.65
        canopy = cube(f"{prefix}_Awning_{bay}_Canopy", (2.25, 1.10, 0.14), (px, -1.33, 3.02), mats["awning"], collection, bevel=0.03, rotation=(math.radians(-9), 0, 0))
        records.append(record(canopy, variant, "awning_canopy", "street_shelter"))
        valance = cube(f"{prefix}_Awning_{bay}_Valance", (2.20, 0.10, 0.30), (px, -1.82, 2.88), mats["awning"], collection, bevel=0.02)
        records.append(record(valance, variant, "awning_valance"))
    add_window_grid(collection, mats, records, variant, prefix, x, 8.4, 12.0, rows=3, cols=3, start_z=4.15)
    sign = cube(f"{prefix}_CommercialSign", (5.8, 0.12, 0.72), (x, -0.90, 3.78), mats["sign_warm"], collection, bevel=0.04)
    records.append(record(sign, variant, "commercial_sign", "quest_or_shop_marker"))
    sign_line = cube(f"{prefix}_CommercialSignLine", (4.9, 0.04, 0.07), (x, -0.98, 3.78), mats["sign_white"], collection, bevel=0.01)
    records.append(record(sign_line, variant, "commercial_sign_detail"))
    roofline = cube(f"{prefix}_Roofline", (9.35, 1.68, 0.30), (x, 0, 12.15), mats["metal"], collection, bevel=0.05)
    records.append(record(roofline, variant, "roofline"))


def add_metro_variant(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material], records: list[dict], x: float) -> None:
    variant = "metro_commercial"
    prefix = "Nova_HeroFacade_Metro"
    body = cube(f"{prefix}_Body", (10.0, 1.60, 13.0), (x, 0, 6.5), mats["concrete"], collection, bevel=0.10)
    records.append(record(body, variant, "facade_body", "block_grid_12m"))
    add_window_grid(collection, mats, records, variant, prefix, x, 9.3, 13.0, rows=3, cols=3, start_z=3.9)
    for side in (-1, 1):
        pillar = cube(f"{prefix}_MetroEntrance_Pillar_{side}", (0.34, 1.05, 3.15), (x + side * 2.0, -0.82, 1.58), mats["concrete_dark"], collection, bevel=0.04)
        records.append(record(pillar, variant, "metro_entrance_pillar", "metro_entrance"))
    canopy = cube(f"{prefix}_MetroCanopy", (5.0, 2.15, 0.24), (x, -1.58, 3.15), mats["metal"], collection, bevel=0.06)
    records.append(record(canopy, variant, "metro_canopy", "metro_entrance"))
    sign = cube(f"{prefix}_MetroSign", (2.0, 0.18, 0.90), (x, -2.43, 3.72), mats["metro_cyan"], collection, bevel=0.05)
    records.append(record(sign, variant, "metro_sign", "fast_travel_marker"))
    sign_inner = cube(f"{prefix}_MetroSignInner", (1.25, 0.04, 0.52), (x, -2.53, 3.72), mats["sign_white"], collection, bevel=0.03)
    records.append(record(sign_inner, variant, "metro_sign_detail"))
    for side in (-1, 1):
        rail = cube(f"{prefix}_MetroRail_{side}", (3.0, 0.08, 0.90), (x + side * 2.2, -2.45, 0.88), mats["metal"], collection, bevel=0.025)
        records.append(record(rail, variant, "metro_guardrail"))
    commercial = cube(f"{prefix}_CommercialBand", (7.2, 0.10, 0.58), (x, -0.91, 8.15), mats["sign_warm"], collection, bevel=0.03)
    records.append(record(commercial, variant, "commercial_sign", "quest_or_shop_marker"))
    roofline = cube(f"{prefix}_Roofline", (10.35, 1.78, 0.30), (x, 0, 13.15), mats["metal"], collection, bevel=0.05)
    records.append(record(roofline, variant, "roofline"))


def build_scene(args: argparse.Namespace) -> dict:
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 75
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium Low Contrast"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("NovaHeroFacadeWorld")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.03, 0.055, 0.11, 1)
        background.inputs["Strength"].default_value = 0.70

    root = bpy.data.collections.new("NovaHeroFacadeKit")
    scene.collection.children.link(root)
    mats = {
        "concrete": make_material("M_NovaHero_Concrete", (0.28, 0.34, 0.42, 1), metallic=0.12, roughness=0.78),
        "concrete_dark": make_material("M_NovaHero_ConcreteDark", (0.18, 0.23, 0.30, 1), metallic=0.18, roughness=0.72),
        "glass": make_material("M_NovaHero_Glass", (0.035, 0.16, 0.24, 1), metallic=0.48, roughness=0.18),
        "glass_warm": make_material("M_NovaHero_GlassWarm", (0.14, 0.25, 0.27, 1), metallic=0.34, roughness=0.22),
        "metal": make_material("M_NovaHero_Metal", (0.34, 0.41, 0.46, 1), metallic=0.84, roughness=0.28),
        "planter": make_material("M_NovaHero_Planter", (0.32, 0.20, 0.14, 1), metallic=0.12, roughness=0.64),
        "foliage": make_material("M_NovaHero_Foliage", (0.035, 0.22, 0.12, 1), roughness=0.86),
        "awning": make_material("M_NovaHero_Awning", (0.08, 0.38, 0.42, 1), metallic=0.08, roughness=0.62),
        "sign_warm": make_material("M_NovaHero_CommercialSign", (0.65, 0.18, 0.045, 1), metallic=0.22, roughness=0.38, emission=(0.9, 0.09, 0.015, 1), emission_strength=1.6),
        "metro_cyan": make_material("M_NovaHero_MetroCyan", (0.03, 0.35, 0.60, 1), metallic=0.30, roughness=0.30, emission=(0.02, 0.55, 1.0, 1), emission_strength=2.2),
        "sign_white": make_material("M_NovaHero_SignWhite", (0.88, 0.90, 0.86, 1), metallic=0.05, roughness=0.42),
        "sidewalk": make_material("M_NovaHero_Sidewalk", (0.36, 0.40, 0.44, 1), roughness=0.86),
        "road": make_material("M_NovaHero_Road", (0.09, 0.12, 0.16, 1), metallic=0.06, roughness=0.82),
    }
    records: list[dict] = []
    # A shared plinth makes the three variants read as a continuous city block.
    plinth = cube("Nova_HeroFacade_SharedPlinth", (32.0, 8.0, 0.18), (0, 0, 0.09), mats["sidewalk"], root, bevel=0.04)
    records.append(record(plinth, "shared", "shared_plinth", "expanded_block_base"))
    road = cube("Nova_HeroFacade_SharedRoad", (32.0, 3.6, 0.16), (0, -4.0, 0.08), mats["road"], root, bevel=0.03)
    records.append(record(road, "shared", "shared_road", "expanded_block_connector"))
    add_balcony_variant(root, mats, records, -11.0)
    add_awning_variant(root, mats, records, 0.0)
    add_metro_variant(root, mats, records, 11.0)

    bpy.ops.object.light_add(type="AREA", location=(0, -13, 24))
    key = bpy.context.object
    key.name = "NovaHeroFacade_KeyLight"
    key.data.energy = 4600
    key.data.size = 22
    aim_at(key, (0, 0, 6))
    link_to_collection(key, root)
    bpy.ops.object.light_add(type="AREA", location=(19, 9, 16))
    fill = bpy.context.object
    fill.name = "NovaHeroFacade_CoolFill"
    fill.data.energy = 2400
    fill.data.color = (0.12, 0.36, 1.0)
    fill.data.size = 18
    aim_at(fill, (0, 0, 6))
    link_to_collection(fill, root)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 24))
    sun = bpy.context.object
    sun.name = "NovaHeroFacade_Sun"
    sun.data.energy = 1.35
    sun.data.color = (0.62, 0.76, 1.0)
    aim_at(sun, (0, 0, 0))
    link_to_collection(sun, root)
    bpy.ops.object.camera_add(location=(29, -34, 21))
    camera = bpy.context.object
    camera.name = "NovaHeroFacade_HeroCamera"
    camera.data.lens = 45
    aim_at(camera, (0, 0, 6.2))
    scene.camera = camera
    link_to_collection(camera, root)
    return {
        "script_version": SCRIPT_VERSION,
        "seed": args.seed,
        "collection": root.name,
        "units": "meters",
        "object_count": len(records),
        "objects": records,
        "materials": sorted(mat.name for mat in mats.values()),
        "variants": ["balcony", "awning", "metro_commercial"],
    }


def export_outputs(args: argparse.Namespace, manifest: dict) -> None:
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    blend_path = output_dir / "NovaHeroFacadeKit.blend"
    glb_path = output_dir / "NovaHeroFacadeKit.glb"
    manifest_path = output_dir / "NovaHeroFacadeKit.manifest.json"
    preview_path = output_dir / "NovaHeroFacadeKit.preview.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.collections.get("NovaHeroFacadeKit").objects:
        if obj.type == "MESH":
            obj.select_set(True)
    try:
        bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB", use_selection=True,
                                  export_materials="EXPORT", export_cameras=False, export_lights=False)
    except TypeError:
        bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB", use_selection=True)
    manifest.update({"blend": str(blend_path), "glb": str(glb_path), "manifest": str(manifest_path), "preview": str(preview_path)})
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    if not args.no_preview:
        bpy.context.scene.render.filepath = str(preview_path)
        bpy.ops.render.render(write_still=True)


def main() -> None:
    args = parse_args()
    clean_scene()
    manifest = build_scene(args)
    export_outputs(args, manifest)
    print(json.dumps({"ok": True, "object_count": manifest["object_count"], "variants": manifest["variants"], "glb": manifest["glb"], "manifest": manifest["manifest"]}))


if __name__ == "__main__":
    main()
