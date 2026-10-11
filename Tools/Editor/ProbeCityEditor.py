"""Exercise required editor APIs in memory without saving the baseline map."""

import json
from pathlib import Path
import sys
import unreal


project = Path(unreal.Paths.project_dir()).resolve()
sys.path.insert(0, str(project / "Tools/Editor"))
from CityScene import instance_group, lighting, navigation, camera, text

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level("/Game/ANANTA/Maps/ANANTA_Slice")
group = {"cell": [0, 0], "mesh": "Cube", "material": None, "collision": True,
         "instances": [{"location": [-50000, -50000, 0], "scale": [1, 1, 1], "yaw": 0}]}
actor = instance_group(group, 999999)
component = actor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
assert component.get_instance_count() == 1
lighting()
volume = navigation()
camera("City_ProbeCamera", (0, 0, 100), (0, 0, 0))
text("City_ProbeText", "NOVA", (0, 0, 100))
report = {"instancing": True, "lighting": True, "navigationBounds": str(volume.get_actor_bounds(False)),
          "runtimeClasses": [getattr(unreal, name).static_class().get_name() for name in (
              "ANANTACityGameMode", "ANANTACityVehicle", "ANANTACityInteractable",
              "ANANTACityEnemy", "ANANTACityCrowd")]}
(project / "Saved/QA/CityEditorProbe.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
unreal.log(f"CITY_EDITOR_PROBE_OK {report}")
