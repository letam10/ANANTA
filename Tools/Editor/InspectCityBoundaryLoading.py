"""Compare persisted boundary streaming bounds with direct actor loading; never save the map."""

import json
from pathlib import Path
import unreal


def main():
    root = Path(unreal.Paths.project_dir()).resolve()
    expected = json.loads((root / "Saved/QA/CityExpansionApplied.json").read_text(encoding="utf-8"))
    edge = expected["layout"]["widthMetres"] * 50
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    library = unreal.WorldPartitionBlueprintLibrary
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    descriptors = library.get_actor_descs()
    prefixes = ("City_28_56_Cube_", "City_28_-1_Cube_", "City_56_28_Cube_", "City_-1_28_Cube_")
    candidates = [item for item in descriptors if str(item.label).startswith(prefixes)]
    assert candidates, "No persisted boundary-cell descriptors"
    points = [(edge, 0), (-edge, 0), (0, edge), (0, -edge), (edge, -130000), (130000, -edge)]
    points += [(x * edge, y * edge) for x in (-1, 1) for y in (-1, 1)]
    selected = {}
    for x, y in points:
        box = unreal.Box(min=unreal.Vector(x - 500, y - 500, -500),
                         max=unreal.Vector(x + 500, y + 500, 2500))
        for item in library.get_intersecting_actor_descs(box):
            if item.native_class.get_name() != "WorldPartitionHLOD":
                selected[unreal.GuidLibrary.conv_guid_to_string(item.guid)] = item.guid
    library.load_actors(list(selected.values()))
    before = unreal.CityEditorTools.audit_world_boundaries(world, edge)
    library.load_actors([item.guid for item in candidates])
    rows = []
    wanted = {str(item.label) for item in candidates}
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        if actor.get_actor_label() not in wanted:
            continue
        origin, extent = actor.get_actor_bounds(False)
        row = dict(label=actor.get_actor_label(), spatial=actor.get_editor_property("is_spatially_loaded"),
                   boundsOrigin=str(origin), boundsExtent=str(extent),
                   descriptorSelected=any(str(item.label) == actor.get_actor_label() and
                                          unreal.GuidLibrary.conv_guid_to_string(item.guid) in selected
                                          for item in candidates), components=[])
        for component in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            transforms = [component.get_instance_transform(index, world_space=True)
                          for index in range(component.get_instance_count())]
            boundaries = [transform for transform in transforms if abs(transform.scale3d.z - 400) < .01]
            if component.is_visible() or not boundaries:
                continue
            row["components"].append(dict(visible=component.is_visible(),
                                          collision=str(component.get_collision_enabled()),
                                          pawn=str(component.get_collision_response_to_channel(
                                              unreal.CollisionChannel.ECC_PAWN)),
                                          profile=str(component.get_collision_profile_name()),
                                          count=component.get_instance_count(),
                                          transforms=[str(transform) for transform in boundaries],
                                          preparation=unreal.CityEditorTools.finalize_instance_collision(component)))
        if row["components"]:
            rows.append(row)
    after = unreal.CityEditorTools.audit_world_boundaries(world, edge)
    result = dict(before=before, after=after, selectedDescriptors=len(selected), boundaries=rows)
    path = root / "Saved/QA/CityBoundaryLoadingDiagnostic.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    unreal.log(f"CITY_BOUNDARY_LOADING_DIAGNOSTIC {result}")
    assert len(rows) == 4, rows
    library.unload_actors(list(selected.values()) + [item.guid for item in candidates])


if __name__ == "__main__":
    main()
