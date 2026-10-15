"""Refresh authored props without replacing the generated city or gameplay actors."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityScene import ACTORS, mesh_asset, material_asset
from CityVenueDressing import describe as venue_items, dress as dress_venues
from CityStreetLandmarks import describe as landmark_items, dress as dress_landmarks
from RefineCityAtmosphere import main as refine_atmosphere


def main():
    items = venue_items() + landmark_items()
    for name in {item["mesh"] for item in items}:
        mesh_asset(name)
    for name in {item["material"] for item in items if item.get("material")}:
        material_asset(name)
    refine_atmosphere()
    # Chi thay lop trang tri; giu nguyen cac actor nhiem vu va dich vu da kiem chung.
    before = list(ACTORS.get_all_level_actors())
    for actor in before:
        if actor.get_actor_label().startswith(("Dressing_", "Landmark_")):
            assert ACTORS.destroy_actor(actor)
    dress_venues()
    dress_landmarks()
    hlod = unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD")
    labels = []
    for actor in ACTORS.get_all_level_actors():
        if actor.get_actor_label().startswith(("Dressing_", "Landmark_")):
            actor.set_editor_property("hlod_layer", hlod)
            actor.set_editor_property("is_spatially_loaded", True)
            labels.append(actor.get_actor_label())
    expected = [item["label"] for item in venue_items() + landmark_items()]
    assert len(labels) == len(set(labels))
    assert set(labels) == set(expected)
    # Save level xu ly ca external package cua actor da xoa, tranh tai xuat hien khi mo map.
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(venueProps=len(venue_items()), landmarkProps=len(landmark_items()),
                  total=len(labels), labels=sorted(labels), hlodRebuildRequired=True, runtimeVerified=False)
    (PROJECT / "Saved/QA/CityDressingApplied.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"CITY_DRESSING_APPLIED total={len(labels)}")


if __name__ == "__main__":
    main()
