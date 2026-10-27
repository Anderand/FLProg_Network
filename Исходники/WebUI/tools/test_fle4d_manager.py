import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[2]
PORTING=ROOT/'hardware_gates/STM32_OTA_PORTABILITY'
MANAGER=ROOT/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER'
sys.path.insert(0,str(PORTING));sys.path.insert(0,str(MANAGER))
import build_stm32_ota as builder
import loader_batch
import manager_extensions


class Fle4dManagerTest(unittest.TestCase):
    def test_default_board_and_geometry(self):
        rows=builder.boards()
        self.assertEqual(builder.visible_build_boards(rows),['FLProg_FLE4D_30MT'])
        self.assertIn('FLProg_FLE4C_30MT',builder.visible_build_boards(rows,True))
        row=rows[builder.DEFAULT_BUILD_BOARD]
        self.assertEqual((row['flash'],row['ram'],row['layout']),(1048576,131072,1))
        self.assertEqual(row['profile_properties']['build.variant_h'],'variant_BLACK_F407VX.h')
        self.assertEqual(row['profile_properties']['build.product_line'],'STM32F407xx')
        self.assertEqual(row['flash_profile_id'],'fle4d_30mt_ota_block_1_0_1')
        self.assertIn('FLPROG_WEBUI_GZIP_ASSETS=1',row['profile_properties']['build.extra_flags'])

    def test_profile_without_preinstalled_local_fle4d(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);core=root/'core';core.mkdir()
            (core/'boards.txt').write_text('GenFLProgF4.name=FLProg\n')
            local=core/'boards.local.txt';original='# user custom profile\nMyBoard.name=Keep\n'
            local.write_text(original)
            row=builder.boards()[builder.DEFAULT_BUILD_BOARD]
            with patch.object(builder,'ROOT',root),patch.object(builder,'CORE',core),patch.object(builder,'boards',return_value={builder.DEFAULT_BUILD_BOARD:row}):
                builder.install_profiles();first=local.read_text()
                builder.install_profiles();self.assertEqual(local.read_text(),first)
            prefix='GenFLProgF4.menu.pnum.FLProg_FLE4D_30MT_OTA_SAFE'
            self.assertTrue(first.startswith(original))
            self.assertIn(prefix+'.build.variant_h=variant_BLACK_F407VX.h',first)
            self.assertIn(prefix+'.build.product_line=STM32F407xx',first)
            self.assertIn(prefix+'.upload.maximum_size=458752',first)
            self.assertIn(prefix+'.build.flash_offset=0x10000',first)
            self.assertIn('FLPROG_STM32_OTA_LAYOUT=1',first)
            self.assertEqual((core/'boards.txt').read_text(),'GenFLProgF4.name=FLProg\n')

    def test_bin_only_has_one_compile_and_no_bootloader_or_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sketch=root/'app.ino';sketch.write_text('void setup(){} void loop(){}')
            row=builder.boards()[builder.DEFAULT_BUILD_BOARD]
            def compile_only(command,**kwargs):
                self.assertIn('pnum=FLProg_FLE4D_30MT_OTA_SAFE',command[command.index('-fqbn')+1])
                output=Path(command[command.index('-build-path')+1]);output.mkdir(parents=True,exist_ok=True)
                (output/'app.ino.bin').write_bytes(struct.pack('<II',0x20020000,0x08010009)+b'12345678')
                return SimpleNamespace(returncode=0)
            with patch.object(builder,'ROOT',root),patch.object(builder,'require_sketch',return_value={'checks':[],'summary':{'errors':0,'warnings':0}}),patch.object(builder,'boards',return_value={builder.DEFAULT_BUILD_BOARD:row}),patch.object(builder.subprocess,'run',side_effect=compile_only) as run:
                target=builder.build(builder.DEFAULT_BUILD_BOARD,sketch,package=False)
            self.assertEqual(target.name,'application.bin');self.assertEqual(run.call_count,1)
            self.assertFalse(list(root.rglob('bootloader.bin')))
            self.assertFalse(list(root.rglob('*.fwpkg')))

    def test_batch_forwards_bin_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);binary=root/'app.bin';binary.write_bytes(b'1234')
            fake=SimpleNamespace(ROOT=root,build=Mock(return_value=binary))
            report=loader_batch.run(fake,['FLE4D'],'app.ino',lambda _:None,libraries='external',package=False)
            fake.build.assert_called_once_with('FLE4D','app.ino',libraries='external',package=False)
            self.assertEqual(report['rows']['FLE4D']['status'],'success')

    def test_bin_event_never_imports_or_flashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'application.bin';binary.write_bytes(b'1234')
            fake=SimpleNamespace(**{name:Mock() for name in ('_set_idle','refresh_loaders','_refresh_profiles','bin_var','profile_var','_save_settings','build_status','_set_result','_log','_start','notebook')})
            fake.profiles={'fle4d_30mt_ota_block_1_0_1':()}
            importer=Mock()
            manager_extensions.event(fake,'build_bin_complete',dict(path=str(binary),profile='fle4d_30mt_ota_block_1_0_1',board='FLE4D-30MT'),importer)
            fake.bin_var.set.assert_called_once_with(str(binary))
            fake._refresh_profiles.assert_called_once_with('fle4d_30mt_ota_block_1_0_1')
            fake.profile_var.set.assert_not_called()
            importer.assert_not_called();fake._start.assert_not_called()

    def test_bin_event_clears_unrelated_or_hidden_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'application.bin';binary.write_bytes(b'1234')
            fake=SimpleNamespace(**{name:Mock() for name in ('_set_idle','refresh_loaders','_refresh_profiles','bin_var','profile_var','_save_settings','build_status','_set_result','_log','_start')})
            fake.profiles={'other_board':()}
            manager_extensions.event(fake,'build_bin_complete',dict(path=str(binary),profile='hidden',board='FLE4D-30MT'),Mock())
            fake.profile_var.set.assert_called_once_with('')
            fake.bin_var.set.assert_called_once_with(str(binary))
            fake._start.assert_not_called()

    def test_missing_bin_does_not_claim_success(self):
        fake=SimpleNamespace(**{name:Mock() for name in ('_set_idle','refresh_loaders','_set_result','_start')})
        manager_extensions.event(fake,'build_bin_complete',dict(path='C:/absent/fle4d/application.bin'),Mock())
        self.assertIn('не найден',fake._set_result.call_args[0][0]);fake._start.assert_not_called()
