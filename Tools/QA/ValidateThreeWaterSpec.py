"""Validate the shared Three.js water spec and its Unreal port contract."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "Prototypes" / "ThreeWater" / "public" / "wave-spec.json"
CONTRACT_PATH = ROOT / "Prototypes" / "ThreeWater" / "public" / "unreal-water-contract.json"
EXPECTED_WAVES = [
    {"direction": [1, 0.25], "wavelength": 28, "amplitude": 0.2, "speed": 1.6, "phase": 0},
    {"direction": [-0.7, 1], "wavelength": 45, "amplitude": 0.12, "speed": 1.1, "phase": 1.4},
    {"direction": [0.35, 0.94], "wavelength": 72, "amplitude": 0.06, "speed": 0.75, "phase": 2.2},
    {"direction": [-1, -0.2], "wavelength": 120, "amplitude": 0.03, "speed": 0.45, "phase": 3.1},
]
EXPECTED_BOUNDARY = {
    "type": "box",
    "minX": -700,
    "maxX": 700,
    "minZ": -400,
    "maxZ": 400,
    "cameraMargin": 14,
    "boatMargin": 8,
}
EXPECTED_SCENES = ["coast", "beach_boat", "offshore"]
EXPECTED_HASH = "f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        fail(f"missing file: {path}")
        raise error
    if not isinstance(value, dict):
        fail(f"root is not an object: {path}")
    return value


def canonical_hash(spec: dict[str, Any]) -> str:
    canonical = json.loads(json.dumps(spec))
    canonical.setdefault("hash", {})["value"] = "PENDING_HASH"
    payload = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, got {actual!r}")


def validate_spec(spec: dict[str, Any]) -> str:
    require_equal(spec.get("schema"), "ananta.three-water.wave-spec.v2", "schema")
    require_equal(spec.get("schemaVersion"), "2.0.0", "schemaVersion")
    require_equal(spec.get("hash", {}).get("algorithm"), "sha256", "hash.algorithm")
    require_equal(
        spec.get("hash", {}).get("canonicalization"),
        "sorted UTF-8 JSON with hash.value=PENDING_HASH",
        "hash.canonicalization",
    )
    actual_hash = canonical_hash(spec)
    require_equal(spec.get("hash", {}).get("value"), actual_hash, "hash.value")
    require_equal(actual_hash, EXPECTED_HASH, "hash.value fixture")
    require_equal(
        spec.get("units"),
        {
            "distance": "meters",
            "time": "seconds",
            "amplitude": "meters",
            "speed": "meters_per_second",
            "phase": "radians",
        },
        "units",
    )
    require_equal(
        spec.get("axes", {}).get("mapping"),
        "UE.X=Three.X, UE.Y=Three.Z, UE.Z=Three.Y",
        "axes.mapping",
    )
    require_equal(spec.get("presetQuality", {}).get("name"), "low", "presetQuality.name")
    require_equal(spec.get("presetQuality", {}).get("maxWaves"), 4, "presetQuality.maxWaves")
    require_equal(spec.get("presetQuality", {}).get("cpuMeshRebuild"), False, "presetQuality.cpuMeshRebuild")
    require_equal(spec.get("presetQuality", {}).get("renderPath"), "single_fixed_mesh_shader", "presetQuality.renderPath")
    require_equal(spec.get("waves"), EXPECTED_WAVES, "waves")
    require_equal(spec.get("foam", {}).get("width"), 6, "foam.width")
    require_equal(spec.get("foam", {}).get("shorelineDepth"), 16, "foam.shorelineDepth")
    for key, value in EXPECTED_BOUNDARY.items():
        require_equal(spec.get("boundary", {}).get(key), value, f"boundary.{key}")
    require_equal(spec.get("boundary", {}).get("polygon"), [[-700, -400], [700, -400], [700, 400], [-700, 400]], "boundary.polygon")
    scenes = spec.get("scenes")
    require_equal([scene.get("id") for scene in scenes], EXPECTED_SCENES, "scenes.ids")
    require_equal([scene.get("durationSeconds") for scene in scenes], [10, 10, 10], "scenes.durationSeconds")
    require_equal(spec.get("unrealPortGate", {}).get("fpsClaim"), False, "unrealPortGate.fpsClaim")
    return actual_hash


def validate_contract(contract: dict[str, Any], source_hash: str) -> None:
    require_equal(contract.get("schemaVersion"), "ananta.three-water.unreal-water-contract.v2", "contract.schemaVersion")
    source = contract.get("sourceWaveSpec", {})
    require_equal(source.get("schema"), "ananta.three-water.wave-spec.v2", "contract.sourceWaveSpec.schema")
    require_equal(source.get("sha256"), source_hash, "contract.sourceWaveSpec.sha256")
    require_equal(source.get("canonicalization"), "sorted UTF-8 JSON with hash.value=PENDING_HASH", "contract.sourceWaveSpec.canonicalization")
    require_equal(contract.get("axes"), {"Three.X": "UE.X", "Three.Z": "UE.Y", "Three.Y": "UE.Z"}, "contract.axes")
    field = contract.get("waveField", {})
    require_equal(field.get("preset"), "low", "contract.waveField.preset")
    require_equal(field.get("waveCount"), 4, "contract.waveField.waveCount")
    require_equal(field.get("parameters"), ["direction", "wavelength", "amplitude", "speed", "phase"], "contract.waveField.parameters")
    require_equal(field.get("waves"), EXPECTED_WAVES, "contract.waveField.waves")
    material = contract.get("materialFunction", {})
    require_equal(material.get("name"), "MF_AnantaWater", "contract.materialFunction.name")
    require_equal(material.get("outputs"), ["BaseColor", "Normal", "Roughness", "Emissive"], "contract.materialFunction.outputs")
    require_equal(material.get("readbackRequired"), True, "contract.materialFunction.readbackRequired")
    require_equal(contract.get("surface", {}).get("blendMode"), "opaque", "contract.surface.blendMode")
    require_equal(contract.get("surface", {}).get("foamWidth"), 6, "contract.surface.foamWidth")
    require_equal(contract.get("surface", {}).get("shorelineDepth"), 16, "contract.surface.shorelineDepth")
    boundary = contract.get("boundaryCollision", {})
    require_equal(boundary.get("shaderIndependent"), True, "contract.boundaryCollision.shaderIndependent")
    require_equal(boundary.get("boundsMeters"), {"minX": -700, "maxX": 700, "minZ": -400, "maxZ": 400}, "contract.boundaryCollision.boundsMeters")
    require_equal(contract.get("cameraComparisonLabels"), EXPECTED_SCENES, "contract.cameraComparisonLabels")
    require_equal(contract.get("acceptance", {}).get("fpsClaim"), False, "contract.acceptance.fpsClaim")
    require_equal(contract.get("acceptance", {}).get("requiresF1ForFrameRate"), True, "contract.acceptance.requiresF1ForFrameRate")


def main() -> int:
    try:
        spec = load_json(SPEC_PATH)
        contract = load_json(CONTRACT_PATH)
        source_hash = validate_spec(spec)
        validate_contract(contract, source_hash)
    except (AssertionError, json.JSONDecodeError) as error:
        print(f"THREE_WATER_SPEC_FAIL {error}", file=sys.stderr)
        return 1
    print(f"THREE_WATER_SPEC_OK sha256={source_hash} waves=4 scenes=3 duration=10s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
