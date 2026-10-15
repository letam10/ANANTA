"""Read persisted Unreal material slot names without changing the mesh or map."""

import json
from pathlib import Path
import unreal


project = Path(unreal.Paths.project_dir()).resolve()
mesh = unreal.load_asset("/Game/ANANTA/City/Meshes/SM_Rowboat")
assert mesh
slots = []
for index, slot in enumerate(mesh.static_materials):
    slots.append(dict(
        index=index,
        name=str(slot.material_slot_name),
        material=slot.material_interface.get_path_name() if slot.material_interface else None,
    ))
report = dict(asset=mesh.get_path_name(), naniteTriangles=mesh.get_num_nanite_triangles(), slots=slots)
path = project / "Saved/QA/CityMetroAssets/rowboat_material_slots.json"
path.write_text(json.dumps(report, indent=2), encoding="utf-8")
unreal.log("CITY_ROWBOAT_MATERIAL_SLOTS " + json.dumps(report))
