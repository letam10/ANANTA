"""Inspect every persisted collision body and every road sample in bounded loading batches."""

import json
from pathlib import Path
import sys
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityExpansionData import GRID_EXTENT


def numbers(report):
    return {key: int(value) for line in report.splitlines() if "=" in line
            for key, value in [line.split("=", 1)] if value.isdigit()}


def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    library = unreal.WorldPartitionBlueprintLibrary
    descriptors = library.get_actor_descs()
    guids = [item.guid for item in descriptors if item.native_class.get_name() != "WorldPartitionHLOD"]
    library.unload_actors(guids)
    totals = dict(blockingComponents=0, blockingInstances=0, roadSamples=0, errors=0)
    failures = []
    for offset in range(0, len(guids), 1000):
        batch = guids[offset:offset + 1000]
        library.load_actors(batch)
        report = unreal.CityEditorTools.audit_collision_actors(world, batch)
        counts = numbers(report)
        for key in ("blockingComponents", "blockingInstances", "errors"):
            totals[key] += counts[key]
        if counts["passed"] != 1:
            failures.append(report)
        library.unload_actors(batch)
        unreal.SystemLibrary.collect_garbage()
        unreal.log(f"CITY_COLLISION_BODY_BATCH {offset + len(batch)}/{len(guids)}")
    # Moi vung 960 m; buffer nap ca component co bounds cat qua mat duong o bien vung.
    step = 96000
    regions = 0
    for x in range(-GRID_EXTENT, GRID_EXTENT, step):
        for y in range(-GRID_EXTENT, GRID_EXTENT, step):
            xmax = min(x + step, GRID_EXTENT) + (1 if x + step >= GRID_EXTENT else 0)
            ymax = min(y + step, GRID_EXTENT) + (1 if y + step >= GRID_EXTENT else 0)
            box = unreal.Box(min=unreal.Vector(x - 7000, y - 7000, -2000),
                             max=unreal.Vector(xmax + 7000, ymax + 7000, 80000))
            intersecting = library.get_intersecting_actor_descs(box)
            loaded = [item.guid for item in intersecting if item.native_class.get_name() != "WorldPartitionHLOD"]
            library.load_actors(loaded)
            report = unreal.CityEditorTools.audit_road_region(world, unreal.Vector(x, y, -1000),
                                                             unreal.Vector(xmax, ymax, 1000))
            counts = numbers(report)
            for key in ("roadSamples", "errors"):
                totals[key] += counts[key]
            if counts["passed"] != 1:
                failures.append(report)
            library.unload_actors(loaded)
            unreal.SystemLibrary.collect_garbage()
            regions += 1
            unreal.log(f"CITY_COLLISION_ROAD_REGION {regions}/49")
    passed = totals["errors"] == 0 and totals["blockingComponents"] > 0 and totals["roadSamples"] > 0
    result = dict(passed=passed, **totals, descriptorsAudited=len(guids), roadRegions=regions,
                  scope="All persisted blocking bodies and grid road support; not every player trajectory",
                  failures=failures)
    path = ROOT / "Saved/QA/CityWholeMapCollision.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    report = f"passed={int(passed)}\n" + "".join(f"{key}={value}\n" for key, value in totals.items())
    report += "scope=" + result["scope"] + "\n" + "\n".join(failures)
    path.with_suffix(".txt").write_text(report, encoding="utf-8")
    assert passed, f"City collision audit failed; see {path}"
    unreal.log("CITY_WHOLE_MAP_COLLISION_OK " + report.replace("\n", " "))


if __name__ == "__main__":
    main()
