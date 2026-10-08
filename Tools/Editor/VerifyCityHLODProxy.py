"""Reopen one rebuilt HLOD and export its actual bound texture data for inspection."""

import json
import os
from pathlib import Path
import unreal


LABEL = os.environ.get("ANANTA_HLOD_LABEL", "City_HLOD/ANANTA_City_City_L0_X0_Y0")
PARENT = "/Game/ANANTA/City/Materials/M_City_HLOD.M_City_HLOD"
EXPECTED = {"BaseColor", "Normal", "MRS", "EmissiveColor"}


def main():
    output = Path(unreal.Paths.project_saved_dir()).resolve() / "QA/CityHLODProxy" / LABEL.split("/")[-1]
    output.mkdir(parents=True, exist_ok=True)
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level("/Game/ANANTA/Maps/ANANTA_City"):
        raise RuntimeError("Could not load city")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    matches = [item for item in descriptors if str(item.label) == LABEL]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one descriptor: {len(matches)}")
    unreal.WorldPartitionBlueprintLibrary.pin_actors([matches[0].guid])
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WorldPartitionHLOD)
    actors = [actor for actor in actors if actor.get_actor_label() == LABEL]
    if len(actors) != 1:
        raise RuntimeError(f"Expected one loaded HLOD: {len(actors)}")
    report = dict(label=LABEL, components=[], errors=[])
    for component in actors[0].get_components_by_class(unreal.StaticMeshComponent):
        mesh = component.static_mesh
        if not mesh:
            report["errors"].append("HLOD component has no mesh")
            continue
        record = dict(mesh=mesh.get_path_name(), triangles=mesh.get_num_triangles(0), materials=[])
        mesh_task = unreal.AssetExportTask()
        mesh_task.object = mesh
        mesh_task.filename = str(output / "Proxy.obj")
        mesh_task.automated = True
        mesh_task.prompt = False
        mesh_task.replace_identical = True
        if not unreal.Exporter.run_asset_export_task(mesh_task):
            report["errors"].append("Proxy geometry export failed")
        mesh_task.filename = str(output / "Proxy.fbx")
        if not unreal.Exporter.run_asset_export_task(mesh_task):
            report["errors"].append("Proxy FBX export failed")
        for slot in range(component.get_num_materials()):
            material = component.get_material(slot)
            if not isinstance(material, unreal.MaterialInstanceConstant):
                report["errors"].append(f"Expected baked material instance: {slot}")
                continue
            parent = material.get_editor_property("parent")
            entry = dict(asset=material.get_path_name(), parent=parent.get_path_name(), textures=[])
            if entry["parent"] != PARENT:
                report["errors"].append(f"Wrong HLOD material parent: {entry['parent']}")
            channels = set()
            for parameter in material.get_editor_property("texture_parameter_values"):
                texture = parameter.get_editor_property("parameter_value")
                info = parameter.get_editor_property("parameter_info")
                if not texture:
                    continue
                name = texture.get_name()
                channel = next((value for value in EXPECTED if name.endswith("_" + value)), None)
                if channel:
                    channels.add(channel)
                target = output / f"{name}.png"
                task = unreal.AssetExportTask()
                task.object = texture
                task.filename = str(target)
                task.automated = True
                task.prompt = False
                task.replace_identical = True
                if not unreal.Exporter.run_asset_export_task(task):
                    report["errors"].append(f"Texture export failed: {name}")
                entry["textures"].append(dict(
                    parameter=str(info.get_editor_property("name")), asset=texture.get_path_name(),
                    size=[texture.blueprint_get_size_x(), texture.blueprint_get_size_y()],
                    virtual=texture.get_editor_property("virtual_texture_streaming"), export=str(target)))
            if channels != EXPECTED:
                report["errors"].append(f"Missing baked channels: {EXPECTED - channels}")
            record["materials"].append(entry)
        if not record["materials"]:
            report["errors"].append("Mesh has no usable material")
        report["components"].append(record)
    if not report["components"]:
        report["errors"].append("No mesh component")
    # Chi doc goi da luu; anh xuat dung de kiem du lieu pixel doc lap.
    (output / "Readback.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if report["errors"]:
        raise RuntimeError("\n".join(report["errors"]))
    unreal.log("CITY_HLOD_PROXY_READBACK_OK channels=4")


if __name__ == "__main__":
    main()
