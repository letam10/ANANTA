"""Read Coastal water candidates without saving the map or any asset."""

from __future__ import annotations

import json
import re
from pathlib import Path

import unreal


ROOT = Path("D:/GAME/ANANTA")
MAP = "/Game/ANANTA/Maps/ANANTA_CoastalCity"
REPORT = ROOT / "Tools/Continuation_20261020/W3_coastal_water_audit.json"
KEYWORD = re.compile(r"water|ocean|foam|shore", re.IGNORECASE)


def vector(value: object) -> list[float] | None:
    if value is None:
        return None
    return [float(value.x), float(value.y), float(value.z)]


def path_name(value: object) -> str | None:
    if value is None:
        return None
    return str(value.get_path_name())


def component_record(component: object) -> dict:
    mesh = component.get_editor_property("static_mesh")
    materials = []
    for index in range(component.get_num_materials()):
        materials.append(path_name(component.get_material(index)))
    return {
        "component": component.get_name(),
        "mesh": path_name(mesh),
        "materials": materials,
        "collisionProfile": str(component.get_collision_profile_name()),
        "collisionEnabled": str(component.get_collision_enabled()),
    }


def actor_record(actor: object) -> dict:
    origin, extent = actor.get_actor_bounds(False)
    components = [
        component_record(component)
        for component in actor.get_components_by_class(unreal.StaticMeshComponent)
    ]
    return {
        "label": actor.get_actor_label(),
        "name": actor.get_name(),
        "class": actor.get_class().get_path_name(),
        "locationCm": vector(actor.get_actor_location()),
        "boundsOriginCm": vector(origin),
        "boundsExtentCm": vector(extent),
        "components": components,
    }


def is_candidate(record: dict) -> bool:
    values = [record["label"], record["name"], record["class"]]
    for component in record["components"]:
        values.append(component["mesh"] or "")
        values.extend(component["materials"])
    return any(KEYWORD.search(value or "") for value in values)


def main() -> None:
    if not unreal.EditorLevelLibrary.load_level(MAP):
        raise RuntimeError(f"Unable to load {MAP}")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    records = [actor_record(actor) for actor in actors]
    candidates = [record for record in records if is_candidate(record)]
    materials = sorted(
        {
            material
            for record in candidates
            for component in record["components"]
            for material in component["materials"]
            if material
        }
    )
    payload = {
        "schema": "ananta.w3.coastal-water-audit.v1",
        "map": MAP,
        "readOnly": True,
        "savedMap": False,
        "totalActors": len(records),
        "candidateCount": len(candidates),
        "candidateMaterials": materials,
        "candidates": candidates,
    }
    REPORT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    unreal.log(
        "W3_COASTAL_WATER_AUDIT "
        + json.dumps(
            {
                "map": MAP,
                "totalActors": len(records),
                "candidateCount": len(candidates),
                "materials": materials,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
