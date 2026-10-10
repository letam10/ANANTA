"""Sweep the unchanged player capsule through the persisted map boundary colliders."""

import json
from pathlib import Path
import unreal


def main():
    root = Path(unreal.Paths.project_dir()).resolve()
    expected = json.loads((root / "Saved/QA/CityExpansionApplied.json").read_text(encoding="utf-8"))
    assert expected.get("physicalBoundaryCheckRequired"), "New boundary map has not been applied"
    edge = expected["layout"]["widthMetres"] * 50
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    library = unreal.WorldPartitionBlueprintLibrary
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    loaded = {}
    points = [(edge, 0), (-edge, 0), (0, edge), (0, -edge), (edge, -130000), (130000, -edge)]
    points += [(x * edge, y * edge) for x in (-1, 1) for y in (-1, 1)]
    for x, y in points:
        box = unreal.Box(min=unreal.Vector(x - 500, y - 500, -500),
                         max=unreal.Vector(x + 500, y + 500, 2500))
        for item in library.get_intersecting_actor_descs(box):
            if item.native_class.get_name() != "WorldPartitionHLOD":
                key = unreal.GuidLibrary.conv_guid_to_string(item.guid)
                loaded[key] = item.guid
    assert loaded, "No boundary-region actors loaded"
    library.load_actors(list(loaded.values()))
    report = unreal.CityEditorTools.audit_world_boundaries(world, edge)
    counts = {key: int(value) for line in report.splitlines() if "=" in line
              for key, value in [line.split("=", 1)] if value.isdigit()}
    result = dict(**counts, extentCm=edge, capsuleRadiusCm=38, capsuleHalfHeightCm=92,
                  loadedDescriptors=len(loaded), details=report,
                  scope="Persisted edge and corner capsule sweeps; no gameplay coordinate clamp")
    path = root / "Saved/QA/CityWorldBoundaries.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    library.unload_actors(list(loaded.values()))
    assert counts.get("passed") == 1 and counts.get("boundarySamples") == 14, report
    unreal.log("CITY_WORLD_BOUNDARIES_OK samples=14 capsule=38/92")


if __name__ == "__main__":
    main()
