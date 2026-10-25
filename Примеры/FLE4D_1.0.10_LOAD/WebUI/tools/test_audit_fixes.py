"""Host regressions; does not upload firmware or install libraries."""
import copy
import json
import tempfile
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_project_package as generator

ROOT = Path(__file__).resolve().parents[1]

class Regression(unittest.TestCase):
    def document(self):
        return {"schema": "flprog.webui/1.0", "project": {"id": "audit_test"},
                "channels": [{"id": "value", "type": "float", "direction": "publish", "index": 120}],
                "pages": [{"id": "main", "widgets": [{"id": "display", "type": "indicator", "channel": "value"}]}]}

    def test_stable_addresses(self):
        d = self.document()
        d["channels"].append({"id": "new", "type": "bool", "direction": "publish"})
        generator.validate(d)
        self.assertEqual([c["index"] for c in d["channels"]], [120, 101])
        d["channels"].reverse()
        generator.validate(d)
        self.assertEqual({c["id"]: c["index"] for c in d["channels"]}, {"value": 120, "new": 101})

    def test_duplicate_rejected(self):
        d = self.document()
        d["channels"].append(dict(d["channels"][0], id="other"))
        with self.assertRaises(ValueError): generator.validate(d)

    def test_bindings_are_generated_for_runtime(self):
        d = self.document()
        d["channels"].append({"id": "alarm", "type": "bool", "direction": "publish", "index": 102})
        d["pages"][0]["widgets"][0]["bindings"] = [{"role": "alarm", "channel": "alarm", "direction": "publish"}]
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "project.flpui"
            source.write_text(json.dumps(d), encoding="utf-8")
            result = generator.build(source, Path(tmp) / "packages")
            header = (result / "src/audit_test_descriptor.h").read_text(encoding="utf-8")
            self.assertIn('"alarm", "alarm", "publish"', header)
            self.assertIn("bindings_0, 1", header)

    def test_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "project.flpui"
            source.write_text(json.dumps(self.document()), encoding="utf-8")
            result = generator.build(source, Path(tmp) / "packages")
            self.assertTrue((result / "src/audit_test_descriptor.h").is_file())

    def test_invalid_binding_direction_rejected(self):
        d = self.document()
        d["channels"].append({"id": "command", "type": "float", "direction": "command", "index": 101})
        d["pages"][0]["widgets"][0]["bindings"] = [{"role": "alarm", "channel": "command", "direction": "command"}]
        with self.assertRaises(ValueError): generator.validate(d)

if __name__ == "__main__": unittest.main()
