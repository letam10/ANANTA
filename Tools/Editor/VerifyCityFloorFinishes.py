"""Independent saved-map and PBR channel readback for the four upgraded floors."""

import json
from pathlib import Path
import unreal


def main():
    project = Path(unreal.Paths.project_dir()).resolve()
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ANANTA/Maps/ANANTA_City")
    descriptors = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()
    unreal.WorldPartitionBlueprintLibrary.load_actors([d.guid for d in descriptors
                                                      if d.native_class.get_name() != "WorldPartitionHLOD"])
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    expected = {"Clinic": "InteriorTerrazzo", "Market": "InteriorTerrazzo",
                "Transit": "InteriorTerrazzo", "Workshop": "InteriorWorkshopConcrete"}
    errors = []
    for venue, name in expected.items():
        matches = [a for a in actors if a.get_actor_label() == f"Expansion_{venue}_Floor"]
        if len(matches) != 1:
            errors.append(f"Expected one floor for {venue}, got {len(matches)}")
            continue
        material = matches[0].static_mesh_component.get_material(0)
        if not material or material.get_name() != f"M_{name}":
            errors.append(f"Incorrect saved floor material: {venue}")
    root = "/Game/ANANTA/City"
    roles = {"baseColor": unreal.MaterialProperty.MP_BASE_COLOR,
             "normal": unreal.MaterialProperty.MP_NORMAL,
             "roughness": unreal.MaterialProperty.MP_ROUGHNESS,
             "ao": unreal.MaterialProperty.MP_AMBIENT_OCCLUSION}
    for name in set(expected.values()):
        material = unreal.load_asset(f"{root}/Materials/M_{name}")
        for role, prop in roles.items():
            texture = unreal.load_asset(f"{root}/Textures/{name}_{role}")
            if not texture or texture.get_editor_property("srgb") != (role == "baseColor"):
                errors.append(f"Missing texture or incorrect colour space: {name}.{role}")
            elif role == "normal" and not texture.get_editor_property("flip_green_channel"):
                errors.append(f"OpenGL normal not converted: {name}")
            if not material or not unreal.MaterialEditingLibrary.get_material_property_input_node(material, prop):
                errors.append(f"Disconnected PBR channel: {name}.{role}")
    report = dict(floors=len(expected), materials=len(set(expected.values())), errors=errors)
    path = project / "Saved/QA/CityFloorFinishesReadback.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert not errors, errors
    unreal.log("CITY_FLOOR_FINISHES_READBACK_OK")


if __name__ == "__main__":
    main()
