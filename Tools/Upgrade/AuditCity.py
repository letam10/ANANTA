"""Read the saved map and asset state without editing existing content."""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import unreal


def main():
    project = Path(unreal.Paths.project_dir())
    output = project / "Saved" / "Upgrade"
    output.mkdir(parents=True, exist_ok=True)
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/ANANTA/Maps/ANANTA_Slice")
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = subsystem.get_all_level_actors()
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "map": "/Game/ANANTA/Maps/ANANTA_Slice",
        "actor_count": len(actors),
        "classes": dict(Counter(actor.get_class().get_name() for actor in actors)),
        "actors": [],
        "meshes": {},
    }
    for actor in actors:
        location = actor.get_actor_location()
        origin, extent = actor.get_actor_bounds(False)
        item = {
            "label": actor.get_actor_label(),
            "class": actor.get_class().get_name(),
            "location_cm": [location.x, location.y, location.z],
            "bounds_center_cm": [origin.x, origin.y, origin.z],
            "bounds_extent_cm": [extent.x, extent.y, extent.z],
        }
        if isinstance(actor, unreal.StaticMeshActor):
            component = actor.static_mesh_component
            mesh = component.static_mesh
            if mesh:
                item["mesh"] = mesh.get_path_name()
                item["materials"] = [
                    component.get_material(index).get_path_name()
                    if component.get_material(index) else None
                    for index in range(component.get_num_materials())
                ]
                report["meshes"][mesh.get_path_name()] = (
                    report["meshes"].get(mesh.get_path_name(), 0) + 1
                )
        report["actors"].append(item)
    report["assets"] = list(unreal.EditorAssetLibrary.list_assets("/Game/ANANTA", recursive=True))
    for class_path in (
        "/Game/ANANTA/Gameplay/BP_NovaGameMode.BP_NovaGameMode_C",
    ):
        cls = unreal.load_class(None, class_path)
        if cls:
            default = unreal.get_default_object(cls)
            report[class_path] = str(default)
            if "GameMode" in class_path:
                report["default_pawn"] = str(default.get_editor_property("default_pawn_class"))
    target = output / "baseline-map.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"UPGRADE_AUDIT_OK {len(actors)} actors; report={target}")


if __name__ == "__main__":
    main()
