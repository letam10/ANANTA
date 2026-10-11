"""Compare asymmetric source bounds with imported meshes to detect an axis flip."""

import json
from pathlib import Path
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()


def main():
    records = []
    for name in ("manifest.json", "expansion_manifest.json"):
        data = json.loads((PROJECT / "Assets/City" / name).read_text(encoding="utf-8"))
        for item in data["meshes"]:
            if not item["id"].startswith("Facade"):
                continue
            mesh = unreal.load_asset("/Game/ANANTA/City/Meshes/SM_" + item["id"])
            bounds = mesh.get_bounding_box()
            source = item["boundsCm"]
            slots = [str(slot.material_interface.get_name()) for slot in mesh.static_materials]
            record = dict(id=item["id"], sourceMin=source["min"], sourceMax=source["max"],
                          importedMin=[bounds.min.x, bounds.min.y, bounds.min.z],
                          importedMax=[bounds.max.x, bounds.max.y, bounds.max.z], materials=slots)
            records.append(record)
            unreal.log(f"CITY_FACADE_BOUNDS {record}")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    nav = []
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if actor.get_actor_label() in ("City_NavigationBounds", "City_RecastNavMesh"):
            origin, extent = actor.get_actor_bounds(False)
            item = dict(label=actor.get_actor_label(), origin=[origin.x, origin.y, origin.z],
                        extent=[extent.x, extent.y, extent.z],
                        spatial=actor.get_editor_property("is_spatially_loaded"))
            nav.append(item)
            unreal.log(f"CITY_NAV_BOUNDS {item}")
    report = dict(facades=records, navigation=nav)
    (PROJECT / "Saved/QA/CityFacadeOrientation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
