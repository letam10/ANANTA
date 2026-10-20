"""Author isolated W3 assets; never modify either existing city map."""

import datetime
import hashlib
import json
from pathlib import Path
import sys

import unreal

TASK = Path(__file__).resolve().parent
ROOT = TASK.parent.parent
sys.path.insert(0, str(TASK))
from water_contract import camera_pose, foam_hlsl, load_spec, normal_hlsl

PACKAGE = "/Game/ANANTA/WaterW3_20261020"
MAP = PACKAGE + "/W3_Comparison"
EDIT = unreal.MaterialEditingLibrary
ASSETS = unreal.EditorAssetLibrary
SPEC = load_spec(ROOT)
REPORT = {
    "schema": "ananta.w3.native-readback.v1",
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "spec_hash": SPEC["hash"]["value"],
    "scope": PACKAGE,
    "evidence": "editor authoring/readback; not runtime or performance",
    "fpsClaim": False,
    "errors": [],
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def asset(name, cls, factory):
    path = PACKAGE + "/" + name
    existing = ASSETS.load_asset(path) if ASSETS.does_asset_exist(path) else None
    if existing:
        require(existing.get_class() == cls.static_class(), "Unexpected asset type: " + path)
        return existing
    result = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, PACKAGE, cls, factory)
    require(result is not None, "Asset creation failed: " + path)
    return result


def node(owner, cls, x=0, y=0, function=False):
    create = EDIT.create_material_expression_in_function if function else EDIT.create_material_expression
    result = create(owner, cls, x, y)
    require(result is not None, "Expression creation failed: " + str(cls))
    return result


def connect(source, destination, pin, output=""):
    require(EDIT.connect_material_expressions(source, output, destination, pin),
            "Connection failed: " + str(destination) + "." + pin)


def custom(function, code, kind, y, position, time):
    result = node(function, unreal.MaterialExpressionCustom, -300, y, True)
    result.set_editor_property("code", code)
    result.set_editor_property("output_type", kind)
    inputs = []
    for name in ("P", "T"):
        entry = unreal.CustomInput()
        entry.set_editor_property("input_name", name)
        inputs.append(entry)
    result.set_editor_property("inputs", inputs)
    connect(position, result, "P")
    connect(time, result, "T")
    return result


def build_material():
    function = asset("MF_WaveSpec", unreal.MaterialFunction, unreal.MaterialFunctionFactoryNew())
    # Chụp danh sách trước khi xóa: tránh sửa collection khi đang duyệt.
    for expression in list(EDIT.get_material_function_expressions(function)):
        EDIT.delete_material_expression_in_function(function, expression)
    require(not EDIT.get_material_function_expressions(function), "Function cleanup left stale expressions")
    position = node(function, unreal.MaterialExpressionFunctionInput, -700, 0, True)
    position.set_editor_property("input_name", "WorldPositionCm")
    position.set_editor_property("input_type", unreal.FunctionInputType.FUNCTION_INPUT_VECTOR3)
    position.set_editor_property("sort_priority", 0)
    time = node(function, unreal.MaterialExpressionFunctionInput, -700, 200, True)
    time.set_editor_property("input_name", "TimeSeconds")
    time.set_editor_property("input_type", unreal.FunctionInputType.FUNCTION_INPUT_SCALAR)
    time.set_editor_property("sort_priority", 1)
    normal = custom(function, normal_hlsl(SPEC), unreal.CustomMaterialOutputType.CMOT_FLOAT3, 0, position, time)
    foam = custom(function, foam_hlsl(SPEC), unreal.CustomMaterialOutputType.CMOT_FLOAT1, 300, position, time)
    base = node(function, unreal.MaterialExpressionLinearInterpolate, 100, 300, True)
    water_color = node(function, unreal.MaterialExpressionConstant3Vector, -300, 650, True)
    water_color.set_editor_property("constant", unreal.LinearColor(0.035, 0.28, 0.55, 1))
    foam_color = node(function, unreal.MaterialExpressionConstant3Vector, -300, 800, True)
    foam_color.set_editor_property("constant", unreal.LinearColor(0.84, 0.96, 1.0, 1))
    connect(water_color, base, "A")
    connect(foam_color, base, "B")
    connect(foam, base, "Alpha")
    roughness = node(function, unreal.MaterialExpressionConstant, 100, 550, True)
    roughness.set_editor_property("r", 0.24)
    emissive = node(function, unreal.MaterialExpressionConstant3Vector, 100, 750, True)
    emissive.set_editor_property("constant", unreal.LinearColor(0, 0, 0, 1))
    for index, (name, source) in enumerate([
        ("BaseColor", base), ("Normal", normal), ("Roughness", roughness), ("Emissive", emissive)
    ]):
        output = node(function, unreal.MaterialExpressionFunctionOutput, 500, index * 200, True)
        output.set_editor_property("output_name", name)
        output.set_editor_property("sort_priority", index)
        pins = EDIT.get_material_expression_input_names(output)
        require(len(pins) == 1, "Function output must have one input: " + str(pins))
        connect(source, output, str(pins[0]))
    EDIT.update_material_function(function)
    require(ASSETS.save_loaded_asset(function), "Function save failed")

    material = asset("M_WaveSpec_Opaque", unreal.Material, unreal.MaterialFactoryNew())
    for expression in list(EDIT.get_material_expressions(material)):
        EDIT.delete_material_expression(material, expression)
    require(not EDIT.get_material_expressions(material), "Material cleanup left stale expressions")
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    material.set_editor_property("tangent_space_normal", False)
    call = node(material, unreal.MaterialExpressionMaterialFunctionCall, -100, 0)
    require(call.set_material_function(function), "SetMaterialFunction failed")
    world = node(material, unreal.MaterialExpressionWorldPosition, -500, 0)
    clock = node(material, unreal.MaterialExpressionTime, -500, 200)
    connect(world, call, "WorldPositionCm")
    connect(clock, call, "TimeSeconds")
    properties = {
        "BaseColor": unreal.MaterialProperty.MP_BASE_COLOR,
        "Normal": unreal.MaterialProperty.MP_NORMAL,
        "Roughness": unreal.MaterialProperty.MP_ROUGHNESS,
        "Emissive": unreal.MaterialProperty.MP_EMISSIVE_COLOR,
    }
    for name, prop in properties.items():
        require(EDIT.connect_material_property(call, name, prop), "Material output failed: " + name)
    EDIT.recompile_material(material)
    require(ASSETS.save_loaded_asset(material), "Material save failed")
    REPORT["material"] = {
        "path": material.get_path_name(),
        "function": function.get_path_name(),
        "opaque": material.get_editor_property("blend_mode") == unreal.BlendMode.BLEND_OPAQUE,
        "world_space_normal": not material.get_editor_property("tangent_space_normal"),
        "function_expression_count": len(EDIT.get_material_function_expressions(function)),
        "connections": {},
        "normal_code_sha256": hashlib.sha256(normal.get_editor_property("code").encode()).hexdigest(),
        "foam_code_sha256": hashlib.sha256(foam.get_editor_property("code").encode()).hexdigest(),
        "waves": SPEC["waves"],
        "displacement": False,
        "note": "Opaque normal-only W3 port; no WPO, physics or buoyancy.",
    }
    for name, prop in properties.items():
        source = EDIT.get_material_property_input_node(material, prop)
        output = EDIT.get_material_property_input_node_output_name(material, prop)
        require(source == call and str(output) == name, "Readback mismatch: " + name)
        REPORT["material"]["connections"][name] = {"node": source.get_path_name(), "output": str(output)}
    require(normal.get_editor_property("code") == normal_hlsl(SPEC), "Normal source mismatch")
    require(foam.get_editor_property("code") == foam_hlsl(SPEC), "Foam source mismatch")
    require(len(EDIT.get_material_function_expressions(function)) == 13, "Unexpected function node count")
    return material


def spawn(cls, label, location, rotation=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*location), rotation or unreal.Rotator())
    require(actor is not None, "Actor creation failed: " + label)
    actor.set_actor_label(label)
    actor.set_editor_property("tags", ["ANANTA_W3_20261020", label])
    return actor


def mesh(label, location, scale, material=None, collision=False):
    actor = spawn(unreal.StaticMeshActor, label, location)
    component = actor.static_mesh_component
    component.set_static_mesh(ASSETS.load_asset("/Engine/BasicShapes/Cube"))
    component.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    actor.set_actor_scale3d(unreal.Vector(*scale))
    if material:
        component.set_material(0, material)
    return actor


def build_level(material):
    # Chỉ map mới của pha W3; không load/save hai city hiện có.
    if ASSETS.does_asset_exist(MAP):
        require(unreal.EditorLevelLibrary.load_level(MAP), "Owned comparison map load failed")
        for actor in unreal.EditorLevelLibrary.get_all_level_actors():
            if "ANANTA_W3_20261020" in [str(tag) for tag in actor.tags]:
                unreal.EditorLevelLibrary.destroy_actor(actor)
    else:
        require(unreal.EditorLevelLibrary.new_level(MAP), "Comparison map creation failed")
    boundary = SPEC["boundary"]
    min_x, max_x = boundary["minX"] * 100, boundary["maxX"] * 100
    min_y, max_y = boundary["minZ"] * 100, boundary["maxZ"] * 100
    ocean = spawn(unreal.StaticMeshActor, "W3_Water_StaticVisual", [0, 0, 0])
    ocean.static_mesh_component.set_static_mesh(ASSETS.load_asset("/Engine/BasicShapes/Plane"))
    ocean.static_mesh_component.set_material(0, material)
    ocean.static_mesh_component.set_collision_profile_name("NoCollision")
    ocean.set_actor_scale3d(unreal.Vector((max_x - min_x) / 100, (max_y - min_y) / 100, 1))
    edges = [
        ("West", [min_x - 500, 0, 0], [10, (max_y - min_y + 2000) / 100, 100]),
        ("East", [max_x + 500, 0, 0], [10, (max_y - min_y + 2000) / 100, 100]),
        ("South", [0, min_y - 500, 0], [(max_x - min_x + 2000) / 100, 10, 100]),
        ("North", [0, max_y + 500, 0], [(max_x - min_x + 2000) / 100, 10, 100]),
    ]
    REPORT["boundary"] = []
    for name, location, scale in edges:
        actor = mesh("W3_Boundary_" + name, location, scale, collision=True)
        actor.set_actor_hidden_in_game(True)
        origin, extent = actor.get_actor_bounds(False)
        REPORT["boundary"].append({
            "name": name,
            "origin_cm": [origin.x, origin.y, origin.z],
            "extent_cm": [extent.x, extent.y, extent.z],
            "collision_profile": str(actor.static_mesh_component.get_collision_profile_name()),
            "hidden_in_game": actor.get_editor_property("hidden"),
        })
    # Vật liệu cát engine dùng lại; không sinh texture mới.
    for name, location, scale in [
        ("West", [min_x - 5000, 0, -250], [100, 1000, 5]),
        ("East", [max_x + 5000, 0, -250], [100, 1000, 5]),
        ("South", [0, min_y - 5000, -250], [1400, 100, 5]),
        ("North", [0, max_y + 5000, -250], [1400, 100, 5]),
    ]:
        mesh("W3_Shore_StaticDressing_" + name, location, scale)
    sun = spawn(unreal.DirectionalLight, "W3_Sun", [0, 0, 30000], unreal.Rotator(-45, -30, 0))
    sun.light_component.set_editor_property("intensity", 5.0)
    sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    spawn(unreal.SkyAtmosphere, "W3_Sky", [0, 0, 0])
    sky = spawn(unreal.SkyLight, "W3_SkyLight", [0, 0, 10000])
    sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sky.light_component.set_editor_property("real_time_capture", True)
    REPORT["cameras"] = []
    for scene in SPEC["scenes"]:
        pose = camera_pose(scene)
        location = unreal.Vector(*pose["position_cm"])
        target = unreal.Vector(*pose["target_cm"])
        rotation = unreal.MathLibrary.find_look_at_rotation(location, target)
        camera = spawn(unreal.CameraActor, "W3_Camera_" + scene["id"], pose["position_cm"], rotation)
        component = camera.camera_component
        component.set_editor_property("field_of_view", pose["fov_degrees"])
        component.set_editor_property("aspect_ratio", pose["aspect_ratio"])
        component.set_editor_property("constrain_aspect_ratio", True)
        actual = camera.get_actor_location()
        REPORT["cameras"].append({"id": scene["id"], **pose,
            "readback_position_cm": [actual.x, actual.y, actual.z],
            "readback_fov": component.get_editor_property("field_of_view"),
            "readback_rotation": str(camera.get_actor_rotation()),
        })
    world = unreal.EditorLevelLibrary.get_editor_world()
    REPORT["boundary_traces"] = []
    for name, end in [
        ("West", [min_x - 1000, 0, 200]), ("East", [max_x + 1000, 0, 200]),
        ("South", [0, min_y - 1000, 200]), ("North", [0, max_y + 1000, 200]),
    ]:
        details = unreal.SystemLibrary.line_trace_single(
            world, unreal.Vector(0, 0, 200), unreal.Vector(*end),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True,
        )
        data = details.to_dict() if details is not None else {}
        hit = bool(data.get("blocking_hit", False))
        impact = data.get("impact_point")
        hit_actor = data.get("hit_actor")
        REPORT["boundary_traces"].append({
            "edge": name, "blocked": hit,
            "impact_cm": [impact.x, impact.y, impact.z] if impact else None,
            "actor": hit_actor.get_actor_label() if hit_actor else None,
        })
    require(unreal.EditorLevelLibrary.save_current_level(), "Comparison map save failed")
    REPORT["map"] = MAP
    REPORT["boundary_query_passed"] = all(row["blocked"] for row in REPORT["boundary_traces"])


try:
    build_level(build_material())
    REPORT["authoring_readback_passed"] = True
except Exception as error:
    REPORT["errors"].append(str(error))
    REPORT["authoring_readback_passed"] = False
    raise
finally:
    (TASK / "W3_native_readback.json").write_text(json.dumps(REPORT, indent=2), encoding="utf-8")
    unreal.log("W3_NATIVE_READBACK=" + json.dumps(REPORT))
