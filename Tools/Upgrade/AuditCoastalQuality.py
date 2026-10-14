"""Engine-free audit of CoastalCity upgrade evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_AZIMUTHS = [0, 45, 90, 135, 180, 225, 270, 315]


class Audit:
    def __init__(self, root: Path, allow_missing: bool) -> None:
        self.root = root
        self.allow_missing = allow_missing
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.counts: Counter[str] = Counter()
        self.models: dict[str, dict[str, Any]] = {}

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def load(self, relative: str, required: bool) -> Any | None:
        path = self.root / relative
        if not path.is_file():
            if required:
                self.fail(f"missing required {relative}")
            else:
                label = "allowed" if self.allow_missing else "optional"
                self.warn(f"missing {label} evidence {relative}")
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.fail(f"invalid JSON {relative}: {type(error).__name__}")
            return None

    def check_dimensions(self, name: str, model: dict[str, Any]) -> None:
        dimensions = model.get("dimensions_m")
        valid = (
            isinstance(dimensions, list)
            and len(dimensions) == 3
            and all(isinstance(value, (int, float)) and value > 0 for value in dimensions)
        )
        if not valid:
            self.fail(f"model {name} dimensions_m must be 3 positive numbers")

    def check_azimuths(self, label: str, row: dict[str, Any]) -> None:
        values = row.get("azimuth_degrees", row.get("azimuths"))
        if values != EXPECTED_AZIMUTHS:
            self.fail(f"{label} azimuths must be [0,45,90,135,180,225,270,315]")

    def hash_fbx(self, name: str) -> str | None:
        path = self.root / "Assets" / "CoastalUpgrade" / f"{name}.fbx"
        if not path.is_file():
            self.warn(f"source FBX unavailable for {name}")
            return None
        try:
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            return digest.hexdigest()
        except OSError as error:
            self.fail(f"cannot hash {name}.fbx: {type(error).__name__}")
            return None

    def check_hash(self, label: str, name: str, row: dict[str, Any]) -> None:
        actual = self.hash_fbx(name)
        expected = row.get("source_sha256")
        if actual is None:
            return
        if not isinstance(expected, str) or not expected:
            self.fail(f"{label} source_sha256 missing for {name}")
        elif expected.lower() != actual:
            self.fail(f"{label} source_sha256 mismatch for {name}")

    def check_manifest(self) -> None:
        data = self.load("Assets/CoastalUpgrade/manifest.json", required=True)
        if data is None:
            return
        models = data.get("models") if isinstance(data, dict) else None
        if not isinstance(models, list):
            self.fail("manifest models must be a list")
            return
        for model in models:
            if not isinstance(model, dict) or not isinstance(model.get("name"), str):
                self.fail("manifest contains a model without name")
                continue
            name = model["name"]
            if name in self.models:
                self.fail(f"duplicate manifest model {name}")
            self.models[name] = model
            self.check_dimensions(name, model)
            if "azimuth_degrees" in model or "azimuths" in model:
                self.check_azimuths(f"manifest model {name}", model)
            if "source_sha256" in model:
                self.check_hash("manifest", name, model)
        self.counts["manifest_models"] = len(self.models)

    def view_path(self, value: Any) -> Path | None:
        if not isinstance(value, str) or not value:
            return None
        path = Path(value)
        return path if path.is_absolute() else self.root / path

    def check_model_views(self) -> None:
        data = self.load("Saved/Upgrade/ModelViews/coverage.json", required=False)
        if data is None:
            return
        rows = data.get("models", data.get("coverage")) if isinstance(data, dict) else data
        if not isinstance(rows, list):
            self.fail("model coverage must be a list")
            return
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("model"), str):
                self.fail("model coverage contains an entry without model")
                continue
            name = row["model"]
            if name in seen:
                self.fail(f"duplicate model coverage {name}")
            seen.add(name)
            if name not in self.models:
                self.fail(f"coverage model not in manifest {name}")
            self.check_azimuths(f"coverage {name}", row)
            views = row.get("views")
            if not isinstance(views, list) or len(views) != 8:
                self.fail(f"coverage {name} must contain 8 view paths")
            else:
                for index, value in enumerate(views):
                    path = self.view_path(value)
                    if path is None or not path.is_file():
                        self.fail(f"coverage {name} view {index} does not exist")
            self.check_hash("coverage", name, row)
        missing = sorted(set(self.models) - seen)
        if missing:
            self.fail(f"coverage missing manifest models: {','.join(missing[:3])}")
        self.counts["coverage_models"] = len(rows)

    def check_imports(self) -> None:
        data = self.load("Saved/Upgrade/import-readback.json", required=False)
        if data is None:
            return
        rows = data.get("models", data.get("imports")) if isinstance(data, dict) else data
        if not isinstance(rows, list):
            self.fail("import readback must be a list")
            return
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("name"), str):
                self.fail("import readback contains an entry without name")
                continue
            name = row["name"]
            if name in seen:
                self.fail(f"duplicate import readback {name}")
            seen.add(name)
            lods = row.get("lod_count")
            if lods is None and isinstance(row.get("lods"), list):
                lods = len(row["lods"])
            collisions = row.get("collision_shapes")
            if collisions is None and isinstance(row.get("collision"), list):
                collisions = len(row["collision"])
            if lods != 3:
                self.fail(f"import {name} must have 3 LODs")
            if collisions != 1:
                self.fail(f"import {name} must have one collision")
        self.counts["import_readback"] = len(rows)

    def expected_review_units(
        self, buildings: list[Any], views: list[dict[str, Any]]
    ) -> list[str]:
        has_rooms = any(
            isinstance(building, dict) and isinstance(building.get("rooms"), dict)
            and building["rooms"]
            for building in buildings
        )
        units: list[str] = []
        for building in buildings:
            if not isinstance(building, dict) or not isinstance(building.get("name"), str):
                self.fail("city layout contains a building without name")
                continue
            name = building["name"]
            rooms = building.get("rooms")
            if isinstance(rooms, dict) and rooms:
                units.extend(f"{name}_{room}" for room in rooms)
            elif not has_rooms or any(
                isinstance(view.get("name"), str)
                and view["name"].startswith(name + "_")
                for view in views
            ):
                units.append(name)
        return units

    def check_layout(self) -> None:
        data = self.load("Saved/Upgrade/city-layout.json", required=True)
        if data is None:
            return
        if not isinstance(data, dict):
            self.fail("city layout must be an object")
            return
        buildings = data.get("buildings")
        views = data.get("review_views")
        if not isinstance(buildings, list) or not isinstance(views, list):
            self.fail("city layout requires buildings and review_views lists")
            return
        names: list[str] = []
        valid_views: list[dict[str, Any]] = []
        for view in views:
            if not isinstance(view, dict) or not isinstance(view.get("name"), str):
                self.fail("review view contains an entry without name")
                continue
            names.append(view["name"])
            valid_views.append(view)
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        if duplicates:
            self.fail(f"duplicate review view names: {','.join(duplicates[:3])}")
        units = self.expected_review_units(buildings, valid_views)
        counts = Counter()
        for view in valid_views:
            for unit in units:
                if view["name"] == unit or view["name"].startswith(unit + "_"):
                    counts[unit] += 1
                    break
        for unit in units:
            if counts[unit] != 5:
                self.fail(f"review unit {unit} must have exactly 5 views")
        self.counts["layout_buildings"] = len(buildings)
        self.counts["layout_review_units"] = len(units)
        self.counts["layout_review_views"] = len(views)

    def check_room_coverage(self) -> None:
        root = self.root / "Saved" / "Upgrade" / "RoomGeometry"
        paths = sorted(root.glob("*/coverage.json")) if root.is_dir() else []
        if not paths:
            label = "allowed" if self.allow_missing else "optional"
            self.warn(f"missing {label} evidence Saved/Upgrade/RoomGeometry/*/coverage.json")
            return
        for path in paths:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                self.fail(f"invalid room coverage {path.parent.name}: {type(error).__name__}")
                continue
            if not isinstance(data, dict) or not isinstance(data.get("views"), list):
                self.fail(f"room coverage {path.parent.name} requires views list")
        self.counts["room_coverage_files"] = len(paths)

    def run(self) -> bool:
        self.check_manifest()
        self.check_model_views()
        self.check_imports()
        self.check_layout()
        self.check_room_coverage()
        return not self.errors

    def report(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "root": str(self.root),
            "checks": dict(sorted(self.counts.items())),
            "warnings": self.warnings,
        }


def emit(prefix: str, message: str) -> None:
    line = f"{prefix} {message}".strip()
    if len(line) > 120:
        line = line[:117] + "..."
    print(line)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--allow-missing-evidence", action="store_true")
    args = parser.parse_args()
    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    audit = Audit(root, args.allow_missing_evidence)
    if not audit.run():
        for error in audit.errors:
            emit("COASTAL_QUALITY_FAIL", error)
        emit("COASTAL_QUALITY_FAIL", f"checks={len(audit.errors)}")
        return 1
    for warning in audit.warnings:
        emit("COASTAL_QUALITY_WARN", warning)
    report = root / "Saved" / "Upgrade" / "coastal-quality-report.json"
    try:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            json.dumps(audit.report(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        emit("COASTAL_QUALITY_FAIL", f"cannot write report: {type(error).__name__}")
        return 1
    emit(
        "COASTAL_QUALITY_OK",
        f"manifest_models={audit.counts.get('manifest_models', 0)} "
        f"review_units={audit.counts.get('layout_review_units', 0)} "
        f"warnings={len(audit.warnings)} report=Saved/Upgrade/coastal-quality-report.json",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
