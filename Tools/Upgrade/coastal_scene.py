"""Metric placement and tiled HISM batches; never edit the original map."""

import json
import math
from pathlib import Path

import unreal


ROOT = "/Game/ANANTA/CoastalUpgrade"


class Scene:
    def __init__(self, palette):
        self.palette = palette
        self.subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        self.batches = {}
        self.placements = []
        self.models = {}
        self.review_views = []
        source = Path(unreal.Paths.project_dir()) / "Assets" / "CoastalUpgrade" / "manifest.json"
        self.model_data = {item["name"]: item for item in json.loads(source.read_text())["models"]}
        self.dimensions = {name: item["dimensions_m"] for name, item in self.model_data.items()}
        self.cube = unreal.load_asset("/Engine/BasicShapes/Cube")
        self.cylinder = unreal.load_asset("/Engine/BasicShapes/Cylinder")
        self.sphere = unreal.load_asset("/Engine/BasicShapes/Sphere")
        self.surface = unreal.load_asset(f"{ROOT}/M_CoastalSurface")
        unreal.MaterialEditingLibrary.set_base_material_usage(
            self.surface, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES
        )
        unreal.MaterialEditingLibrary.recompile_material(self.surface)
        unreal.EditorAssetLibrary.save_loaded_asset(self.surface)

    def spawn(self, cls, label, position, yaw=0):
        actor = self.subsystem.spawn_actor_from_class(
            cls, unreal.Vector(*(value * 100 for value in position)), unreal.Rotator(yaw=yaw)
        )
        assert actor, label
        actor.set_actor_label("Coast_" + label)
        return actor

    def instance(self, mesh, mat, position, size=(1, 1, 1), yaw=0, collision=True, cull=0, pitch=0):
        tile = (math.floor(position[0] / 64), math.floor(position[1] / 64))
        cull_band = 0 if cull <= 0 else max(10, min(300, int(math.ceil(cull / 5) * 5)))
        key = (mesh.get_name(), mat.get_name(), tile, collision, cull_band)
        if key not in self.batches:
            actor = self.spawn(unreal.CoastalBatch, f"Batch_{len(self.batches):03}", (0, 0, 0))
            component = actor.instances
            component.set_static_mesh(mesh)
            component.set_material(0, mat)
            component.set_collision_enabled(
                unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION
            )
            start_cull_cm = int(cull_band * 100)
            end_cull_cm = int(cull_band * 120)
            component.set_cull_distances(start_cull_cm, end_cull_cm)
            component.set_editor_property(
                "affect_distance_field_lighting", cull_band == 0 or cull_band > 150
            )
            component.set_editor_property(
                "cast_shadow", collision or (cull_band > 50 and mesh != self.cube)
            )
            self.batches[key] = component
        transform = unreal.Transform(
            location=unreal.Vector(*(value * 100 for value in position)),
            rotation=unreal.Rotator(pitch=pitch, yaw=yaw), scale=unreal.Vector(*size),
        )
        index = self.batches[key].add_instance(transform, world_space=True)
        self.placements.append({"mesh": mesh.get_name(), "material": mat.get_name(),
                                "pitch": pitch, "position_m": position,
                                "scale": size, "yaw": yaw, "batch": self.batches[key].get_owner().get_actor_label(),
                                "instance": index, "collision": collision, "cull_m": cull})

    def box(self, position, size, color="Concrete", yaw=0, collision=True, pitch=0):
        self.instance(self.cube, self.palette[color], position, size, yaw, collision, pitch=pitch)

    def model(self, name, position, yaw=0, scale=(1, 1, 1), collision=None):
        if name not in self.models:
            self.models[name] = unreal.load_asset(f"{ROOT}/Models/{name}")
        mesh = self.models[name]
        assert mesh, name
        diameter = max(self.dimensions[name]) * max(scale)
        # Kích thước trên màn hình: d = đường kính * chiều ngang / (2*tan(FOV/2)*pixel).
        distance = min(300, max(10, diameter * 1600 / (2 * math.tan(math.pi / 4) * 4)))
        if collision is None:
            collision = diameter > 0.8 and name not in ("OperaShells", "PotPlant")
        self.instance(mesh, self.surface, position, scale, yaw, collision, distance)

    def text(self, label, position, text, yaw=90, size=0.45, color=(230, 235, 225, 255)):
        actor = self.spawn(unreal.TextRenderActor, label, position, yaw)
        component = actor.text_render
        component.set_text(text)
        component.set_world_size(size * 100)
        component.set_text_render_color(unreal.Color(*color))
        component.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        component.set_editor_property("cast_shadow", False)
        return actor

    def action(
        self,
        name,
        position,
        message,
        kind=0,
        model="FactoryControl",
        yaw=0,
        schedule=False,
    ):
        actor = self.spawn(unreal.CoastalInteractable, name, position, yaw)
        actor.action_name = name.replace("_", " ")
        actor.message = message
        actor.kind = kind
        actor.mesh.set_static_mesh(unreal.load_asset(f"{ROOT}/Models/{model}"))
        actor.mesh.set_material(0, self.surface)
        if schedule and kind == 2:
            actor.set_editor_property("schedule_enabled", True)
            actor.set_editor_property("schedule_radius", 120.0)
            actor.set_editor_property("schedule_speed", 0.65)
        if kind == 1:
            actor.mesh.set_relative_location(unreal.Vector(0, 45, 0), False, False)
        if kind == 4:
            actor.mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        return actor

    def vehicle(self, name, position, yaw=0, boat=False):
        actor = self.spawn(unreal.CoastalVehicle, name, position, yaw)
        actor.mesh.set_static_mesh(unreal.load_asset(f"{ROOT}/Models/{name}"))
        actor.mesh.set_material(0, self.surface)
        actor.vehicle_name = name
        actor.boat = boat
        bounds = self.dimensions[name]
        if boat:
            actor.collision.set_box_extent(unreal.Vector(bounds[0] * 47, bounds[1] * 43, bounds[2] * 18))
        else:
            actor.collision.set_box_extent(unreal.Vector(bounds[0] * 47, bounds[1] * 43, bounds[2] * 38))
        actor.mesh.set_relative_location(unreal.Vector(0, 0, -bounds[2] * 40), False, False)
        return actor
