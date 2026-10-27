import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from build_compatibility import export_report, sketch_report, MANIFEST
from build_project_package import build

ROOT = Path(__file__).resolve().parents[1]


class BuildCompatibilityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ide = self.root / 'IDE'
        (self.ide / 'arduino-builder.exe').parent.mkdir(parents=True)
        (self.ide / 'arduino-builder.exe').touch()
        core = self.ide / 'portable/packages/STMicroelectronics/hardware/stm32/3.0.0/cores/arduino/Arduino.h'
        core.parent.mkdir(parents=True); core.touch()
        self.libs = self.root / 'Project with spaces/libraries'
        self.doc = json.loads((ROOT / 'projects/preview_busy_demo.flpui').read_text(encoding='utf-8'))
        self.doc['project']['id'] = 'panel-a'
        self.source = self.root / 'panel.flpui'
        self.source.write_text(json.dumps(self.doc), encoding='utf-8')
        self.package = build(self.source, self.libs)
        shutil.copytree(ROOT / 'runtime/FLProg_WebUI', self.libs / 'FLProg_WebUI')
        network = self.libs / 'FLProg_Network/src/flprogNetwork.h'
        network.parent.mkdir(parents=True); network.write_text('// network')
        self.sketch = self.root / 'app.ino'
        self.sketch.write_text('#include <panel-a_webui.h>\nvoid setup(){FLPROG_WEBUI_BEGIN_SELECTED();}\nvoid loop(){}')

    def check(self):
        return sketch_report(self.sketch, self.ide, self.libs)

    def messages(self, report):
        return '\n'.join(c['message'] for c in report['checks'])

    def test_matching_package_no_mutation(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertTrue(self.check()['ok'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_missing_project_header(self):
        self.sketch.write_text('#include <wrong_webui.h>')
        report = self.check()
        self.assertFalse(report['ok']); self.assertIn('Не найден wrong_webui.h', self.messages(report))

    def test_old_runtime_same_version_rejected(self):
        header = self.libs / 'FLProg_WebUI/src/FLProgWebUi.h'
        header.write_text(header.read_text(encoding='utf-8').replace('#define FLPROG_WEBUI_DESCRIPTOR_API 1', ''), encoding='utf-8')
        self.assertFalse(self.check()['ok'])
        self.assertIn('Несовместимая FLProg_WebUI', self.messages(self.check()))

    def test_changed_or_missing_generated_header(self):
        header = self.package / 'src/panel_a_descriptor.h'
        header.write_text('// stale')
        self.assertFalse(self.check()['ok'])
        header.unlink(); self.assertFalse(self.check()['ok'])

    def test_catalog_runtime_helper_required_before_compiler(self):
        (self.libs / 'FLProg_WebUI/src/adapters/FLProgWebUiWidgetCatalog.h').unlink()
        report = self.check()
        self.assertFalse(report['ok'])
        self.assertIn('каталога виджетов', self.messages(report))

    def test_missing_manifest_requires_explicit_regeneration(self):
        (self.package / MANIFEST).unlink()
        self.assertFalse(self.check()['ok'])
        self.assertIn('Пересоберите', self.messages(self.check()))

    def test_manifest_id_and_paths_checked(self):
        manifest_path = self.package / MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['projectId'] = 'another'
        manifest_path.write_text(json.dumps(manifest))
        self.assertFalse(self.check()['ok'])
        manifest['projectId'] = 'panel-a'
        manifest['files']['../outside.h'] = '0' * 64
        manifest_path.write_text(json.dumps(manifest))
        self.assertFalse(self.check()['ok'])

    def test_core_271_is_not_accepted(self):
        (self.ide / 'portable/packages/STMicroelectronics/hardware/stm32/3.0.0/cores/arduino/Arduino.h').unlink()
        old = self.ide / 'portable/packages/STMicroelectronics/hardware/stm32/2.7.1/cores/arduino/Arduino.h'
        old.parent.mkdir(parents=True); old.touch()
        self.assertFalse(self.check()['ok'])
        self.assertIn('2.7.1 не поддерживается', self.messages(self.check()))

    def test_missing_network_and_multiple_projects(self):
        shutil.rmtree(self.libs / 'FLProg_Network')
        self.assertFalse(self.check()['ok'])
        self.sketch.write_text('#include <panel-a_webui.h>\n#include <other_webui.h>')
        self.assertIn('несколько проектов', self.messages(self.check()))

    def test_duplicates_reported_comments_not_includes(self):
        duplicate = self.ide / 'portable/sketchbook/libraries/FLProg_WebUI'
        shutil.copytree(self.libs / 'FLProg_WebUI', duplicate)
        self.sketch.write_text(self.sketch.read_text() + '\n/* #include <comment_webui.h> */\n// #include <other_webui.h>')
        report = self.check()
        self.assertTrue(report['ok']); self.assertGreater(report['summary']['warnings'], 0)

    def test_export_check_readonly_and_ide_copy_gated(self):
        self.doc['projectFolder'] = str(self.root / 'Not yet created')
        report = export_report(self.doc, ROOT, self.root / 'projects', self.root / 'packages', self.ide / 'libraries')
        self.assertTrue(report['ok']); self.assertFalse((self.root / 'Not yet created').exists())
        self.doc['installToIde'] = True
        self.assertFalse(export_report(self.doc, ROOT, self.root / 'projects', self.root / 'packages', self.ide / 'libraries')['ok'])

    def test_export_rejects_file_in_path_without_writes(self):
        bad = self.root / 'file'; bad.write_text('keep')
        self.doc['projectFolder'] = str(bad / 'project')
        self.assertFalse(export_report(self.doc, ROOT, '.', '.', self.ide)['ok'])
        self.assertEqual(bad.read_text(), 'keep')

    def test_malformed_document_reported_without_exception(self):
        for document in (None, [], {'schema': 'wrong'}, {'schema': 'flprog.webui/1.0', 'project': 'bad'}):
            self.assertFalse(export_report(document, ROOT, '.', '.', self.ide)['ok'])

    def test_compiler_not_started_on_preflight_error(self):
        source = ROOT.parent / 'hardware_gates/STM32_OTA_PORTABILITY/build_stm32_ota.py'
        spec = importlib.util.spec_from_file_location('preflight_builder', source)
        builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
        builder.ROOT = self.root / 'build_tools'; builder.IDE = self.ide
        self.sketch.write_text('#include <missing_webui.h>')
        with patch.object(builder, 'boards', return_value={'Board': dict(layout=1, fqbn='x')}), patch.object(builder.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'Не найден missing_webui.h'):
                builder.build('Board', self.sketch, libraries=self.libs)
            run.assert_not_called()
        self.assertFalse(builder.ROOT.exists())
