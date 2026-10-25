"""Regressions for 1.7 project data. No network or controller access."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import build_project_package as g


class Controls(unittest.TestCase):
    def document(self):
        return dict(schema="flprog.webui/1.0", project=dict(id="controls_test"),
                    channels=[dict(id="setpoint", type="float", direction="duplex", index=101)],
                    pages=[dict(id="main", widgets=[dict(id="field", type="number-input", channel="setpoint",
                        group="Насосная", placeholder="Введите число", unit="°C", maxLength=20,
                        confirmation="Изменить уставку?", min=0, max=100, step=0.5)])])

    def test_metadata_survives_package(self):
        document = self.document()
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "test.flpui"
            source.write_text(json.dumps(document), encoding="utf-8")
            package = g.build(source, Path(temporary) / "out")
            header = (package / "src/controls_test_descriptor.h").read_text(encoding="utf-8")
            for expected in ('"Насосная"', '"Введите число"', '"°C"', '"Изменить уставку?"'):
                self.assertIn(expected, header)
        config = g._widget_config(document["pages"][0]["widgets"][0], {})
        self.assertEqual(config["maxLength"], 20)

    def test_invalid_ranges_and_lengths(self):
        for key, value in [("step", 0), ("step", -1), ("min", 101), ("max", float("nan")),
                           ("maxLength", 0), ("maxLength", 64)]:
            document = self.document()
            document["pages"][0]["widgets"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                g.validate(document)

    def test_duplicate_widget_ids_rejected(self):
        document = self.document()
        document["pages"][0]["widgets"].append(copy.deepcopy(document["pages"][0]["widgets"][0]))
        with self.assertRaises(ValueError):
            g.validate(document)

    def test_old_button_keeps_confirmation(self):
        self.assertEqual(g._widget_config(dict(type="button"), {})["confirmation"], "Отправить команду?")
        self.assertEqual(g._widget_config(dict(type="button", confirmation=""), {})["confirmation"], "")


if __name__ == "__main__":
    unittest.main()
