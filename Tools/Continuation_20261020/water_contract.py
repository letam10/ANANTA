"""Pure wave-spec validation and Unreal shader/camera recipe generation."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path


SPEC_SCHEMA = "ananta.three-water.wave-spec.v2"
SPEC_SHA256 = "f1023df3c0ca24d3f5afb8a18bb25d85b01c9cc32b3973c9c5923384f718621f"
CANONICALIZATION = "sorted UTF-8 JSON with hash.value=PENDING_HASH"


def load_spec(root: Path) -> dict:
    """Read the pinned source contract without modifying it or creating files."""
    path = root / "Prototypes" / "ThreeWater" / "public" / "wave-spec.json"
    spec = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("wave-spec root must be an object")
    if spec.get("schema") != SPEC_SCHEMA or spec.get("schemaVersion") != "2.0.0":
        raise ValueError("wave-spec schema or schemaVersion does not match v2")
    metadata = spec.get("hash")
    if not isinstance(metadata, dict):
        raise ValueError("wave-spec hash must be an object")
    if metadata.get("algorithm") != "sha256":
        raise ValueError("wave-spec hash.algorithm must be sha256")
    if metadata.get("canonicalization") != CANONICALIZATION:
        raise ValueError("wave-spec canonicalization does not match the contract")

    # Chỉ sửa bản sao để hash và dữ liệu nguồn luôn giữ nguyên.
    canonical = copy.deepcopy(spec)
    canonical["hash"]["value"] = "PENDING_HASH"
    payload = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    actual_hash = hashlib.sha256(payload).hexdigest()
    if metadata.get("value") != actual_hash:
        raise ValueError(f"wave-spec canonical SHA256 mismatch: {actual_hash}")
    if actual_hash != SPEC_SHA256:
        raise ValueError(f"wave-spec differs from the pinned source: {actual_hash}")
    return spec


def _hlsl_number(value: int | float) -> str:
    """Keep source decimal values and reject invalid shader literals."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"expected a finite numeric shader value, got {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"expected a finite numeric shader value, got {value!r}")
    literal = str(value)
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def normal_hlsl(spec: dict) -> str:
    """Return a Custom float3 body: P is world cm; T is elapsed seconds.

    The result is an Unreal world-space normal. Its consuming material must
    disable tangent-space normals, or explicitly transform this output.
    """
    waves = spec["waves"]
    if len(waves) != 4:
        raise ValueError("the low water contract requires exactly four waves")
    lines = [
        "// Three XZ mét -> Unreal XY centimet; P là world position.",
        "float2 horizontalMeters = P.xy / 100.0;",
        "float tau = 6.283185307179586;",
        "float2 heightDerivative = float2(0.0, 0.0);",
    ]
    for index, wave in enumerate(waves):
        direction_x, direction_z = wave["direction"]
        if math.hypot(direction_x, direction_z) == 0:
            raise ValueError(f"wave {index} direction must be nonzero")
        if wave["wavelength"] <= 0:
            raise ValueError(f"wave {index} wavelength must be positive")
        direction = f"direction{index}"
        wavelength = _hlsl_number(wave["wavelength"])
        amplitude = _hlsl_number(wave["amplitude"])
        speed = _hlsl_number(wave["speed"])
        phase_offset = _hlsl_number(wave["phase"])
        phase = f"phase{index}"
        lines.extend([
            f"float2 {direction} = normalize(float2({_hlsl_number(direction_x)}, {_hlsl_number(direction_z)}));",
            f"float {phase} = tau * (dot({direction}, horizontalMeters) / {wavelength} - {speed} * T / {wavelength}) + {phase_offset};",
            f"heightDerivative += {amplitude} * tau / {wavelength} * cos({phase}) * {direction};",
        ])
    lines.extend([
        "// Đạo hàm cùng trường height; tỉ số mét/mét không đổi khi sang cm.",
        "// Normal Three (-dX, 1, -dZ) -> Unreal (-dX, -dZ, 1).",
        "return normalize(float3(-heightDerivative.x, -heightDerivative.y, 1.0));",
    ])
    return "\n".join(lines) + "\n"


def foam_hlsl(spec: dict) -> str:
    """Return a Custom float1 foam body matching ShoreFoam; inputs P and T.

    This is a visual mask only. Collision remains an independent actor recipe.
    """
    boundary = spec["boundary"]
    if boundary["type"] != "box":
        raise ValueError("the foam contract requires a box boundary")
    min_x = _hlsl_number(boundary["minX"])
    max_x = _hlsl_number(boundary["maxX"])
    min_z = _hlsl_number(boundary["minZ"])
    max_z = _hlsl_number(boundary["maxZ"])
    width = _hlsl_number(spec["foam"]["width"])
    depth = _hlsl_number(spec["foam"]["shorelineDepth"])
    return "\n".join([
        "// Box Three XZ mét -> Unreal XY; dùng cùng khoảng cách tới bờ.",
        "float2 horizontalMeters = P.xy / 100.0;",
        f"float distanceX = min(horizontalMeters.x - ({min_x}), ({max_x}) - horizontalMeters.x);",
        f"float distanceZ = min(horizontalMeters.y - ({min_z}), ({max_z}) - horizontalMeters.y);",
        "float edgeDistance = max(min(distanceX, distanceZ), 0.0);",
        f"float foamRange = max({width}, 0.001);",
        f"float depthRange = max({depth}, 0.001);",
        "float shorelineMask = 1.0 - smoothstep(0.0, depthRange, edgeDistance);",
        "float foamMask = 1.0 - smoothstep(0.0, foamRange, edgeDistance);",
        "float waveA = 0.5 + 0.5 * sin((horizontalMeters.x + horizontalMeters.y) / foamRange + T * 1.35);",
        "float waveB = 0.5 + 0.5 * sin((horizontalMeters.x - horizontalMeters.y) / foamRange * 1.7 - T * 1.05);",
        "float foam = foamMask * (0.48 + waveA * 0.28);",
        "foam += foamMask * shorelineMask * (0.18 + waveB * 0.18);",
        "return clamp(foam * 0.92, 0.0, 0.86);",
    ]) + "\n"


def camera_pose(scene: dict, aspect_ratio: float = 16 / 9) -> dict:
    """Convert a spec scene to the exact Unreal comparison camera pose."""
    camera_x, camera_y, camera_z = scene["camera"]
    target_x, target_y, target_z = scene["target"]
    # Đổi Y-up sang Z-up rồi nhân 100: Three (X,Y,Z) -> UE (X,Z,Y).
    vertical_fov = 48.0
    horizontal_fov = math.degrees(
        2 * math.atan(math.tan(math.radians(vertical_fov / 2)) * aspect_ratio)
    )
    return {
        "position_cm": [camera_x * 100, camera_z * 100, camera_y * 100],
        "target_cm": [target_x * 100, target_z * 100, target_y * 100],
        "vertical_fov_degrees": vertical_fov,
        "fov_degrees": horizontal_fov,
        "aspect_ratio": aspect_ratio,
    }
