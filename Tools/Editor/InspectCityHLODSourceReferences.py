"""Check the native HLOD metadata bridge against one existing proxy; no expanded-map acceptance."""

import json
from pathlib import Path
import unreal


def main():
    root = Path(unreal.Paths.project_dir()).resolve()
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    library = unreal.WorldPartitionBlueprintLibrary
    candidates = [item for item in library.get_actor_descs() if item.native_class.get_name() == "WorldPartitionHLOD"]
    assert candidates, "No existing HLOD proxy for metadata API check"
    item = candidates[0]
    library.pin_actors([item.guid])
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    wanted = unreal.GuidLibrary.conv_guid_to_string(item.guid)
    actors = [actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WorldPartitionHLOD)
              if unreal.GuidLibrary.conv_guid_to_string(actor.get_editor_property("actor_guid")) == wanted]
    assert len(actors) == 1, f"Expected one pinned HLOD actor for {wanted}; found {len(actors)}"
    metadata = json.loads(unreal.CityEditorTools.hlod_source_actor_references(actors[0]))
    references = metadata.get("references", [])
    passed = metadata.get("available") is True and bool(references)
    for reference in references:
        guid = reference["guid"].replace("-", "").lower()
        passed &= bool(reference["path"]) and len(guid) == 32 and guid != "0" * 32
        passed &= all(value in "0123456789abcdef" for value in guid)
    result = dict(passed=passed, proxy=actors[0].get_actor_label(), references=len(references),
                  sample=references[:3], mapCoverageAccepted=False, renderedArtAccepted=False,
                  scope="Native metadata API binding on one existing proxy only")
    (root / "Saved/QA/CityHLODSourceBridge.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    library.unpin_actors([item.guid])
    assert passed, metadata
    unreal.log(f"CITY_HLOD_SOURCE_BRIDGE_OK references={len(references)} scope=metadata_api_only")


if __name__ == "__main__":
    main()
