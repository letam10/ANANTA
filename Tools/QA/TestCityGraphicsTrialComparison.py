"""Synthetic tempfile checks only: no Unreal, user saves, or performance acceptance."""

import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

from CityGraphicsTrialData import COLUMNS, FIXED_CVARS, OTHER_CVARS, TRIAL_CVARS, TRIALS, load_run
from CompareCityGraphicsTrials import compare_runs


class TrialComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = {name: self.make_run(name) for name in TRIALS}

    def make_run(self, name):
        path = self.root / name
        path.mkdir()
        now = time.time()
        metadata = dict(schemaVersion=1, qualityTrial=name, diagnostic="None", profileRender=False,
                        runtimeKind="Packaged", gameplayPassed=True, qaSlotsReset=True, qaSlotsRestored=True,
                        startedUtc=datetime.fromtimestamp(now - 5, timezone.utc).isoformat(),
                        completedUtc=datetime.fromtimestamp(now + 5, timezone.utc).isoformat(),
                        artifactFingerprint=dict(
                            executable=dict(path="ANANTA/Binaries/Win64/ANANTA.exe", sha256="a" * 64),
                            containers=[dict(path="ANANTA/Content/Paks/ANANTA.pak", sha256="b" * 64)]))
        (path / "Trial.json").write_text(json.dumps(metadata), encoding="utf-8")
        values = FIXED_CVARS | dict.fromkeys(OTHER_CVARS, 1) | dict(zip(TRIAL_CVARS, TRIALS[name]))
        config = "output=1920x1080\n" + "\n".join(f"{key}={value}" for key, value in values.items())
        (path / "RenderConfig.txt").write_text(config, encoding="utf-8")
        (path / "Report.txt").write_text(
            "mode=Check process_id=123 status=PASSED held_keys_after_cleanup=0\n"
            "save_slot=ANANTA_City_QA\nbackup_slot=ANANTA_City_QA_Backup\n"
            "normal_save_io=false\ninput_source=PlayerController.InputKey\n", encoding="utf-8")
        (path / "FrameTimes.csv").write_text(
            ",".join(COLUMNS) + "\n0.02,20,5,18,3,17,0,0\n0.08,60,6,22,4,21,100,-20\n", encoding="utf-8")
        (path / "Summary.json").write_text('{"averageFps":99999}', encoding="utf-8")
        return path

    def metadata(self, path, mutate):
        target = path / "Trial.json"
        data = json.loads(target.read_text(encoding="utf-8"))
        mutate(data)
        target.write_text(json.dumps(data), encoding="utf-8")

    def test_base_and_three_variants_include_every_frame(self):
        result = compare_runs(self.paths["Base"], [self.paths[name] for name in TRIALS if name != "Base"])
        self.assertEqual(len(result["candidates"]), 3)
        stats = result["baseline"]["statistics"]
        self.assertEqual((stats["frames"], stats["averageFps"], stats["p95WallMs"]), (2, 25, 60))
        self.assertEqual((stats["gpu_ms"], stats["framesOver50Ms"]), (19, 1))
        self.assertTrue(result["includesAllFrames"])
        self.assertFalse(result["visualAccepted"])
        self.assertFalse(result["stable90Accepted"])
        self.assertEqual(result["candidates"][0]["deltaFromBase"]["averageFps"], 0)

    def test_invalid_metadata(self):
        path = self.paths["GI32"]
        original = json.loads((path / "Trial.json").read_text(encoding="utf-8"))
        cases = {"schemaVersion": 2, "runtimeKind": "Editor", "diagnostic": "VsmOff", "profileRender": True,
                 "qaSlotsReset": False, "qaSlotsRestored": False, "gameplayPassed": False,
                 "artifactFingerprint": None, "qualityTrial": "unknown", "startedUtc": original["completedUtc"]}
        for key, value in cases.items():
            with self.subTest(key=key):
                data = copy.deepcopy(original)
                data[key] = value
                (path / "Trial.json").write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_run(path)

    def test_missing_containers_or_changed_package(self):
        path = self.paths["GI32"]
        self.metadata(path, lambda data: data["artifactFingerprint"]["executable"].update(sha256="c" * 64))
        with self.assertRaisesRegex(ValueError, "artifact mismatch"):
            compare_runs(self.paths["Base"], [path])
        self.metadata(path, lambda data: data["artifactFingerprint"].update(containers=[]))
        with self.assertRaisesRegex(ValueError, "containers"):
            load_run(path)

    def test_uncontrolled_cvar_and_wrong_quality(self):
        path = self.paths["GI32"]
        config = path / "RenderConfig.txt"
        original = config.read_text(encoding="utf-8")
        for before, after in (("output=1920x1080", "output=1280x720"),
                              ("r.ScreenPercentage=100", "r.ScreenPercentage=66"),
                              ("DownsampleFactor=32", "DownsampleFactor=24"),
                              ("r.Nanite.AsyncRasterization=1", "r.Nanite.AsyncRasterization=0"),
                              ("sg.TextureQuality=3", "sg.TextureQuality=MISSING")):
            with self.subTest(change=after):
                config.write_text(original.replace(before, after), encoding="utf-8")
                with self.assertRaises(ValueError):
                    compare_runs(self.paths["Base"], [path])

    def test_invalid_frames(self):
        path = self.paths["GI32"]
        csv = path / "FrameTimes.csv"
        header = ",".join(COLUMNS) + "\n"
        for rows in ("", "0.02,0,1,1,1,1,0,0\n", "0.02,nan,1,1,1,1,0,0\n",
                     "0.02,20,-1,1,1,1,0,0\n", "0.02,20,1,1,1,0,0,0\n",
                     "0.02,20,1,1,1,1,0,0\n0.01,20,1,1,1,1,0,0\n", "0.02,20,1\n"):
            with self.subTest(rows=rows):
                csv.write_text(header + rows, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_run(path)

    def test_stale_files_and_missing_gameplay(self):
        path = self.paths["GI32"]
        for name in ("FrameTimes.csv", "Report.txt", "RenderConfig.txt"):
            target = path / name
            original = target.stat().st_mtime
            os.utime(target, (1, 1))
            with self.assertRaisesRegex(ValueError, "outside-run"):
                load_run(path)
            os.utime(target, (original, original))
        (path / "Report.txt").write_text("status=PASSED", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "gameplay marker"):
            load_run(path)

    def test_wrong_baseline_and_duplicate_candidates(self):
        with self.assertRaises(ValueError):
            compare_runs(self.paths["GI32"], [self.paths["Base"]])
        with self.assertRaises(ValueError):
            compare_runs(self.paths["Base"], [self.paths["GI32"], self.paths["GI32"]])

    def test_cli_writes_comparison(self):
        import sys

        script = Path(__file__).with_name("CompareCityGraphicsTrials.py")
        output = self.root / "Comparison.json"
        command = [sys.executable, str(script), str(self.paths["Base"]), str(self.paths["GI32"]),
                   "--output", str(output)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(output.read_text(encoding="utf-8"))["stable90Accepted"])

    @unittest.skipUnless(os.name == "nt", "PowerShell save-isolation fixture runs on Windows")
    def test_powershell_save_restoration_after_failure(self):
        helper = Path(__file__).resolve().parents[1] / "Build" / "CityGraphicsTrialEvidence.ps1"
        script = self.root / "CheckSave.ps1"
        script.write_text(r'''
param($Helper, $Root)
$ErrorActionPreference = 'Stop'
. $Helper
$saved = Join-Path $Root 'Saved'
$slots = Join-Path $saved 'SaveGames'
New-Item -ItemType Directory -Path $slots -Force | Out-Null
$primary = Join-Path $slots 'ANANTA_City_QA.sav'
$backup = Join-Path $slots 'ANANTA_City_QA_Backup.sav'
$ordinary = Join-Path $slots 'ANANTA_City.sav'
[IO.File]::WriteAllText($primary, 'original QA')
[IO.File]::WriteAllText($ordinary, 'ordinary untouched')
$snapshot = @(Get-CityQASlotSnapshot $saved)
try {
    Reset-CityQASlots $saved $snapshot
    if (Test-Path -LiteralPath $primary) {
        throw 'Reset failed'
    }
    [IO.File]::WriteAllText($primary, 'new QA')
    [IO.File]::WriteAllText($backup, 'new backup')
    throw 'simulated process failure'
} catch {
    if ($_.Exception.Message -ne 'simulated process failure') {
        throw
    }
} finally {
    Restore-CityQASlots $saved $snapshot
}
if ([IO.File]::ReadAllText($primary) -ne 'original QA') {
    throw 'Restore failed'
}
if (Test-Path -LiteralPath $backup) {
    throw 'Originally absent backup was retained'
}
if ([IO.File]::ReadAllText($ordinary) -ne 'ordinary untouched') {
    throw 'Ordinary slot changed'
}
try {
    Assert-CityQASlotPath $saved $ordinary
    throw 'Unsafe path was accepted'
} catch {
    if ($_.Exception.Message -eq 'Unsafe path was accepted') {
        throw
    }
}
''', encoding="utf-8")
        result = subprocess.run(["powershell", "-NoProfile", "-File", str(script), str(helper), str(self.root)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
