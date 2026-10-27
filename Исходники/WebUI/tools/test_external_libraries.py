import importlib.util,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]

class ExternalLibrariesTest(unittest.TestCase):
    def test_builder_passes_external_path_as_one_argument(self):
        source=ROOT/'hardware_gates/STM32_OTA_PORTABILITY/build_stm32_ota.py'
        spec=importlib.util.spec_from_file_location('external_library_builder',source)
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        class Captured(Exception):pass
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sketch=root/'user.ino';sketch.write_text('void setup(){} void loop(){}')
            libraries=root/'User projects/a123/libraries';libraries.mkdir(parents=True)
            builder.ROOT=root
            row=dict(layout=1,fqbn='STMicroelectronics:stm32:Example',ram=131072)
            with patch.object(builder,'boards',return_value={'Example':row}),patch.object(builder.subprocess,'run',side_effect=Captured) as run:
                with self.assertRaises(Captured):builder.build('Example',sketch,libraries=libraries)
                args=run.call_args[0][0]
                self.assertEqual(args[args.index('-libraries')+1],str(libraries.resolve()))
                self.assertEqual(args[-1],str(sketch.resolve()))
                self.assertEqual(list(libraries.iterdir()),[])
    def test_batch_forwards_external_libraries(self):
        source=ROOT/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER/loader_batch.py'
        spec=importlib.util.spec_from_file_location('external_batch',source)
        batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);binary=root/'result.bin';binary.write_bytes(b'1234')
            from types import SimpleNamespace
            from unittest.mock import Mock
            builder=SimpleNamespace(ROOT=root,build=Mock(return_value=binary))
            report=batch.run(builder,['Example'],'user.ino',lambda report:None,libraries='external libraries')
            builder.build.assert_called_once_with('Example','user.ino',libraries='external libraries')
            self.assertEqual(report['rows']['Example']['status'],'success')
