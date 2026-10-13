"""Generate the owned upgrade kit; never modify the original Nova assets."""

import json
import sys
from datetime import datetime
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import fleet
import interior_models
import street_models


def main():
    output = ROOT / "Assets" / "CoastalUpgrade"
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    material = bpy.data.materials.new("CoastalSurface")
    material.use_nodes = True
    attribute = material.node_tree.nodes.new("ShaderNodeVertexColor")
    attribute.layer_name = "Color"
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value = 0.12
    material.node_tree.links.new(attribute.outputs["Color"], shader.inputs["Base Color"])
    material.node_tree.links.new(attribute.outputs["Alpha"], shader.inputs["Roughness"])
    objects = fleet.build() + interior_models.furniture() + street_models.build()
    objects.append(street_models.opera_roof())
    report = {"generated_at": datetime.now().isoformat(), "units": "metres", "models": []}
    for obj in objects:
        lowest = min(vertex.co.z for vertex in obj.data.vertices)
        for vertex in obj.data.vertices:
            vertex.co.z -= lowest
        obj.data.update()
        obj.data.calc_loop_triangles()
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.01)
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.update()
        bpy.ops.export_scene.fbx(
            filepath=str(output / f"{obj.name}.fbx"), use_selection=True,
            object_types={"MESH"}, add_leaf_bones=False, bake_anim=False,
            axis_forward="-Y", axis_up="Z", use_mesh_modifiers=True,
            colors_type="LINEAR", use_custom_props=False,
            mesh_smooth_type="FACE",
        )
        dimensions = [round(value, 4) for value in obj.dimensions]
        assert all(value > 0 for value in dimensions), (obj.name, dimensions)
        triangles = len(obj.data.loop_triangles)
        assert triangles < 20000, (obj.name, triangles)
        report["models"].append({
            "name": obj.name, "dimensions_m": dimensions,
            "triangles": triangles, "material_sections": 1,
            "pivot": "ground center", "forward": "+X",
        })
    (output / "manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "CoastalModels.blend"))
    print(f"COASTAL_MODELS_OK {len(objects)} models; max triangles="
          f"{max(item['triangles'] for item in report['models'])}")


if __name__ == "__main__":
    main()
