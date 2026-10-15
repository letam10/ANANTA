"""Apply only civic dressing to the current map, preserving existing gameplay geometry."""

import json
from pathlib import Path
import sys
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(PROJECT / "Tools/Editor"))
from CityLayout import Layout
from CityBarSeating import generate as bar_seating
from CityCivicDressing import generate as arcade_dressing
from CityScene import ACTORS, instance_group, material_asset, mesh_asset


def old_cabinets():
    boxes = []
    for xx in (2550, 3300, 4050):
        for side in (-1, 1):
            x, y = -24000 + xx, -6000 + side * 1250
            boxes.extend((("DistrictNavy", (x, y, 110), (125, 85, 190)),
                          ("DistrictSteel", (x, y - side * 46, 110), (140, 50, 12)),
                          ("DistrictNeon", (x, y - side * 44, 164), (95, 4, 62)),
                          ("DistrictPink", (x, y - side * 45, 220), (130, 6, 30))))
            for dx in (-30, 10, 35):
                boxes.append(("DistrictYellow", (x + dx, y - side * 55, 120), (12, 12, 8)))
    return boxes


def main():
    layout = Layout()
    arcade_dressing(layout)
    bar_seating(layout)
    groups = layout.export()["groups"]
    for group in groups:
        mesh_asset(group["mesh"])
        if group["material"]:
            material_asset(group["material"])
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors
                                                      if item.native_class.get_name() != "WorldPartitionHLOD"])
    expected = old_cabinets()
    matches = []
    for actor in ACTORS.get_all_level_actors():
        for component in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            mesh = component.static_mesh
            if not mesh or mesh.get_name() not in ("Cube", "SM_CityCubeNanite"):
                continue
            material = component.get_material(0)
            if not material:
                continue
            indices = []
            for index in range(component.get_instance_count()):
                transform = component.get_instance_transform(index, world_space=True)
                position = transform.translation
                scale = transform.scale3d
                for name, location, size in expected:
                    same_position = max(abs(a - b) for a, b in zip(
                        (position.x, position.y, position.z), location)) < 0.05
                    same_scale = max(abs(a - b / 100) for a, b in zip(
                        (scale.x, scale.y, scale.z), size)) < 0.0001
                    if same_position and same_scale and material.get_name() == f"M_{name}":
                        indices.append(index)
                        break
            if indices:
                matches.append((component, indices))
    removed = sum(len(indices) for _, indices in matches)
    assert removed == 42, f"Expected 42 old cabinet pieces before changing geometry, found {removed}"
    # Chi xoa cac instance khop toa do, kich thuoc va vat lieu; giu nguyen tuong/san/va cham khac.
    for component, indices in matches:
        component.modify()
        for index in sorted(indices, reverse=True):
            assert component.remove_instance(index)
    hlod = unreal.load_asset("/Game/ANANTA/City/HLOD/City_HLOD")
    for index, group in enumerate(groups):
        actor = instance_group(group, 40000 + index)
        actor.set_actor_label(f"Living_CivicDressing_Group_{index}")
        actor.set_editor_property("hlod_layer", hlod)
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    report = dict(removedCabinetPieces=removed, writtenGroups=len(groups),
                  writtenInstances=sum(len(group["instances"]) for group in groups),
                  hlodRebuildRequired=True, collisionRuntimeVerified=False, fpsAccepted=False)
    (PROJECT / "Saved/QA/CityCivicDressingApplied.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("CITY_CIVIC_DRESSING_APPLIED " + json.dumps(report))


if __name__ == "__main__":
    main()
