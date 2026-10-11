"""Read saved instanced HLODs, checking geometry and source material references."""

import json
import os
from pathlib import Path
import sys
import time
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityHLODIdentity import MAP, check_actor_sets, read_json, validate_receipt

LABEL = os.environ.get("ANANTA_HLOD_LABEL", "")
RUN_STARTED = time.time()


def guid_text(guid):
    return unreal.GuidLibrary.conv_guid_to_string(guid)


def boundary_sources(descriptors):
    """Locate the four actual hidden edge colliders before comparing HLOD source metadata."""
    applied = read_json(PROJECT / "Saved/QA/CityExpansionApplied.json")
    cells = int(applied["layout"]["roadBlocks"] ** 0.5)
    middle = cells // 2
    prefixes = tuple(f"City_{x}_{y}_Cube_" for x, y in
                     ((middle, cells), (middle, -1), (cells, middle), (-1, middle)))
    candidates = [item for item in descriptors if str(item.label).startswith(prefixes)]
    assert candidates, "No boundary source descriptors"
    library = unreal.WorldPartitionBlueprintLibrary
    library.load_actors([item.guid for item in candidates])
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    wanted = {str(item.label) for item in candidates}
    sources = []
    boundary_instances = 0
    edge = applied["layout"]["widthMetres"] * 50
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor):
        if actor.get_actor_label() not in wanted:
            continue
        count = 0
        for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if component.is_visible() or not component.static_mesh:
                continue
            if component.static_mesh.get_path_name() != "/Engine/BasicShapes/Cube.Cube":
                continue
            for index in range(component.get_instance_count()):
                transform = component.get_instance_transform(index, world_space=True)
                scale = transform.scale3d
                position = transform.translation
                x_edge = abs(scale.x - 1) < .01 and abs(abs(position.x) - 50 - edge) < 1
                y_edge = abs(scale.y - 1) < .01 and abs(abs(position.y) - 50 - edge) < 1
                if abs(scale.z - 400) < .01 and (x_edge or y_edge):
                    count += 1
        if count:
            assert not actor.get_editor_property("enable_auto_lod_generation"), "Boundary source enables HLOD"
            sources.append(dict(label=actor.get_actor_label(), path=actor.get_path_name(),
                                guid=guid_text(actor.get_editor_property("actor_guid"))))
            boundary_instances += count
    assert len(sources) == 4 and boundary_instances == 4, "Cannot identify all four boundary source actors"
    return sources


def check_boundary_exclusion(actors, sources):
    result = dict(status="UNVERIFIED", sourceActors=sources, checkedHLODs=0, sourceReferences=0,
                  violations=[], limitations=[])
    paths = {source["path"] for source in sources}
    guids = {source["guid"].replace("-", "").lower() for source in sources}
    for actor in actors:
        try:
            # Day la metadata source that; khong suy ra tu ten proxy hay mesh Cube.
            metadata = json.loads(unreal.CityEditorTools.hlod_source_actor_references(actor))
            mappings = metadata.get("references", [])
            if metadata.get("available") is not True or not mappings:
                raise RuntimeError(metadata.get("reason", "No native source actor mappings"))
            for mapping in mappings:
                path = mapping["path"]
                guid = mapping["guid"].replace("-", "").lower()
                if not path or path == "None":
                    raise RuntimeError("Source actor mapping has no object path")
                if len(guid) != 32 or guid == "0" * 32 or not all(value in "0123456789abcdef" for value in guid):
                    raise RuntimeError("Source actor mapping has no valid GUID")
                result["sourceReferences"] += 1
                if path in paths or guid in guids:
                    result["violations"].append(dict(hlod=actor.get_actor_label(), path=path, guid=guid))
            result["checkedHLODs"] += 1
        except Exception as error:
            result["limitations"].append(f"{actor.get_actor_label()}: {error}")
    if result["violations"]:
        result["status"] = "FAIL"
    elif not result["limitations"] and result["checkedHLODs"] == len(actors):
        result["status"] = "PASS"
    return result


def main():
    identity, receipt = validate_receipt(PROJECT)
    layer = unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD")
    assert layer.get_editor_property("layer_type") == unreal.HLODLayerType.INSTANCING
    builder = layer.get_editor_property("hlod_builder_settings")
    assert not builder.get_editor_property("disallow_nanite")
    assert builder.get_editor_property("instance_filtering_type") == unreal.InstanceFilteringType.FILTER_NONE
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(MAP)
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    selected = [item for item in descriptors if item.native_class.get_name() == "WorldPartitionHLOD"
                and (not LABEL or str(item.label) == LABEL)]
    assert selected, "No matching HLOD descriptor"
    unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in selected])
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WorldPartitionHLOD)
    actors = [actor for actor in actors if not LABEL or actor.get_actor_label() == LABEL]
    errors = []
    entries = []
    try:
        check_actor_sets(receipt, [(str(item.label), guid_text(item.guid)) for item in selected],
                         [(actor.get_actor_label(), guid_text(actor.get_editor_property("actor_guid")))
                          for actor in actors], LABEL)
    except AssertionError as error:
        errors.append(str(error))
    try:
        exclusion = check_boundary_exclusion(actors, boundary_sources(descriptors))
    except Exception as error:
        exclusion = dict(status="UNVERIFIED", limitations=[str(error)])
    if exclusion["status"] != "PASS":
        errors.append(f"Boundary source exclusion: {exclusion['status']}; see boundarySourceExclusion")
    for actor in actors:
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
        rendered = [component for component in components if component.static_mesh]
        record = dict(label=actor.get_actor_label(), guid=guid_text(actor.get_editor_property("actor_guid")),
                      components=[], instances=0)
        if not rendered:
            errors.append(f"No geometry: {record['label']}")
        for component in rendered:
            if not isinstance(component, unreal.InstancedStaticMeshComponent):
                errors.append(f"Non-instanced proxy: {record['label']}")
                continue
            count = component.get_instance_count()
            if count < 1:
                errors.append(f"Empty instance group: {record['label']}")
            materials = [component.get_material(slot) for slot in range(component.get_num_materials())]
            if not materials or any(material is None for material in materials):
                errors.append(f"Missing source material: {record['label']}")
            record["instances"] += count
            record["components"].append(dict(mesh=component.static_mesh.get_path_name(), instances=count,
                                             materials=[material.get_path_name() if material else None
                                                        for material in materials]))
        entries.append(record)
    report = dict(map=MAP, selectedLabel=LABEL or None, descriptors=len(selected), actors=len(actors),
                  instances=sum(entry["instances"] for entry in entries), entries=entries, errors=errors,
                  naniteAllowed=True, instanceFiltering=False, fpsAccepted=False)
    report.update(status="FAIL" if errors else ("SAMPLE" if LABEL else "PASS"),
                  scope="sample" if LABEL else "full", fullMapAccepted=not errors and not LABEL,
                  sourceIdentity=identity, buildRunId=receipt["runId"], buildLogSha256=receipt["logSha256"],
                  builtActorCount=receipt["builtActorCount"], boundarySourceExclusion=exclusion,
                  renderedArtAccepted=False)
    name = "CityHLODInstancesSample.json" if LABEL else "CityHLODInstances.json"
    output = Path(unreal.Paths.project_saved_dir()).resolve() / "QA" / name
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert not errors, "\n".join(errors)
    unreal.log(f"CITY_HLOD_INSTANCES_OK actors={len(actors)} instances={report['instances']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Loi truoc buoc doc actor cung phai thay the bao cao cu, tranh tai dung PASS.
        name = "CityHLODInstancesSample.json" if LABEL else "CityHLODInstances.json"
        output = PROJECT / "Saved/QA" / name
        if not output.exists() or output.stat().st_mtime < RUN_STARTED:
            failure = dict(map=MAP, status="FAIL", selectedLabel=LABEL or None, descriptors=0, actors=0,
                           instances=0, entries=[], fullMapAccepted=False, errors=[str(error)],
                           naniteAllowed=None, instanceFiltering=None, fpsAccepted=False)
            output.write_text(json.dumps(failure, indent=2), encoding="utf-8")
        raise
