"""Validate native metadata response handling without launching Unreal or using existing HLOD evidence."""

import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = dict(path="/Game/ANANTA/Maps/ANANTA_City.Boundary", guid="A" * 32)
OTHER = dict(path="/Game/ANANTA/Maps/ANANTA_City.Building", guid="B" * 32)


class Actor:
    def get_actor_label(self):
        return "Proxy_Test"


class BoundaryBridgeTests(unittest.TestCase):
    def check_response(self, response):
        bridge = types.ModuleType("unreal")
        bridge.Paths = types.SimpleNamespace(project_dir=lambda: str(ROOT))
        bridge.CityEditorTools = types.SimpleNamespace(hlod_source_actor_references=lambda actor: response)
        path = ROOT / "Tools/Editor/VerifyCityHLODInstances.py"
        spec = importlib.util.spec_from_file_location("city_hlod_bridge_fixture", path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": bridge}):
            spec.loader.exec_module(module)
            return module.check_boundary_exclusion([Actor()], [BOUNDARY])

    def metadata(self, references):
        return json.dumps(dict(available=True, references=references))

    def test_excluded_source_passes(self):
        result = self.check_response(self.metadata([OTHER]))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["checkedHLODs"], 1)
        self.assertEqual(result["sourceReferences"], 1)

    def test_boundary_guid_case_and_hyphens_fail(self):
        reference = dict(path=OTHER["path"], guid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        result = self.check_response(self.metadata([reference]))
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(len(result["violations"]), 1)

    def test_boundary_path_fails(self):
        reference = dict(path=BOUNDARY["path"], guid=OTHER["guid"])
        self.assertEqual(self.check_response(self.metadata([reference]))["status"], "FAIL")

    def test_unavailable_is_unverified(self):
        result = self.check_response(json.dumps(dict(available=False, reason="Missing cell", references=[])))
        self.assertEqual(result["status"], "UNVERIFIED")

    def test_empty_is_unverified(self):
        self.assertEqual(self.check_response(self.metadata([]))["status"], "UNVERIFIED")

    def test_invalid_guid_is_unverified(self):
        result = self.check_response(self.metadata([dict(path=OTHER["path"], guid="bad-guid")]))
        self.assertEqual(result["status"], "UNVERIFIED")

    def test_zero_guid_is_unverified(self):
        result = self.check_response(self.metadata([dict(path=OTHER["path"], guid="0" * 32)]))
        self.assertEqual(result["status"], "UNVERIFIED")

    def test_invalid_json_is_unverified(self):
        self.assertEqual(self.check_response("broken" )["status"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
