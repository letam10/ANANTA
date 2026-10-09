"""Read existing furniture bounds for collision-safe civic placement."""

import json
from pathlib import Path
import unreal


NAMES = ("CafeCounter", "CafeTable", "House_dining_chair_02", "House_sofa_02",
         "House_mid_century_lounge_chair", "House_hanging_industrial_lamp", "ArcadeCabinet",
         "KitchenFridge", "CeilingFan", "WasteBin", "InteriorServiceDesk", "DetailedPlanter")


def main():
    entries = {}
    for name in NAMES:
        path = f"/Game/ANANTA/City/Meshes/SM_{name}"
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            entries[name] = dict(available=False)
            continue
        mesh = unreal.load_asset(path)
        bounds = mesh.get_bounding_box()
        entries[name] = dict(available=True, asset=path, triangles=mesh.get_num_triangles(0),
                             minimum=[bounds.min.x, bounds.min.y, bounds.min.z],
                             maximum=[bounds.max.x, bounds.max.y, bounds.max.z])
    output = Path(unreal.Paths.project_saved_dir()).resolve() / "QA/CityCivicMeshBounds.json"
    output.write_text(json.dumps(dict(units="cm", mapLoaded=False, meshes=entries), indent=2), encoding="utf-8")
    unreal.log("CITY_CIVIC_MESH_BOUNDS_OK " + json.dumps(entries))


if __name__ == "__main__":
    main()
