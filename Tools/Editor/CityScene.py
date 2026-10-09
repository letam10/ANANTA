"""Small Unreal editor helpers for persistent city instance groups and lighting."""

import unreal
from CityAssetOrientation import imported_yaw


ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SUBOBJECTS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
DATA = unreal.SubobjectDataBlueprintFunctionLibrary
ASSET_ROOT = "/Game/ANANTA/City"


def spawn(cls, label, location=(0, 0, 0), yaw=0):
    rotation = unreal.Rotator(pitch=0, yaw=yaw, roll=0)
    actor = ACTORS.spawn_actor_from_class(cls, unreal.Vector(*location), rotation)
    if not actor:
        raise RuntimeError(f"Could not spawn {label}")
    actor.set_actor_label(label)
    actor.set_folder_path("City")
    return actor


def add_component(actor, cls):
    handles = SUBOBJECTS.k2_gather_subobject_data_for_instance(actor)
    params = unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=cls)
    handle, reason = SUBOBJECTS.add_new_subobject(params)
    component = DATA.get_object(DATA.get_data(handle))
    if not component:
        raise RuntimeError(f"Component creation failed: {reason}")
    return component


def mesh_asset(name):
    path = "/Engine/BasicShapes/Cube" if name == "Cube" else f"{ASSET_ROOT}/Meshes/SM_{name}"
    mesh = unreal.load_asset(path)
    if not mesh:
        raise RuntimeError(f"Missing mesh {path}")
    return mesh


def material_asset(name):
    material = unreal.load_asset(f"{ASSET_ROOT}/Materials/M_{name}")
    if not material:
        raise RuntimeError(f"Missing material {name}")
    return material


def promote_cube_component(component):
    mesh = component.get_editor_property("static_mesh")
    path = f"{ASSET_ROOT}/Meshes/SM_CityCubeNanite"
    if not mesh or mesh.get_path_name() != "/Engine/BasicShapes/Cube.Cube" or not component.is_visible():
        return False
    material = component.get_material(0)
    opaque = (unreal.BlendMode.BLEND_OPAQUE, unreal.BlendMode.BLEND_MASKED)
    if not material or material.get_editor_property("blend_mode") not in opaque:
        return False
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        return False
    component.set_static_mesh(unreal.load_asset(path))
    return True


def instance_group(group, index):
    cx, cy = group["cell"]
    origin = group.get("origin", (-60000 + (cx + 0.5) * 12000, -60000 + (cy + 0.5) * 12000, 0))
    actor = spawn(unreal.StaticMeshActor, f"City_{cx}_{cy}_{group['mesh']}_{index}", origin)
    actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
    component = add_component(actor, unreal.HierarchicalInstancedStaticMeshComponent)
    component.set_static_mesh(mesh_asset(group["mesh"]))
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_collision_profile_name("BlockAll" if group["collision"] else "NoCollision")
    if group.get("hidden"):
        component.set_visibility(False)
        component.set_cast_shadow(False)
        component.set_editor_property("affect_distance_field_lighting", False)
        actor.set_editor_property("enable_auto_lod_generation", False)
    if group["material"]:
        component.set_material(0, material_asset(group["material"]))
    promote_cube_component(component)
    small_lighting = ("StreetSign", "BusStopSign", "TrafficSignal", "BikeRack", "HarborBollard",
                      "CeilingFan", "TableLamp", "Microwave", "MakeupCompact", "ToyBlocks",
                      "CoffeeMug", "KitchenBowl", "RoomVase", "BathroomSoap")
    if group["mesh"] in small_lighting or group["material"] in ("RoadMark", "DistrictNeon"):
        # Giu hinh anh/va cham, bo cac chi tiet nho khoi scene distance field cua Lumen.
        component.set_editor_property("affect_distance_field_lighting", False)
    if group["material"] in ("RoadMark", "DistrictNeon"):
        component.set_cast_shadow(False)
    if group["material"] == "DistrictWater":
        component.set_cast_shadow(False)
        component.set_editor_property("affect_distance_field_lighting", False)
        if any(max(item["scale"][:2]) > 1000 for item in group["instances"]):
            # Ba mat bien lon luon nap; khong ghep vao proxy HLOD hay tao bong.
            actor.set_editor_property("is_spatially_loaded", False)
            actor.set_editor_property("enable_auto_lod_generation", False)
    transforms = []
    for item in group["instances"]:
        transform = unreal.Transform()
        transform.translation = unreal.Vector(*item["location"])
        rotation = unreal.Rotator(pitch=0, yaw=imported_yaw(group["mesh"], item["yaw"]), roll=0)
        transform.rotation = rotation.quaternion()
        transform.scale3d = unreal.Vector(*item["scale"])
        transforms.append(transform)
    component.add_instances(transforms, False, True, False)
    if component.get_instance_count() != len(transforms):
        raise RuntimeError(f"Incomplete instance group {index}")
    if group["material"] != "DistrictWater" or not any(
            max(item["scale"][:2]) > 1000 for item in group["instances"]):
        actor.set_editor_property("is_spatially_loaded", True)
    return actor


def prop(name, label, location, yaw=0, scale=(1, 1, 1), collision=True):
    actor = spawn(unreal.StaticMeshActor, label, location, imported_yaw(name, yaw))
    component = actor.static_mesh_component
    component.set_static_mesh(mesh_asset(name))
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor


def box(label, location, size, material="Concrete", collision=True):
    actor = prop("Cube", label, location, scale=tuple(v / 100 for v in size), collision=collision)
    actor.static_mesh_component.set_material(0, material_asset(material))
    promote_cube_component(actor.static_mesh_component)
    return actor


def text(label, message, location, yaw=0, size=65):
    actor = spawn(unreal.TextRenderActor, label, location, yaw)
    component = actor.get_component_by_class(unreal.TextRenderComponent)
    component.set_text(message)
    component.set_world_size(size)
    component.set_text_render_color(unreal.Color(218, 236, 236, 255))
    component.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    return actor


def lighting():
    sun = spawn(unreal.DirectionalLight, "City_Sun", (0, 0, 14000))
    sun.set_actor_rotation(unreal.Rotator(pitch=-38, yaw=-28, roll=0), False)
    sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sun.light_component.set_intensity(60000)
    sun.light_component.set_editor_property("atmosphere_sun_light", True)
    sky = spawn(unreal.SkyLight, "City_Sky")
    sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sky.light_component.set_editor_property("real_time_capture", True)
    sky.light_component.set_intensity(1.15)
    spawn(unreal.SkyAtmosphere, "City_Atmosphere")
    fog = spawn(unreal.ExponentialHeightFog, "City_Fog", (0, 0, -250))
    fog.component.set_editor_property("fog_density", 0.002)
    fog.component.set_editor_property("start_distance", 4000.0)
    fog.component.set_editor_property("fog_height_falloff", 0.18)
    volume = spawn(unreal.PostProcessVolume, "City_Exposure")
    volume.set_editor_property("unbound", True)
    settings = volume.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_min_brightness", True)
    settings.set_editor_property("override_auto_exposure_max_brightness", True)
    settings.set_editor_property("auto_exposure_min_brightness", 5.0)
    settings.set_editor_property("auto_exposure_max_brightness", 16.0)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", -0.35)
    settings.set_editor_property("override_motion_blur_amount", True)
    settings.set_editor_property("motion_blur_amount", 0.15)
    volume.set_editor_property("settings", settings)
    for actor in (sun, sky, fog, volume):
        actor.set_editor_property("is_spatially_loaded", False)


def camera(label, location, rotation):
    actor = spawn(unreal.CameraActor, label, location)
    actor.set_actor_rotation(unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]), False)
    actor.camera_component.set_editor_property("field_of_view", 75)
    return actor


def navigation():
    volume = spawn(unreal.NavMeshBoundsVolume, "City_NavigationBounds", (0, 0, 1500))
    _, extent = volume.get_actor_bounds(False)
    if min(extent.x, extent.y, extent.z) <= 0:
        raise RuntimeError("Navigation volume has no brush bounds")
    volume.set_actor_scale3d(unreal.Vector(61000 / extent.x, 61000 / extent.y, 2500 / extent.z))
    volume.set_editor_property("is_spatially_loaded", False)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nav = unreal.CityEditorTools.ensure_navigation(world)
    if not nav:
        raise RuntimeError("NavigationSystem could not create Recast navigation data")
    nav.set_actor_label("City_RecastNavMesh")
    nav.set_editor_property("runtime_generation", unreal.RuntimeGenerationType.DYNAMIC)
    nav.set_editor_property("force_rebuild_on_load", True)
    nav.set_editor_property("can_be_main_nav_data", True)
    nav.set_editor_property("is_spatially_loaded", False)
    return volume
