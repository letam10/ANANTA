"""Generate a deterministic, original urban prop and connector kit for Nova City.

This is separate from ``GenerateNovaCitySlice.py`` so the vehicle/prop pass
can be regenerated without rewriting the city blockout. Every mesh is authored
in metres, has a stable name, and is exported as one GLB with a manifest for
the UE-MCP import/placement step.

Example:
  blender.exe --background --python Tools/Blender/GenerateNovaCityProps.py -- \
    --output-dir Saved/Generated/NovaCityProps --seed 17
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


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def apply_scale(obj: bpy.types.Object, scale: tuple[float, float, float]) -> None:
    obj.scale = scale
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
    assign_material(obj, mat)
    if bevel > 0.0:
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
    assign_material(obj, mat)
    link_to_collection(obj, collection)
    return obj


def record(obj: bpy.types.Object, role: str, placement_hint: str = "") -> dict:
    return {
        "name": obj.name,
        "role": role,
        "placement_hint": placement_hint,
        "dimensions_m": [round(float(v), 4) for v in obj.dimensions],
        "materials": [mat.name for mat in obj.data.materials],
    }


def add_wheel(collection: bpy.types.Collection, name: str, x: float, y: float, z: float,
              tire: bpy.types.Material, rim: bpy.types.Material, records: list[dict]) -> None:
    wheel = cylinder(name, 0.34, 0.20, (x, y, z), tire, collection, vertices=20, rotation=(math.pi / 2, 0, 0))
    records.append(record(wheel, "vehicle_wheel"))
    hub = cylinder(f"{name}_Hub", 0.13, 0.215, (x, y, z), rim, collection, vertices=16, rotation=(math.pi / 2, 0, 0))
    records.append(record(hub, "vehicle_hub"))


def add_sedan(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict], x: float, y: float) -> None:
    body = cube("Nova_Vehicle_Sedan_Body", (4.4, 1.85, 0.72), (x, y, 0.72), materials["car_blue"], collection, bevel=0.16)
    records.append(record(body, "vehicle_sedan_body", "parking_lane"))
    hood = cube("Nova_Vehicle_Sedan_Hood", (1.25, 1.72, 0.20), (x + 1.30, y, 1.13), materials["car_blue"], collection, bevel=0.08)
    records.append(record(hood, "vehicle_sedan_hood"))
    cabin = cube("Nova_Vehicle_Sedan_Cabin", (2.20, 1.50, 0.68), (x - 0.35, y, 1.27), materials["car_glass"], collection, bevel=0.15)
    records.append(record(cabin, "vehicle_sedan_glass"))
    roof = cube("Nova_Vehicle_Sedan_Roof", (1.88, 1.44, 0.13), (x - 0.35, y, 1.66), materials["car_blue"], collection, bevel=0.05)
    records.append(record(roof, "vehicle_sedan_roof"))
    for side in (-1, 1):
        for wheel_x in (x - 1.45, x + 1.45):
            add_wheel(collection, f"Nova_Vehicle_Sedan_Wheel_{'L' if side < 0 else 'R'}_{'F' if wheel_x < x else 'R'}",
                      wheel_x, y + side * 0.94, 0.42, materials["rubber"], materials["rim"], records)
    for side in (-1, 1):
        lamp = cube(f"Nova_Vehicle_Sedan_Lamp_{'L' if side < 0 else 'R'}", (0.16, 0.48, 0.16), (x + 2.22, y + side * 0.55, 0.88), materials["lamp_white"], collection, bevel=0.03)
        records.append(record(lamp, "vehicle_headlamp"))


def add_van(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict], x: float, y: float) -> None:
    body = cube("Nova_Vehicle_Van_Body", (5.0, 2.05, 1.65), (x, y, 1.22), materials["van_warm"], collection, bevel=0.14)
    records.append(record(body, "vehicle_van_body", "loading_bay"))
    windshield = cube("Nova_Vehicle_Van_Windshield", (0.12, 1.68, 0.72), (x + 2.52, y, 1.55), materials["car_glass"], collection, bevel=0.03, rotation=(0, math.radians(-8), 0))
    records.append(record(windshield, "vehicle_van_windshield"))
    for side in (-1, 1):
        windows = cube(f"Nova_Vehicle_Van_SideWindows_{'L' if side < 0 else 'R'}", (2.2, 0.08, 0.66), (x - 0.45, y + side * 1.04, 1.60), materials["car_glass"], collection, bevel=0.04)
        records.append(record(windows, "vehicle_van_side_windows"))
        for wheel_x in (x - 1.55, x + 1.55):
            add_wheel(collection, f"Nova_Vehicle_Van_Wheel_{'L' if side < 0 else 'R'}_{'F' if wheel_x < x else 'R'}",
                      wheel_x, y + side * 1.05, 0.47, materials["rubber"], materials["rim"], records)
    rear = cube("Nova_Vehicle_Van_RearDoor", (0.10, 1.68, 1.22), (x - 2.52, y, 1.30), materials["van_warm"], collection, bevel=0.02)
    records.append(record(rear, "vehicle_van_rear_door"))


def add_scooter(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict], x: float, y: float) -> None:
    deck = cube("Nova_Vehicle_Scooter_Deck", (1.5, 0.34, 0.18), (x, y, 0.48), materials["car_red"], collection, bevel=0.05)
    records.append(record(deck, "vehicle_scooter_deck"))
    stem = cylinder("Nova_Vehicle_Scooter_Stem", 0.06, 1.15, (x + 0.45, y, 1.0), materials["metal"], collection, vertices=12, rotation=(0, math.radians(-12), 0))
    records.append(record(stem, "vehicle_scooter_stem"))
    handle = cube("Nova_Vehicle_Scooter_Handle", (0.55, 0.08, 0.08), (x + 0.56, y, 1.54), materials["metal"], collection, bevel=0.02)
    records.append(record(handle, "vehicle_scooter_handle"))
    for side, wheel_x in ((-1, x - 0.55), (1, x + 0.55)):
        wheel = cylinder(f"Nova_Vehicle_Scooter_Wheel_{side}", 0.20, 0.10, (wheel_x, y, 0.24), materials["rubber"], collection, vertices=16, rotation=(math.pi / 2, 0, 0))
        records.append(record(wheel, "vehicle_scooter_wheel"))


def add_traffic_signal(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict], x: float, y: float) -> None:
    pole = cylinder("Nova_TrafficSignal_Pole", 0.09, 3.7, (x, y, 1.85), materials["metal"], collection, vertices=12)
    records.append(record(pole, "traffic_signal_pole", "road_intersection"))
    arm = cube("Nova_TrafficSignal_Arm", (1.15, 0.12, 0.12), (x + 0.54, y, 3.54), materials["metal"], collection, bevel=0.03)
    records.append(record(arm, "traffic_signal_arm"))
    housing = cube("Nova_TrafficSignal_Housing", (0.30, 0.38, 0.92), (x + 1.06, y, 3.12), materials["signal_body"], collection, bevel=0.06)
    records.append(record(housing, "traffic_signal_housing"))
    for index, (z, mat) in enumerate(((3.42, materials["signal_red"]), (3.12, materials["signal_amber"]), (2.82, materials["signal_green"]))):
        lamp = cylinder(f"Nova_TrafficSignal_Lamp_{index}", 0.095, 0.03, (x + 1.22, y, z), mat, collection, vertices=16, rotation=(0, math.pi / 2, 0))
        records.append(record(lamp, "traffic_signal_lamp"))


def add_street_sign(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict], x: float, y: float) -> None:
    pole = cylinder("Nova_StreetSign_Pole", 0.06, 2.65, (x, y, 1.33), materials["metal"], collection, vertices=12)
    records.append(record(pole, "street_sign_pole", "sidewalk_edge"))
    sign = cube("Nova_StreetSign_Panel", (0.85, 0.07, 0.45), (x, y, 2.38), materials["sign_blue"], collection, bevel=0.03)
    records.append(record(sign, "street_sign_panel"))
    trim = cube("Nova_StreetSign_Trim", (0.67, 0.075, 0.05), (x, y - 0.005, 2.38), materials["sign_white"], collection, bevel=0.01)
    records.append(record(trim, "street_sign_trim"))


def add_bench(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict], x: float, y: float) -> None:
    seat = cube("Nova_Bench_Seat", (1.8, 0.48, 0.12), (x, y, 0.62), materials["wood"], collection, bevel=0.05)
    records.append(record(seat, "bench_seat", "plaza"))
    back = cube("Nova_Bench_Back", (1.8, 0.10, 0.75), (x - 0.72, y, 1.05), materials["wood"], collection, bevel=0.04, rotation=(0, math.radians(-7), 0))
    records.append(record(back, "bench_back"))
    for side in (-1, 1):
        leg = cube(f"Nova_Bench_Leg_{side}", (0.10, 0.42, 0.58), (x + side * 0.62, y, 0.30), materials["metal"], collection, bevel=0.025)
        records.append(record(leg, "bench_leg"))


def add_barrier(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict], x: float, y: float) -> None:
    for side in (-1, 1):
        foot = cube(f"Nova_Barrier_Foot_{side}", (0.22, 0.38, 0.12), (x + side * 1.0, y, 0.08), materials["metal"], collection, bevel=0.03)
        records.append(record(foot, "barrier_foot", "road_edge"))
    rail = cube("Nova_Barrier_Rail", (2.25, 0.10, 0.78), (x, y, 0.58), materials["barrier_orange"], collection, bevel=0.06)
    records.append(record(rail, "barrier_rail"))
    for idx, stripe_x in enumerate((x - 0.55, x + 0.55)):
        stripe = cube(f"Nova_Barrier_Reflector_{idx}", (0.20, 0.12, 0.28), (stripe_x, y - 0.06, 0.58), materials["sign_white"], collection, bevel=0.02)
        records.append(record(stripe, "barrier_reflector"))


def add_road_connectors(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material], records: list[dict]) -> None:
    road = cube("Nova_RoadConnector_Straight", (24.0, 8.0, 0.20), (0, 0, 0.10), materials["road"], collection, bevel=0.05)
    records.append(record(road, "road_connector_straight", "snap_grid_24m"))
    center = cube("Nova_RoadConnector_Cross", (8.0, 8.0, 0.21), (0, 0, 0.105), materials["road"], collection, bevel=0.05)
    records.append(record(center, "road_connector_cross", "snap_grid_8m"))
    for index, x in enumerate((-2.7, -1.8, -0.9, 0.0, 0.9, 1.8, 2.7)):
        strip = cube(f"Nova_RoadConnector_Crosswalk_{index}", (0.38, 7.6, 0.025), (x, 0, 0.225), materials["road_mark"], collection, bevel=0.01)
        records.append(record(strip, "crosswalk_marking"))
    for side in (-1, 1):
        sidewalk = cube(f"Nova_RoadConnector_Sidewalk_{side}", (24.0, 2.2, 0.32), (0, side * 5.1, 0.16), materials["sidewalk"], collection, bevel=0.04)
        records.append(record(sidewalk, "sidewalk_connector", "snap_grid_24m"))
        curb = cube(f"Nova_RoadConnector_Curb_{side}", (24.0, 0.18, 0.28), (0, side * 3.98, 0.24), materials["curb"], collection, bevel=0.02)
        records.append(record(curb, "curb_connector"))
    corner = cube("Nova_RoadConnector_Corner", (8.0, 8.0, 0.17), (13.0, 13.0, 0.085), materials["sidewalk"], collection, bevel=0.04)
    records.append(record(corner, "sidewalk_corner_connector", "snap_grid_8m"))


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
        scene.world = bpy.data.worlds.new("NovaCityPropsWorld")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.035, 0.06, 0.12, 1)
        background.inputs["Strength"].default_value = 0.65

    root = bpy.data.collections.new("NovaCityProps")
    scene.collection.children.link(root)
    materials = {
        "road": make_material("M_NovaProps_Asphalt", (0.095, 0.115, 0.15, 1), metallic=0.05, roughness=0.82),
        "road_mark": make_material("M_NovaProps_RoadMark", (0.82, 0.69, 0.24, 1), roughness=0.55),
        "sidewalk": make_material("M_NovaProps_Sidewalk", (0.36, 0.39, 0.43, 1), roughness=0.88),
        "curb": make_material("M_NovaProps_Curb", (0.55, 0.57, 0.57, 1), metallic=0.05, roughness=0.72),
        "metal": make_material("M_NovaProps_Metal", (0.28, 0.34, 0.39, 1), metallic=0.82, roughness=0.30),
        "rubber": make_material("M_NovaProps_Rubber", (0.035, 0.045, 0.055, 1), roughness=0.80),
        "rim": make_material("M_NovaProps_Rim", (0.52, 0.58, 0.62, 1), metallic=0.9, roughness=0.24),
        "car_blue": make_material("M_NovaProps_CarBlue", (0.055, 0.22, 0.42, 1), metallic=0.72, roughness=0.27),
        "car_red": make_material("M_NovaProps_CarRed", (0.58, 0.10, 0.075, 1), metallic=0.62, roughness=0.30),
        "van_warm": make_material("M_NovaProps_VanWarm", (0.48, 0.43, 0.35, 1), metallic=0.38, roughness=0.38),
        "car_glass": make_material("M_NovaProps_Glass", (0.035, 0.17, 0.25, 1), metallic=0.40, roughness=0.18),
        "lamp_white": make_material("M_NovaProps_LampWhite", (0.74, 0.88, 0.96, 1), metallic=0.15, roughness=0.23, emission=(0.8, 0.92, 1.0, 1), emission_strength=2.5),
        "signal_body": make_material("M_NovaProps_SignalBody", (0.13, 0.16, 0.18, 1), metallic=0.55, roughness=0.42),
        "signal_red": make_material("M_NovaProps_SignalRed", (0.75, 0.035, 0.02, 1), roughness=0.26, emission=(1.0, 0.03, 0.01, 1), emission_strength=2.0),
        "signal_amber": make_material("M_NovaProps_SignalAmber", (0.9, 0.32, 0.03, 1), roughness=0.26, emission=(1.0, 0.20, 0.01, 1), emission_strength=1.8),
        "signal_green": make_material("M_NovaProps_SignalGreen", (0.04, 0.62, 0.22, 1), roughness=0.26, emission=(0.03, 1.0, 0.18, 1), emission_strength=1.5),
        "sign_blue": make_material("M_NovaProps_SignBlue", (0.035, 0.22, 0.58, 1), metallic=0.12, roughness=0.48),
        "sign_white": make_material("M_NovaProps_SignWhite", (0.86, 0.87, 0.80, 1), metallic=0.08, roughness=0.47),
        "wood": make_material("M_NovaProps_Wood", (0.36, 0.18, 0.08, 1), roughness=0.72),
        "barrier_orange": make_material("M_NovaProps_BarrierOrange", (0.78, 0.24, 0.035, 1), metallic=0.22, roughness=0.44),
    }
    records: list[dict] = []
    add_road_connectors(root, materials, records)
    add_sedan(root, materials, records, -5.5, 1.2)
    add_van(root, materials, records, 5.0, -1.2)
    add_scooter(root, materials, records, 0.0, 4.7)
    add_traffic_signal(root, materials, records, -6.0, -5.0)
    add_street_sign(root, materials, records, 7.0, 5.1)
    add_bench(root, materials, records, -7.0, 5.0)
    add_barrier(root, materials, records, 7.0, -4.7)

    bpy.ops.object.light_add(type="AREA", location=(0, -9, 18))
    key = bpy.context.object
    key.name = "NovaProps_KeyLight"
    key.data.energy = 2200
    key.data.size = 16
    aim_at(key, (0, 0, 0))
    link_to_collection(key, root)
    bpy.ops.object.light_add(type="AREA", location=(15, 10, 10))
    fill = bpy.context.object
    fill.name = "NovaProps_CoolFill"
    fill.data.energy = 1800
    fill.data.color = (0.10, 0.38, 1.0)
    fill.data.size = 12
    aim_at(fill, (0, 0, 1))
    link_to_collection(fill, root)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 20))
    sun = bpy.context.object
    sun.name = "NovaProps_Sun"
    sun.data.energy = 1.2
    sun.data.color = (0.62, 0.75, 1.0)
    aim_at(sun, (0, 0, 0))
    link_to_collection(sun, root)
    bpy.ops.object.camera_add(location=(20, -22, 12))
    camera = bpy.context.object
    camera.name = "NovaProps_HeroCamera"
    camera.data.lens = 42
    aim_at(camera, (0, 0, 0.9))
    scene.camera = camera
    link_to_collection(camera, root)
    return {"script_version": SCRIPT_VERSION, "seed": args.seed, "collection": root.name, "units": "meters",
            "object_count": len(records), "objects": records, "materials": sorted(mat.name for mat in materials.values())}


def export_outputs(args: argparse.Namespace, manifest: dict) -> None:
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    blend_path = output_dir / "NovaCityProps.blend"
    glb_path = output_dir / "NovaCityProps.glb"
    manifest_path = output_dir / "NovaCityProps.manifest.json"
    preview_path = output_dir / "NovaCityProps.preview.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.collections.get("NovaCityProps").objects:
        if obj.type == "MESH":
            obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects.get("NovaProps_HeroCamera")
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
    print(json.dumps({"ok": True, "object_count": manifest["object_count"], "output_dir": str(Path(args.output_dir).resolve()), "glb": manifest["glb"], "manifest": manifest["manifest"]}))


if __name__ == "__main__":
    main()
