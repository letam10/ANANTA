"""Apply the first hero-slice corrections inside a running UE editor.

This is intentionally small and idempotent.  It closes the visible ground gap,
reactivates the authored light actors, and leaves a JSON report under Saved so
the next MCP readback can verify what actually changed.

Run from UE's Python environment after the Restore Packages dialog is handled.
"""

from __future__ import annotations

import json
from pathlib import Path

import unreal


MAP_PATH = "/Game/ANANTA/Maps/ANANTA_Slice"
MESH_ROOT = "/Game/ANANTA/Generated/NovaCitySlice/NovaCitySlice/StaticMeshes"
REPORT_PATH = Path(unreal.Paths.project_saved_dir()) / "Generated" / "NovaHeroApplyReport.json"


def load_asset(path: str):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        raise RuntimeError(f"Missing UE asset: {path}")
    return asset


def actors() -> list[unreal.Actor]:
    return list(unreal.EditorLevelLibrary.get_all_level_actors())


def find_label(label: str):
    for actor in actors():
        if actor.get_actor_label() == label:
            return actor
    return None


def set_actor_label(actor, label: str) -> None:
    if actor.get_actor_label() != label:
        actor.set_actor_label(label, mark_dirty=True)


def spawn_mesh_once(mesh_path: str, label: str, location: unreal.Vector,
                    scale: unreal.Vector, yaw: float = 0.0):
    existing = find_label(label)
    if existing:
        return existing, False
    mesh = load_asset(mesh_path)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if not actor:
        raise RuntimeError(f"Could not spawn {label}")
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.set_actor_scale3d(scale)
    set_actor_label(actor, label)
    return actor, True


def activate_light(label: str) -> bool:
    actor = find_label(label)
    if not actor:
        return False
    # The earlier imported scene had these flags disabled despite containing lights.
    if actor.has_editor_property("b_enabled"):
        actor.set_editor_property("b_enabled", True)
    root = actor.get_editor_property("root_component")
    if root and root.has_editor_property("b_auto_activate"):
        root.set_editor_property("b_auto_activate", True)
    if root:
        root.activate(True)
    return True


def main() -> dict:
    unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
    report = {
        "map": MAP_PATH,
        "created": [],
        "existing": [],
        "lightsActivated": [],
    }

    ground = f"{MESH_ROOT}/Nova_Ground"
    road = f"{MESH_ROOT}/Nova_Road_Main"
    sidewalk = f"{MESH_ROOT}/Nova_Sidewalk_+1"

    pieces = [
        (ground, "Nova_HeroGround_Continuous", unreal.Vector(12000.0, 12000.0, -220.0), unreal.Vector(12.0, 12.0, 1.0), 0.0),
        (road, "Nova_HeroRoad_EastWest", unreal.Vector(12000.0, 12000.0, -70.0), unreal.Vector(12.0, 3.0, 1.0), 0.0),
        (road, "Nova_HeroRoad_NorthSouth", unreal.Vector(12000.0, 12000.0, -65.0), unreal.Vector(12.0, 3.0, 1.0), 90.0),
        (sidewalk, "Nova_HeroSidewalk_EastWest_North", unreal.Vector(12000.0, 13350.0, -40.0), unreal.Vector(12.0, 3.0, 1.0), 0.0),
        (sidewalk, "Nova_HeroSidewalk_EastWest_South", unreal.Vector(12000.0, 10650.0, -40.0), unreal.Vector(12.0, 3.0, 1.0), 0.0),
        (sidewalk, "Nova_HeroSidewalk_NorthSouth_East", unreal.Vector(13350.0, 12000.0, -40.0), unreal.Vector(12.0, 3.0, 1.0), 90.0),
        (sidewalk, "Nova_HeroSidewalk_NorthSouth_West", unreal.Vector(10650.0, 12000.0, -40.0), unreal.Vector(12.0, 3.0, 1.0), 90.0),
    ]
    for mesh_path, label, location, scale, yaw in pieces:
        _, created = spawn_mesh_once(mesh_path, label, location, scale, yaw)
        report["created" if created else "existing"].append(label)

    for label in ("ANANTA_Sun", "ANANTA_Sky", "Nova_HeightFog"):
        if activate_light(label):
            report["lightsActivated"].append(label)

    unreal.EditorLevelLibrary.save_current_level()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(json.dumps(report))
    return report


if __name__ == "__main__":
    main()
