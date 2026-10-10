"""Receipt order differs between PowerShell culture sorting and Python ordinal sorting."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Editor"))
import CityHLODIdentity as identity


class ReceiptOrderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        qa = self.root / "Saved/QA"
        logs = self.root / "Saved/Logs"
        qa.mkdir(parents=True)
        logs.mkdir()
        now = time.time()
        applied = dict(map=identity.MAP, stage="expanded", writtenGroups=identity.GROUPS,
                       writtenInstances=identity.INSTANCES,
                       layout=dict(widthMetres=identity.WIDTH, groups=identity.GROUPS,
                                   instances=identity.INSTANCES))
        readback = dict(status="PASS", groups=identity.GROUPS, instances=identity.INSTANCES)
        for name, data in (("CityExpansionApplied.json", applied), ("CityMobilityMapReadback.json", readback)):
            path = qa / name
            path.write_text(json.dumps(data), encoding="utf-8")
            os.utime(path, (now - 20, now - 20))
        self.labels = ["City_L0_X0_Y0", "City_L0_X-10_Y-1", "City_L0_X1_Y0"]
        log_path = logs / "CityHLOD-fixture.log"
        lines = [f"{identity.MAP} -RebuildHLODs"]
        lines.extend(f"[{index} / 3] Building HLOD actor {label}..."
                     for index, label in enumerate(self.labels, 1))
        lines.append("#### Built 3 HLOD actors ####")
        log_path.write_text("\n".join(lines), encoding="utf-8")
        os.utime(log_path, (now - 5, now - 5))
        utc = lambda seconds: datetime.fromtimestamp(seconds, timezone.utc).isoformat()
        self.receipt = dict(schemaVersion=1, status="PASS", scope="full", singleHLOD=None,
                            sourceIdentity=identity.source_identity(self.root), forceRebuild=True,
                            startedUtc=utc(now - 10), completedUtc=utc(now - 1),
                            logPath=str(log_path), runId="fixture", logSha256=identity.sha256(log_path),
                            builtActors=list(self.labels), builtActorCount=3)
        self.path = qa / "CityHLODBuildReceipt.json"

    def check(self):
        self.path.write_text(json.dumps(self.receipt), encoding="utf-8")
        return identity.validate_receipt(self.root)

    def test_equal_actor_set_with_different_order(self):
        self.assertNotEqual(self.labels, sorted(self.labels))
        self.check()

    def test_duplicate_actor_rejected(self):
        self.receipt["builtActors"][-1] = self.labels[0]
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_actor_rejected(self):
        self.receipt["builtActors"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_extra_actor_rejected(self):
        self.receipt["builtActors"].append("City_L0_X2_Y0")
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_actor_rejected(self):
        self.receipt["builtActors"][-1] = "Other_L0_X1_Y0"
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_count_rejected(self):
        self.receipt["builtActorCount"] = 2
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
