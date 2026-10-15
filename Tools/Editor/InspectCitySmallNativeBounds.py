"""Read native small props and nearby furniture without changing the saved city."""

import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityActorBatches import batches
from CitySmallDetails import REQUIRED, describe

NAMES = (*REQUIRED, "Microwave", "TableLamp", "CafeCounter", "CafeTable",
         "House_vintage_electric_kettle", "House_modern_coffee_table_01")

def vector(value):
    return [value.x, value.y, value.z]

def world_bounds(mesh, transform):
    box = mesh.get_bounding_box()
    corners = [unreal.MathLibrary.transform_location(transform, unreal.Vector(*point))
               for point in itertools.product((box.min.x, box.max.x), (box.min.y, box.max.y),
                                              (box.min.z, box.max.z))]
    return dict(min=[min(vector(point)[i] for point in corners) for i in range(3)],
                max=[max(vector(point)[i] for point in corners) for i in range(3)])

def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    library = unreal.WorldPartitionBlueprintLibrary
    regions = [(item["location"][0] - 180, item["location"][1] - 180,
                item["location"][0] + 180, item["location"][1] + 180) for item in describe()]
    selected = {}
    for x1, y1, x2, y2 in regions:
        box = unreal.Box(min=unreal.Vector(x1, y1, 0), max=unreal.Vector(x2, y2, 400))
        for desc in library.get_intersecting_actor_descs(box):
            if desc.native_class.get_name() != "WorldPartitionHLOD":
                selected[unreal.GuidLibrary.conv_guid_to_string(desc.guid)] = desc
    for desc in library.get_actor_descs():
        if str(desc.label).startswith("Living_Small_"):
            selected[unreal.GuidLibrary.conv_guid_to_string(desc.guid)] = desc
    entries = []
    meshes = {}
    for name in NAMES:
        mesh = unreal.load_asset(f"/Game/ANANTA/City/Meshes/SM_{name}")
        assert mesh, name
        box = mesh.get_bounding_box()
        meshes[name] = dict(min=vector(box.min), max=vector(box.max))
    for actors in batches(list(selected.values()), size=200):
        for actor in actors:
            for component in actor.get_components_by_class(unreal.StaticMeshComponent):
                mesh = component.get_editor_property("static_mesh")
                if not mesh:
                    continue
                transforms = [(None, component.get_world_transform())]
                if isinstance(component, unreal.InstancedStaticMeshComponent):
                    transforms = [(i, component.get_instance_transform(i, world_space=True))
                                  for i in range(component.get_instance_count())]
                for index, transform in transforms:
                    bounds = world_bounds(mesh, transform)
                    nearby = any(bounds["min"][0] < x2 and bounds["max"][0] > x1
                                 and bounds["min"][1] < y2 and bounds["max"][1] > y1
                                 and bounds["min"][2] < 400 for x1, y1, x2, y2 in regions)
                    if not nearby and not actor.get_actor_label().startswith("Living_Small_"):
                        continue
                    layer = actor.get_editor_property("hlod_layer")
                    entries.append(dict(label=actor.get_actor_label(), mesh=mesh.get_name(),
                                        guid=unreal.GuidLibrary.conv_guid_to_string(
                                            actor.get_editor_property("actor_guid")), instance=index,
                                        bounds=bounds, location=vector(transform.translation),
                                        scale=vector(transform.scale3d),
                                        collisionProfile=str(component.get_collision_profile_name()),
                                        spatiallyLoaded=actor.get_editor_property("is_spatially_loaded"),
                                        autoHLOD=actor.get_editor_property("enable_auto_lod_generation"),
                                        hlodLayer=layer.get_path_name() if layer else None))
    path = ROOT / "Saved/QA/CitySmallNativeBounds.json"
    path.write_text(json.dumps(dict(schemaVersion=1, completedUtc=datetime.now(timezone.utc).isoformat(),
                                    meshes=meshes, actors=entries, sourceActors=len(selected),
                                    persistedMap=True, changed=False), indent=2), encoding="utf-8")
    unreal.log(f"CITY_SMALL_NATIVE_BOUNDS_OK entries={len(entries)} sources={len(selected)}")

if __name__ == "__main__":
    main()
