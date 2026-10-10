"""Validate persisted city identity and the full HLOD completion receipt without Unreal."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

MAP = "/Game/ANANTA/Maps/ANANTA_City"
WIDTH = 6788.2250993908565
GROUPS = 85386
INSTANCES = 1660761


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def source_identity(project):
    qa = Path(project) / "Saved/QA"
    applied_path = qa / "CityExpansionApplied.json"
    readback_path = qa / "CityMobilityMapReadback.json"
    applied = read_json(applied_path)
    readback = read_json(readback_path)
    assert applied["map"] == MAP and applied["stage"] == "expanded", "Wrong applied map/stage"
    assert abs(applied["layout"]["widthMetres"] - WIDTH) < 0.000001, "Wrong applied map width"
    assert applied["writtenGroups"] == GROUPS and applied["writtenInstances"] == INSTANCES
    assert applied["layout"]["groups"] == GROUPS and applied["layout"]["instances"] == INSTANCES
    assert readback["status"] == "PASS", "Current map readback is not PASS"
    assert readback["groups"] == GROUPS and readback["instances"] == INSTANCES, "Map readback mismatch"
    assert readback_path.stat().st_mtime >= applied_path.stat().st_mtime, "Map readback predates apply"
    return dict(map=MAP, stage="expanded", widthMetres=applied["layout"]["widthMetres"],
                sourceGroups=GROUPS, sourceInstances=INSTANCES,
                applySha256=sha256(applied_path), readbackSha256=sha256(readback_path))


def built_labels(log):
    completed = re.findall(r"#### Built (\d+) HLOD actors? ####", log)
    assert len(completed) == 1 and int(completed[0]) > 0, "No unique completed HLOD build"
    count = int(completed[0])
    rows = re.findall(r"\[(\d+) / (\d+)\] Building HLOD actor ([^\r\n]+?)\.\.\.", log)
    assert len(rows) == count, "Incomplete HLOD log"
    labels = []
    for index, (number, total, label) in enumerate(rows, 1):
        assert int(number) == index and int(total) == count, "Incomplete HLOD sequence"
        labels.append(label)
    assert len(set(labels)) == count, "Duplicate built HLOD labels"
    return sorted(labels)


def utc(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None, "Receipt timestamp has no timezone"
    return parsed.timestamp()


def validate_receipt(project):
    project = Path(project)
    identity = source_identity(project)
    receipt_path = project / "Saved/QA/CityHLODBuildReceipt.json"
    receipt = read_json(receipt_path)
    assert receipt["schemaVersion"] == 1 and receipt["status"] == "PASS", "No completed HLOD receipt"
    assert receipt["scope"] == "full" and receipt["singleHLOD"] is None, "Sample cannot accept the city"
    assert receipt["sourceIdentity"] == identity, "Stale HLOD source identity"
    assert receipt["forceRebuild"] is True, "Receipt does not prove a forced rebuild"
    started = utc(receipt["startedUtc"])
    completed = utc(receipt["completedUtc"])
    assert started <= completed <= datetime.now(timezone.utc).timestamp(), "Invalid build timestamps"
    for name in ("CityExpansionApplied.json", "CityMobilityMapReadback.json"):
        assert (project / "Saved/QA" / name).stat().st_mtime <= started, "Source evidence changed after build"
    log_path = Path(receipt["logPath"]).resolve()
    assert log_path.parent == (project / "Saved/Logs").resolve(), "Build log is outside project logs"
    assert log_path.name == f"CityHLOD-{receipt['runId']}.log", "Build log run identity mismatch"
    assert started <= log_path.stat().st_mtime <= completed, "Build log is not from receipt interval"
    assert sha256(log_path) == receipt["logSha256"], "Build log changed after completion"
    log = log_path.read_text(encoding="utf-8-sig", errors="replace")
    assert MAP in log and "-RebuildHLODs" in log, "Build log is missing map/rebuild command"
    assert "-BuildSingleHLOD=" not in log, "Partial build log cannot accept the city"
    labels = built_labels(log)
    assert receipt["builtActors"] == labels, "Receipt actor set differs from log"
    assert receipt["builtActorCount"] == len(labels), "Receipt actor count differs from log"
    return identity, receipt


def check_actor_sets(receipt, descriptors, actors, selected_label=""):
    """Names alone are insufficient: require unique descriptor and loaded actor GUID parity."""
    descriptor_pairs = [(str(item[0]), str(item[1])) for item in descriptors]
    actor_pairs = [(str(item[0]), str(item[1])) for item in actors]
    expected = {selected_label} if selected_label else set(receipt["builtActors"])
    assert expected.issubset(receipt["builtActors"]), "Sample is absent from current full build"
    for name, pairs in (("descriptor", descriptor_pairs), ("loaded actor", actor_pairs)):
        assert len(pairs) == len(set(label for label, _ in pairs)), f"Duplicate {name} label"
        assert len(pairs) == len(set(guid for _, guid in pairs)), f"Duplicate {name} GUID"
        assert set(label for label, _ in pairs) == expected, f"{name} set differs from current build"
    assert set(descriptor_pairs) == set(actor_pairs), "HLOD descriptor/actor GUID mismatch"
