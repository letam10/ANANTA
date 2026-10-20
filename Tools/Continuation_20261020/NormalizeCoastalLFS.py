"""Normalize only the 88 recorded raw Git blobs, preserving every worktree byte."""

import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

TASK = Path(__file__).resolve().parent
ROOT = TASK.parent.parent


def git(*args):
    process = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True)
    return process.stdout


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert git("branch", "--show-current").decode().strip() == "main"
assert not git("diff", "--cached", "--name-only").strip(), "Index must be empty before this phase"
baseline = json.loads((TASK / "R0_gates.json").read_text(encoding="utf-8-sig"))
paths = sorted(set(re.search(r'"(Assets/CoastalUpgrade/[^\"]+)"', line).group(1)
                   for line in baseline["lfsOutput"] if "unexpectedGitObject" in line))
assert len(paths) == 88, "Unexpected recorded LFS scope"
records = []
for relative in paths:
    path = (ROOT / relative).resolve()
    assert path.is_relative_to((ROOT / "Assets/CoastalUpgrade").resolve())
    assert path.suffix.lower() in (".fbx", ".blend", ".png")
    expected_blob = git("rev-parse", "HEAD:" + relative).decode().strip()
    actual_blob = git("hash-object", "--no-filters", "--", relative).decode().strip()
    assert actual_blob == expected_blob, "Pre-existing worktree modification: " + relative
    records.append({"path": relative, "bytes": path.stat().st_size,
                    "sha256_before": sha(path), "original_git_blob": expected_blob})

# Chỉ thay index theo allowlist; không ghi đè file, không rewrite history.
git("add", "--renormalize", "--", *paths)
for row in records:
    path = ROOT / row["path"]
    row["sha256_after"] = sha(path)
    assert row["sha256_before"] == row["sha256_after"], "Worktree content changed"
    expected = ("version https://git-lfs.github.com/spec/v1\n"
                + "oid sha256:" + row["sha256_before"] + "\nsize " + str(row["bytes"]) + "\n")
    pointer = git("show", ":" + row["path"]).decode()
    assert pointer == expected, "Unexpected index pointer: " + row["path"]
    row["canonical_pointer"] = True

assert set(git("diff", "--cached", "--name-only").decode().splitlines()) == set(paths)
report = {
    "schema": "ananta.c1.lfs-normalization.v1",
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "baseline_head": git("rev-parse", "HEAD").decode().strip(),
    "scope": "88 previously committed non-pointer blobs recorded by R0 fsck",
    "files": records,
    "bytes": sum(row["bytes"] for row in records),
    "worktree_bytes_unchanged": True,
    "index_changes_only": True,
    "history_rewritten": False,
    "full_fsck_after_commit": "pending",
}
(TASK / "C1_lfs_normalization.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("COASTAL_LFS_NORMALIZED", len(records), report["bytes"], "worktree bytes unchanged")
