"""Replace generated shells and streets in the existing partitioned city, preserving gameplay anchors."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityExpansionLayout import generate
from CityExpansionData import VENUES, GRID_EXTENT
from CityExpansionVenues import furnish
from CityVenueDressing import describe as venue_items, dress as dress_venues
from CityInteriorFinishes import FLOORS
from CityStreetLandmarks import dress as dress_landmarks
from CityCivicDistrict import furnish as furnish_civic
from CityCivicLighting import furnish as light_civic
from CityLivingDetails import furnish as furnish_living
from CityScene import ACTORS, instance_group, mesh_asset, material_asset

MAP = "/Game/ANANTA/Maps/ANANTA_City"


def main():
    data = generate()
    # Kiem tra tai nguyen truoc khi thay geometry trong map da co.
    for name in {g["mesh"] for g in data["groups"]}:
        mesh_asset(name)
    for name in {g["material"] for g in data["groups"] if g["material"]}:
        material_asset(name)
    for item in venue_items():
        mesh_asset(item["mesh"])
        if item.get("material"):
            material_asset(item["material"])
    for name in set(FLOORS.values()):
        material_asset(name)
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(MAP)
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([d.guid for d in descriptors
                                                      if d.native_class.get_name() != "WorldPartitionHLOD"])
    actors = list(ACTORS.get_all_level_actors())
    preserved = {}
    removed = 0
    for actor in actors:
        label = actor.get_actor_label()
        generated = label.startswith("City_") and actor.get_components_by_class(
            unreal.HierarchicalInstancedStaticMeshComponent)
        if generated or label.startswith(("Expansion_", "Dressing_", "Landmark_", "District_", "Living_")):
            assert ACTORS.destroy_actor(actor)
            removed += 1
        elif label in ("City_PlayerStart", "City_PlayerCar", "City_MissionGiver", "City_AnomalyFragment"):
            loc = actor.get_actor_location()
            preserved[label] = [loc.x, loc.y, loc.z]
        elif label == "City_NavigationBounds":
            actor.modify()
            _, extent = actor.get_actor_bounds(False)
            scale = actor.get_actor_scale3d()
            actor.set_actor_scale3d(unreal.Vector(scale.x * (GRID_EXTENT + 2000) / extent.x,
                                                scale.y * (GRID_EXTENT + 2000) / extent.y, scale.z))
    assert len(preserved) == 4, preserved
    hlod = unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD")
    for index, group in enumerate(data["groups"]):
        actor = instance_group(group, index)
        actor.set_editor_property("hlod_layer", hlod)
        if index % 250 == 0:
            unreal.log(f"CITY_EXPANSION_GROUP {index}/{len(data['groups'])}")
    furnish()
    dress_venues()
    dress_landmarks()
    furnish_civic()
    light_civic()
    furnish_living()
    for actor in ACTORS.get_all_level_actors():
        if actor.get_actor_label().startswith(("Dressing_", "Landmark_")):
            actor.set_editor_property("hlod_layer", hlod)
            actor.set_editor_property("is_spatially_loaded", True)
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(map=MAP, stage="expanded", layout=data["audit"], removedGeneratedActors=removed,
                  writtenGroups=len(data["groups"]), writtenInstances=data["audit"]["instances"],
                  actorCount=len(ACTORS.get_all_level_actors()),
                  interiors=["Cafe", "Apartment"] + [v["id"] for v in VENUES], preservedAnchors=preserved,
                  hlodRebuildRequired=True, runtimeVerified=False)
    (PROJECT / "Saved/QA/CityMapBuild.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (PROJECT / "Saved/QA/CityExpansionApplied.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_EXPANSION_SAVED {report}")


if __name__ == "__main__":
    main()
