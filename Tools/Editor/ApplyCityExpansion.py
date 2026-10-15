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
from CityInteractiveTransit import furnish as furnish_transit
from CitySmallDetails import furnish as furnish_small, REQUIRED as SMALL_MESHES
from CityExpansionCleanup import clear_previous
from CityScene import ACTORS, instance_group, mesh_asset, material_asset

MAP = "/Game/ANANTA/Maps/ANANTA_City"


def main():
    data = generate()
    # Kiem tra tai nguyen truoc khi thay geometry trong map da co.
    for name in {g["mesh"] for g in data["groups"]}:
        mesh_asset(name)
    for name in ("Rowboat", "PassengerTrain") + SMALL_MESHES:
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
    removed, preserved = clear_previous(levels)
    hlod = unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD")
    pending_guids = []
    for index, group in enumerate(data["groups"]):
        actor = instance_group(group, index)
        actor.set_editor_property("hlod_layer", hlod)
        pending_guids.append(actor.get_editor_property("actor_guid"))
        if index % 250 == 0:
            unreal.log(f"CITY_EXPANSION_GROUP {index}/{len(data['groups'])}")
        if len(pending_guids) == 1000:
            # Luu package truoc khi do actor, de map lon khong giu ca thanh pho trong RAM Editor.
            assert levels.save_current_level()
            assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
            unreal.WorldPartitionBlueprintLibrary.unload_actors(pending_guids)
            pending_guids.clear()
            unreal.SystemLibrary.collect_garbage()
    if pending_guids:
        assert levels.save_current_level()
        assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        unreal.WorldPartitionBlueprintLibrary.unload_actors(pending_guids)
        unreal.SystemLibrary.collect_garbage()
    furnish()
    dress_venues()
    dress_landmarks()
    furnish_civic()
    light_civic()
    furnish_living()
    transports = furnish_transit()
    small_props = furnish_small()
    for actor in ACTORS.get_all_level_actors():
        if actor.get_actor_label().startswith(("Dressing_", "Landmark_")):
            actor.set_editor_property("hlod_layer", hlod)
            actor.set_editor_property("is_spatially_loaded", True)
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(map=MAP, stage="expanded", layout=data["audit"], removedGeneratedActors=removed,
                  writtenGroups=len(data["groups"]), writtenInstances=data["audit"]["instances"],
                  actorCount=len(unreal.WorldPartitionBlueprintLibrary.get_actor_descs()),
                  interiors=["Cafe", "Apartment"] + [v["id"] for v in VENUES], preservedAnchors=preserved,
                  hlodRebuildRequired=True, runtimeVerified=False,
                  physicalBoundaryCheckRequired=True,
                  interactiveTransportActors=[actor.get_actor_label() for actor in transports])
    report["smallPropActors"] = [actor.get_actor_label() for actor in small_props]
    (PROJECT / "Saved/QA/CityMapBuild.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (PROJECT / "Saved/QA/CityExpansionApplied.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_EXPANSION_SAVED {report}")


if __name__ == "__main__":
    main()
