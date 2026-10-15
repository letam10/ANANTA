"""Validate recorded packaged gameplay evidence; never infer quality from source INIs."""

import csv
from datetime import datetime
import json
import math
from pathlib import Path, PurePosixPath
import re
import statistics


TRIAL_CVARS = (
    "r.Lumen.ScreenProbeGather.DownsampleFactor",
    "r.Lumen.Reflections.DownsampleFactor",
    "r.Shadow.Virtual.ResolutionLodBiasDirectional",
)
TRIALS = {"Base": (24, 2, -1.5), "GI32": (32, 2, -1.5),
          "Reflections4": (24, 4, -1.5), "VsmBias0": (24, 2, 0)}
QUALITY_NAMES = (
    "ViewDistance", "AntiAliasing", "Shadow", "GlobalIllumination", "Reflection",
    "PostProcess", "Texture", "Effects", "Foliage", "Shading",
)
FIXED_CVARS = {f"sg.{name}Quality": 3 for name in QUALITY_NAMES}
FIXED_CVARS.update({
    "r.ScreenPercentage": 100, "r.VSync": 0, "t.MaxFPS": 90,
    "r.Lumen.HardwareRayTracing": 0, "r.Shadow.Virtual.SMRT.RayCountDirectional": 4,
    "r.Shadow.Virtual.SMRT.RayCountLocal": 4, "r.Shadow.Virtual.SMRT.SamplesPerRayDirectional": 4,
    "r.Shadow.Virtual.Enable": 1, "r.Nanite.Culling.Frustum": 1, "r.Nanite.Culling.HZB": 1,
    "r.TSR.History.ScreenPercentage": 100,
})
OTHER_CVARS = (
    "r.Streaming.PoolSize", "r.Nanite.Streaming.ReservedResources", "r.Nanite.AsyncRasterization",
    "r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor", "r.Shadow.Virtual.NonNanite.Batch",
    "r.Shadow.Virtual.NonNanite.UseHZB", "r.Shadow.Virtual.NonNanite.IncludeInCoarsePages",
)
COLUMNS = ("elapsed_s", "wall_ms", "game_ms", "render_ms", "rhi_ms", "gpu_ms", "x_cm", "y_cm")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0, "UTC required")
    return parsed.timestamp()


def fingerprint(value):
    require(isinstance(value, dict), "Missing packaged fingerprint")
    containers = value.get("containers")
    require(isinstance(containers, list) and containers, "Missing package containers")
    executable = value.get("executable", {})
    entries = [executable] + containers
    paths = []
    for entry in entries:
        require(isinstance(entry, dict), "Invalid fingerprint entry")
        path = entry.get("path", "")
        require(isinstance(path, str) and path and "\\" not in path, "Invalid artifact path")
        relative = PurePosixPath(path)
        require(not relative.is_absolute() and ".." not in relative.parts and ":" not in path,
                "Fingerprint paths must be relative")
        require(re.fullmatch(r"[0-9a-fA-F]{64}", entry.get("sha256", "")), "Invalid SHA256")
        paths.append(path.casefold())
    require(len(paths) == len(set(paths)), "Duplicate fingerprint artifact")
    require(PurePosixPath(executable["path"]).suffix.lower() == ".exe", "Missing executable hash")
    require(all(PurePosixPath(item["path"]).suffix.lower() in (".pak", ".utoc", ".ucas")
                for item in containers), "Invalid package container")
    # So sánh tên và hash, không phụ thuộc thứ tự liệt kê của hệ thống tệp.
    return tuple(sorted((item["path"].casefold(), item["sha256"].lower()) for item in entries))


def read_configuration(path, trial):
    values = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            require(key not in values, f"Duplicate observed cvar: {key}")
            values[key] = value.strip()
    require(values.pop("output", None) == "1920x1080", "Observed output is not native 1080p")
    numeric = {key: float(value) for key, value in values.items()}
    require(all(math.isfinite(value) for value in numeric.values()), "Nonfinite observed cvar")
    expected = FIXED_CVARS | dict(zip(TRIAL_CVARS, TRIALS[trial]))
    require(set(expected).union(OTHER_CVARS).issubset(numeric), "Incomplete observed render state")
    for key, value in expected.items():
        require(numeric.get(key) == value, f"Unexpected observed {key}: expected {value}")
    return numeric


def frame_statistics(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        require(tuple(reader.fieldnames or ()) == COLUMNS, "Invalid frame CSV header")
        rows = list(reader)
    require(rows, "Empty frame CSV")
    data = []
    for row in rows:
        require(None not in row and all(row.get(key) is not None for key in COLUMNS), "Malformed CSV row")
        values = {key: float(row[key]) for key in COLUMNS}
        require(all(math.isfinite(value) for value in values.values()), "Nonfinite frame CSV")
        require(values["wall_ms"] > 0, "Nonpositive wall frame")
        require(all(values[key] >= 0 for key in COLUMNS[:1] + COLUMNS[2:6]), "Negative frame counter")
        require(not data or values["elapsed_s"] > data[-1]["elapsed_s"], "Elapsed time must increase")
        data.append(values)
    wall = [row["wall_ms"] for row in data]
    mean = statistics.mean(wall)
    result = dict(frames=len(data), observedSeconds=sum(wall) / 1000,
                  elapsedSeconds=data[-1]["elapsed_s"], averageFps=1000 / mean, meanWallMs=mean,
                  p95WallMs=sorted(wall)[math.ceil(len(wall) * .95) - 1], maxWallMs=max(wall),
                  framesOver33Ms=sum(value > 33.3 for value in wall),
                  framesOver50Ms=sum(value > 50 for value in wall), frameTargetMs=1000 / 90,
                  includesAllFrames=True, visualAccepted=False, stable90Accepted=False)
    for name in COLUMNS[2:6]:
        result[name] = statistics.mean(row[name] for row in data)
    require(result["gpu_ms"] > 0, "GPU counters unavailable")
    return result


def load_run(directory: Path) -> dict:
    directory = Path(directory)
    trial = json.loads((directory / "Trial.json").read_text(encoding="utf-8-sig"))
    require(type(trial.get("schemaVersion")) is int and trial["schemaVersion"] == 1, "Unknown trial schema")
    name = trial.get("qualityTrial")
    require(name in TRIALS, "Unknown quality trial")
    require(trial.get("runtimeKind") == "Packaged", "Only packaged gameplay can be compared")
    require(trial.get("diagnostic") == "None" and trial.get("profileRender") is False,
            "Diagnostic/profile runs cannot be compared")
    for key in ("qaSlotsReset", "qaSlotsRestored", "gameplayPassed"):
        require(trial.get(key) is True, f"Missing successful {key}")
    identity = fingerprint(trial.get("artifactFingerprint"))
    started = timestamp(trial["startedUtc"])
    completed = timestamp(trial["completedUtc"])
    require(completed > started, "Invalid run time range")
    for name_on_disk in ("FrameTimes.csv", "RenderConfig.txt", "Report.txt"):
        modified = (directory / name_on_disk).stat().st_mtime
        require(started <= modified <= completed, f"Stale/outside-run evidence: {name_on_disk}")
    report = (directory / "Report.txt").read_text(encoding="utf-8-sig")
    require(re.search(r"^mode=Check process_id=\d+ status=PASSED held_keys_after_cleanup=0$", report, re.M),
            "Missing successful ordinary gameplay marker")
    for marker in ("save_slot=ANANTA_City_QA", "backup_slot=ANANTA_City_QA_Backup",
                   "normal_save_io=false", "input_source=PlayerController.InputKey"):
        require(marker in report.splitlines(), f"Missing gameplay provenance: {marker}")
    return dict(directory=str(directory.resolve()), qualityTrial=name, fingerprint=identity,
                renderConfig=read_configuration(directory / "RenderConfig.txt", name),
                statistics=frame_statistics(directory / "FrameTimes.csv"))
