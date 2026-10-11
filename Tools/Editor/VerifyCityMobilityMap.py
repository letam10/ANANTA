"""Reopen the written map and inspect expansion, transport assets and solid street props."""

import json
import math
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityExpansionData import GRID_EXTENT
from CityCivicDistrict import SERVICES
from CityActorBatches import batches


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    expected = json.loads((PROJECT / "Saved/QA/CityExpansionApplied.json").read_text(encoding="utf-8"))
    meshes = {}
    groups = 0
    instances = 0
    colliders = 0
    services = []
    living = []
    civic_lights = 0
    extrema = [0, 0]
    boundary_edges = []
    for actors in batches(descriptors):
        for actor in actors:
            if actor.get_actor_label().startswith("Living_"):
                living.append(actor.get_actor_label())
            if actor.get_actor_label().startswith("District_Light_") and isinstance(actor, unreal.RectLight):
                civic_lights += 1
            if isinstance(actor, unreal.CityServiceInteractable):
                services.append(str(actor.get_editor_property("interaction_id")))
            for component in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
                groups += 1
                count = component.get_instance_count()
                instances += count
                mesh = component.get_editor_property("static_mesh")
                name = mesh.get_name()
                meshes[name] = meshes.get(name, 0) + count
                if not component.is_visible() and str(component.get_collision_profile_name()) == "BlockAll":
                    colliders += count
                    for index in range(count):
                        transform = component.get_instance_transform(index, world_space=True)
                        scale = transform.scale3d
                        if abs(scale.z - 400) < .01:
                            position = transform.translation
                            if abs(scale.x - 1) < .01:
                                boundary_edges.append(abs(position.x) - 50)
                            elif abs(scale.y - 1) < .01:
                                boundary_edges.append(abs(position.y) - 50)
                position = actor.get_actor_location()
                extrema[0] = max(extrema[0], abs(position.x))
                extrema[1] = max(extrema[1], abs(position.y))
    assert groups == expected["writtenGroups"], (groups, expected["writtenGroups"])
    assert instances == expected["writtenInstances"], (instances, expected["writtenInstances"])
    assert len(services) == 12 and len(set(services)) == 12, services
    assert all(name + "_Read" in services for name, _ in SERVICES), services
    expected_road_extent = math.sqrt(expected["layout"]["roadBlocks"]) * 6000
    assert min(extrema) >= expected_road_extent - 6000, extrema
    assert meshes.get("SM_DetailedPlanter", 0) > 1000, meshes
    assert meshes.get("SM_DetailedStreetLamp", 0) > 1000, meshes
    assert colliders > 1000, colliders
    assert meshes.get("SM_FerrisWheel") == 1, meshes
    extra = expected.get("interactiveTransportActors", []) + expected.get("smallPropActors", [])
    extra += expected.get("civicDressingActors", [])
    assert len(living) == len(set(living)) == 19 + len(extra), living
    assert set(extra).issubset(living), extra
    assert civic_lights == 16, civic_lights
    if expected.get("physicalBoundaryCheckRequired"):
        assert len(boundary_edges) == 4, boundary_edges
        target = expected["layout"]["widthMetres"] * 50
        assert all(abs(edge - target) < 1 for edge in boundary_edges), (boundary_edges, target)
    report = dict(status="PASS", groups=groups, instances=instances, hiddenSolidPrimitives=colliders,
                  generatedActorExtremaCm=extrema, services=sorted(services), meshes=meshes,
                  livingActors=sorted(living), civicLights=civic_lights,
                  physicalBoundaryEdgesCm=boundary_edges,
                  runtimeCollisionAccepted=False, renderedArtAccepted=False)
    path = PROJECT / "Saved/QA/CityMobilityMapReadback.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_MOBILITY_MAP_READBACK_OK groups={groups} instances={instances} services={len(services)}")


if __name__ == "__main__":
    main()
