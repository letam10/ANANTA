"""Reconcile actual native readback/capture files with the frozen source contract."""

import datetime
import hashlib
import json
import math
from pathlib import Path

from PIL import Image

from water_contract import load_spec, normal_hlsl, foam_hlsl

TASK = Path(__file__).resolve().parent
ROOT = TASK.parent.parent
spec = load_spec(ROOT)
native = json.loads((TASK / "W3_native_readback.json").read_text())
review = json.loads((TASK / "W3_review.json").read_text())
ownership = json.loads((TASK / "ownership.json").read_text(encoding="utf-8-sig"))
checks = []


def check(name, passed):
    checks.append({"name": name, "passed": bool(passed)})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


check("native_authoring_readback", native["authoring_readback_passed"] and not native["errors"])
check("exact_wave_tuples", native["material"]["waves"] == spec["waves"])
check("exact_13_nodes", native["material"]["function_expression_count"] == 13)
check("opaque_world_normal", native["material"]["opaque"] and native["material"]["world_space_normal"])
for key, code in [("normal", normal_hlsl(spec)), ("foam", foam_hlsl(spec))]:
    check(key + "_native_code_hash", native["material"][key + "_code_sha256"] == hashlib.sha256(code.encode()).hexdigest())
for output in ("BaseColor", "Normal", "Roughness", "Emissive"):
    check("output_" + output, native["material"]["connections"][output]["output"] == output)

expected_edges = {"West": [-70000, 0, 200], "East": [70000, 0, 200],
                  "South": [0, -40000, 200], "North": [0, 40000, 200]}
check("four_boundary_rays", len(native["boundary_traces"]) == 4)
for row in native["boundary_traces"]:
    edge = row["edge"]
    check("ray_" + edge, row["blocked"] and row["actor"] == "W3_Boundary_" + edge
          and all(abs(a - b) < 0.1 for a, b in zip(row["impact_cm"], expected_edges[edge])))

captures = {row["id"]: row for row in review["captures"]}
check("three_distinct_captures", set(captures) == {row["id"] for row in spec["scenes"]})
for scene in spec["scenes"]:
    name = scene["id"]
    capture = captures[name]["captureMetadata"]
    position = [scene["camera"][i] * 100 for i in (0, 2, 1)]
    actual = capture["location"]
    check(name + "_position", all(abs(actual[k] - value) < 0.1 for k, value in zip(("x", "y", "z"), position)))
    delta = [scene["target"][i] - scene["camera"][i] for i in (0, 2, 1)]
    length = math.sqrt(sum(v * v for v in delta))
    check(name + "_forward", all(abs(capture["forward"][k] - value / length) < 1e-6
                                for k, value in zip(("x", "y", "z"), delta)))
    vertical = math.degrees(2 * math.atan(math.tan(math.radians(capture["fovDegrees"] / 2)) / (1422 / 800)))
    check(name + "_vertical_fov48", abs(vertical - 48) < 1e-4)
    for engine, extension in [("Three", "jpg"), ("UE", "png")]:
        image = TASK / f"W3_{engine}_{name}.{extension}"
        with Image.open(image) as opened:
            check(name + "_" + engine + "_image", opened.size == (1422, 800))

check("source_config_185_unchanged", len(ownership["sourceConfigHashes"]) == 185 and all(
    sha(Path(row["Path"])).upper() == row["Hash"] for row in ownership["sourceConfigHashes"]))
check("protected_agents_unchanged", sha(ROOT / "AGENTS.md").upper() ==
      "0E2D1FB4139C9FDE444FE7C027C628E619CE4AC2DE66AA14CDB7F0197A1AA591")
check("no_fps_claim", review["fpsClaim"] is False and native["fpsClaim"] is False)

report = {
    "schema": "ananta.w3.gates.v1",
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "passed": all(row["passed"] for row in checks),
    "checks": checks,
    "package_hashes": {str(path.relative_to(ROOT)): sha(path)
                       for path in (ROOT / "Content/ANANTA/WaterW3_20261020").glob("*.*")},
    "scope": "isolated W3 contract only; no hero/runtime/FPS acceptance",
}
(TASK / "W3_gates.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("W3_GATE_CHECKS", report["passed"], len(checks), [row["name"] for row in checks if not row["passed"]])
raise SystemExit(0 if report["passed"] else 1)
