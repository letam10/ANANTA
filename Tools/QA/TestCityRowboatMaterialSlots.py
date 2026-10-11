"""Exercise the actual importer binder with the persisted old slot order."""

import ast
from pathlib import Path
from types import SimpleNamespace


root = Path(__file__).resolve().parents[2]
source = ast.parse((root / "Tools/Editor/ImportCityRowboatDryFloor.py").read_text(encoding="utf-8"))
function = next(
    node for node in source.body
    if isinstance(node, ast.FunctionDef) and node.name == "bind_materials"
)
prefix = "/Game/ANANTA/City"
expected = ["City_wood_floor", "Living_Enamel", "Living_Steel"]


class Material:
    def __init__(self, path):
        self.path = path

    def get_path_name(self):
        return self.path


class Mesh:
    def __init__(self, names):
        self.static_materials = [SimpleNamespace(material_slot_name=name) for name in names]
        self.bound = {}

    def set_material(self, index, material):
        self.bound[index] = material.get_path_name()


materials = {
    f"{prefix}/Materials/M_{name}": Material(f"{prefix}/Materials/M_{name}")
    for name in expected
}
namespace = dict(ROOT=prefix, unreal=SimpleNamespace(load_asset=materials.get))
exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_importer_binder", "exec"), namespace)
bind = namespace["bind_materials"]
old_order = ["Living_Enamel", "Living_Steel", "City_wood_floor"]
assert all(old_order[index] != expected[index] for index in range(3))
for names in (expected, old_order):
    mesh = Mesh(names)
    bindings = bind(mesh, expected)
    assert len(bindings) == 3
    for index, name in enumerate(names):
        assert mesh.bound[index] == f"{prefix}/Materials/M_{name}"
for names in (["Living_Enamel", "Living_Steel"], ["Living_Enamel"] * 3, ["Unexpected"] * 3):
    try:
        bind(Mesh(names), expected)
    except AssertionError:
        pass
    else:
        raise AssertionError(f"Invalid slots accepted: {names}")
wood = materials.pop(f"{prefix}/Materials/M_City_wood_floor")
try:
    bind(Mesh(old_order), expected)
except AssertionError:
    pass
else:
    raise AssertionError("Missing wood material accepted")
materials[wood.path] = wood
print("CITY_ROWBOAT_MATERIAL_SLOT_TEST_OK cases=6 reproduced_mismatches=3")
