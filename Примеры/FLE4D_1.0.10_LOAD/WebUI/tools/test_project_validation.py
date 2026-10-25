import copy
import json
import unittest
from pathlib import Path
from project_validation import validate_project
import build_project_package as g


class ProjectValidation(unittest.TestCase):
    def document(self):
        return dict(schema="flprog.webui/1.0", project=dict(id="validation_test"),
                    channels=[dict(id="number",type="float",direction="duplex",index=101),
                              dict(id="flag",type="bool",direction="publish",index=102)],
                    pages=[dict(id="main",title="Главная",widgets=[dict(id="input",type="number-input",label="Уставка",channel="number",x=1,y=1,w=4,h=2)])])

    def codes(self, document):
        return {i["code"] for i in validate_project(document)["issues"]}

    def test_valid_projects_unchanged(self):
        for path in (Path(__file__).resolve().parents[1]/"projects").glob("*.flpui"):
            document=json.loads(path.read_text(encoding="utf-8"));before=copy.deepcopy(document)
            self.assertTrue(validate_project(document)["valid"],path.name)
            self.assertEqual(document,before)

    def test_collects_multiple_widget_errors_and_targets(self):
        d=self.document();d["pages"][0]["widgets"][0]["channel"]="flag"
        d["pages"].append(dict(id="other",title="Другая",widgets=[dict(id="missing",type="switch",channel="gone")]))
        report=validate_project(d)
        self.assertIn("widget-channel-type",{i["code"] for i in report["issues"]})
        issue=next(i for i in report["issues"] if i["code"]=="missing-channel")
        self.assertEqual((issue["pageIndex"],issue["widgetIndex"]),(1,0))
        self.assertGreaterEqual(report["summary"]["errors"],2)

    def test_readonly_commands(self):
        d=self.document();d["channels"][0]["direction"]="publish"
        self.assertIn("readonly-command",self.codes(d))
        d["channels"].append(dict(id="command",type="float",direction="command",index=103))
        d["pages"][0]["widgets"][0]["bindings"]=[dict(role="setpoint",channel="command",direction="command")]
        self.assertTrue(validate_project(d)["valid"])

    def test_missing_and_wrong_binding_types(self):
        d=self.document();d["pages"][0]["widgets"][0]["bindings"]=[dict(role="busy",channel="number",direction="publish"),dict(role="alarm",channel="missing")]
        self.assertTrue({"binding-type","missing-binding-channel"}<=self.codes(d))

    def test_overlap_is_warning_and_has_two_targets(self):
        d=self.document();w=d["pages"][0]["widgets"][0];d["pages"][0]["widgets"].append(dict(w,id="copy",x=3))
        report=validate_project(d);self.assertEqual(report["summary"],dict(errors=0,warnings=1))
        self.assertEqual(report["issues"][0]["relatedWidgetIndex"],1)
        self.assertTrue(report["valid"])

    def test_touching_and_different_groups_do_not_overlap(self):
        d=self.document();w=d["pages"][0]["widgets"][0];d["pages"][0]["widgets"].append(dict(w,id="copy",x=5))
        self.assertNotIn("overlap",self.codes(d))
        d["pages"][0]["widgets"][1].update(x=1,group="Другая")
        self.assertNotIn("overlap",self.codes(d))

    def test_legacy_limits_preserved(self):
        d=self.document();d["pages"][0]["widgets"][0]["step"]=0
        self.assertFalse(validate_project(d)["valid"])
        with self.assertRaises(ValueError):g.validate(d)

    def test_invalid_channel_type_points_to_widget(self):
        d=self.document();d["channels"][0]["type"]="unknown"
        issue=next(i for i in validate_project(d)["issues"] if i["code"]=="channel-type")
        self.assertEqual(issue["widgetIndex"],0)

    def test_corrupt_structures_return_errors(self):
        for d in (None,[],dict(channels="bad"),dict(channels=[],pages=[None]),dict(channels=[dict(type=[])],pages=[])):
            self.assertFalse(validate_project(d)["valid"])


if __name__=="__main__":unittest.main()
