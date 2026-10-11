"""Read back the converted map, audit bodies and inspect the observed Transit sidewalk block."""

import json
from pathlib import Path
import sys
import unreal


ROOT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from VerifyCityMobilityMap import main as verify_map


def main():
    verify_map()
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    report = unreal.CityEditorTools.audit_loaded_collision(world)
    (ROOT / "Saved/QA/CityWholeMapCollision.txt").write_text(report, encoding="utf-8")
    assert report.startswith("passed=1\n"), report
    start = unreal.Vector(46393.31, 1088.84, 109.15)
    end = unreal.Vector(46700, 1088.84, 109.15)
    hits = unreal.SystemLibrary.capsule_trace_multi(
        world, start, end, 38, 92, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        False, [], unreal.DrawDebugTrace.NONE, True)
    rows = []
    for hit in hits or []:
        values = unreal.GameplayStatics.break_hit_result(hit)
        actor, component = values[9], values[10]
        rows.append(dict(blocking=values[0], overlap=values[1], distance=values[3],
                         actor=actor.get_actor_label() if actor else "",
                         component=component.get_name() if component else "",
                         impact=str(values[5])))
    mesh = unreal.load_asset("/Game/ANANTA/City/Meshes/SM_CityCubeNanite")
    assert mesh.get_editor_property("nanite_settings").get_editor_property("enabled")
    result = dict(collisionAudit="PASS", transitStaticSweep=rows, scope="Editor static map; no runtime NPCs")
    (ROOT / "Saved/QA/CityNaniteCollision.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    unreal.log("CITY_NANITE_COLLISION " + json.dumps(result))


if __name__ == "__main__":
    main()
