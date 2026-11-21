import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('flprog_network_build_profile', HERE / 'flprog_network_build_profile.py')
profile_hook = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile_hook)
INSTALL_SPEC = importlib.util.spec_from_file_location('install_hook', HERE / 'install_hook.py')
install_hook = importlib.util.module_from_spec(INSTALL_SPEC)
INSTALL_SPEC.loader.exec_module(install_hook)


class ProfileDetectionTests(unittest.TestCase):
    def _project(self, files):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for name, text in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        return temp, root

    def test_legacy_project_uses_library_defaults(self):
        temp, root = self._project({'Legacy.ino': '#include <Ethernet.h>\nEthernet.begin(mac);\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['profile'], 0)
            self.assertEqual(profile_hook.analyze_project(root)['ota'], 0)
        finally:
            temp.cleanup()

    def test_wifi_only_profile(self):
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network;\nvoid setup(){network.setClientSsid("x"); network.clientOn();}\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['profile'], 1)
        finally:
            temp.cleanup()

    def test_native_generator_wifi_interface_include_selects_wifi_profile(self):
        temp, root = self._project({'NativeWifi.ino': '#include <flprogOnBoardWifiInterface.h>\n'
            'FLProgOnBoardWifiInterface wifi;\n'
            'void setup(){wifi.setClientSsid("ssid"); wifi.setClientPassword("pass"); wifi.clientOn();}\n'})
        try:
            result = profile_hook.analyze_project(root)
            self.assertEqual((result['profile'], result['ota'], result['rmii']), (1, 0, 0))
        finally:
            temp.cleanup()

    def test_native_generator_wifi_header_variants_are_not_string_matches(self):
        for header in ('flprogOnBoardWifiInterface.h', 'flprogWifiInterface.h'):
            temp, root = self._project({'NativeWifi.ino': '#include <%s>\n' % header})
            try:
                result = profile_hook.analyze_project(root)
                self.assertEqual((result['profile'], result['rmii']), (1, 0))
            finally:
                temp.cleanup()

    def test_wired_only_profile(self):
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network;\nvoid setup(){network.networkMode(FLPROG_NETWORK_MODE_ETHERNET); network.wiznetMode(true);}\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['profile'], 2)
        finally:
            temp.cleanup()

    def test_typed_wifi_and_w5500_disable_rmii(self):
        cases = [
            ('Wifi.ino', '#include <flprogNetwork.h>\nFLProgOnBoardWifiInterface wifi;\n'),
            ('W5500.ino', '#include <flprogNetwork.h>\nFLProgWiznetInterface ethernet;\n'),
        ]
        for name, source in cases:
            temp, root = self._project({name: source})
            try:
                result = profile_hook.analyze_project(root)
                self.assertEqual(result['rmii'], 0)
                with tempfile.TemporaryDirectory() as build_temp:
                    profile_hook.write_build_config(build_temp, result)
                    self.assertIn('FLPROG_NETWORK_COMPILE_RMII 0',
                                  (Path(build_temp) / 'flprog_network_build_profile.h').read_text())
            finally:
                temp.cleanup()

    def test_wiznet_true_and_rmii_false_disable_rmii_but_dynamic_case_stays_universal(self):
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network;\n'
            'void setup(){network.wiznetMode(true); network.rmiiMode(false);}\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['rmii'], 0)
        finally:
            temp.cleanup()
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network;\nvoid setup(){network.wiznetMode(mode);}\n'})
        try:
            self.assertIsNone(profile_hook.analyze_project(root)['rmii'])
        finally:
            temp.cleanup()

    def test_partial_generic_wiznet_pairs_and_later_rmii_enable_keep_rmii(self):
        cases = [
            'FLProgNetworkInterface a; FLProgNetworkInterface b; '
            'void setup(){a.wiznetMode(true); a.rmiiMode(false); b.rmiiMode(true);}',
            'FLProgNetworkInterface a; FLProgNetworkInterface b; '
            'void setup(){a.wiznetMode(true); a.rmiiMode(false);}',
            'FLProgNetworkInterface *a; void setup(){a->wiznetMode(true); a->rmiiMode(false); a->rmiiMode(true);}',
        ]
        for body in cases:
            temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n' + body})
            try:
                self.assertIsNone(profile_hook.analyze_project(root)['rmii'])
            finally:
                temp.cleanup()

    def test_dynamic_numeric_network_mode_with_wifi_stays_universal(self):
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network;\n'
            'void setup(){network.setClientSsid("ssid"); network.networkMode(1);}\n'})
        try:
            result = profile_hook.analyze_project(root)
            self.assertEqual(result['profile'], 0)
        finally:
            temp.cleanup()

    def test_rmii_and_wifi_wired_dynamic_keep_rmii(self):
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network; FLProgRmiiInterface rmii;\n'
            'void setup(){network.networkMode(FLPROG_NETWORK_MODE_BOTH);}\n'})
        try:
            self.assertIsNone(profile_hook.analyze_project(root)['rmii'])
        finally:
            temp.cleanup()

    def test_legacy_and_universal_ota_forms_enable_compile_ota(self):
        cases = [
            ('Legacy.ino', '#include <flprogOTA.h>\nFLProgOTA ota;\nvoid loop(){ota.pool();}\n'),
            ('Universal.ino', '#include <flprogOtaUniversalBlock.h>\n'
             'FLProgOtaUniversalBlock flprogOtaUniversal;\n'
             'void loop(){flprogOtaUniversal.control(EN, NET_NUM, PASSWORD);}\n'),
        ]
        for name, source in cases:
            temp, root = self._project({name: source})
            try:
                self.assertEqual(profile_hook.analyze_project(root)['ota'], 1)
            finally:
                temp.cleanup()

    def test_strings_vendored_libraries_examples_and_backups_do_not_select_blocks(self):
        temp, root = self._project({
            'Main.ino': '#include <flprogNetwork.h>\nFLProgOnBoardWifiInterface wifi;\n'
                'void setup(){Serial.println(".clientOn() https://example.test FLProgNetworkOta ota; ota.begin(network)");}\n',
            'libraries/FLProg_Network/src/old.cpp': 'FLProgNetworkInterface net; FLProgRmiiInterface rmii;\n'
                'FLProgNetworkOta ota; void f(){ota.begin(net);}\n',
            'examples/Example.cpp': 'FLProgNetworkInterface net; FLProgNetworkOta ota; void f(){ota.begin(net);}\n',
            'backup/Old.cpp': 'FLProgNetworkInterface net; FLProgNetworkOta ota; void f(){ota.begin(net);}\n',
        })
        try:
            result = profile_hook.analyze_project(root)
            self.assertEqual((result['profile'], result['ota'], result['rmii']), (1, 0, 0))
        finally:
            temp.cleanup()

    def test_static_w5500_unconditional_setup_false_enables_wiznet_dhcp_stub(self):
        temp, root = self._project({'StaticW5500.ino': '#include <flprogNetwork.h>\n'
            'FLProgWiznetInterface network(5);\n'
            'void setup(){network.dhcpMode(false); network.connect();}\n'
            'void loop(){network.pool();}\n'})
        try:
            result = profile_hook.analyze_project(root)
            self.assertEqual(result['wiznet_dhcp'], 0)
            with tempfile.TemporaryDirectory() as build:
                profile_hook.write_build_config(build, result)
                header = (Path(build) / 'flprog_network_build_profile.h').read_text()
                self.assertIn('FLPROG_NETWORK_COMPILE_WIZNET_DHCP 0', header)
        finally:
            temp.cleanup()

    def test_reset_dhcp_legacy_alias_is_static_false(self):
        temp, root = self._project({'StaticW5500.ino': '#include <flprogNetwork.h>\n'
            'FLProgWiznetInterface network;\n'
            'void setup(){network.resetDhcp(); network.connect();}\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['wiznet_dhcp'], 0)
        finally:
            temp.cleanup()

    def test_two_static_w5500_interfaces_are_all_covered(self):
        temp, root = self._project({'StaticW5500.ino': '#include <flprogNetwork.h>\n'
            'FLProgWiznetInterface a(5); FLProgWiznetInterface b(15);\n'
            'void setup(){a.dhcpMode(false); b.resetDhcp(); a.connect(); b.connect();}\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['wiznet_dhcp'], 0)
        finally:
            temp.cleanup()

    def test_two_generic_w5500_interfaces_require_static_selection_and_dhcp_off(self):
        complete = ('#include <flprogNetwork.h>\nFLProgNetworkInterface a; FLProgNetworkInterface b;\n'
            'void setup(){a.networkMode(FLPROG_NETWORK_MODE_ETHERNET); a.wiznetMode(true); a.rmiiMode(false); a.dhcpMode(false); '
            'b.networkMode(FLPROG_NETWORK_MODE_BOTH); b.wiznetMode(true); b.rmiiMode(false); b.dhcpMode(false); a.connect(); b.connect();}\n')
        incomplete = complete.replace('b.dhcpMode(false); ', '')
        for body, expected in ((complete, 0), (incomplete, None)):
            temp, root = self._project({'GenericW5500.ino': body})
            try:
                self.assertEqual(profile_hook.analyze_project(root)['wiznet_dhcp'], expected)
            finally:
                temp.cleanup()

    def test_wifi_and_rmii_only_dhcp_settings_keep_wiznet_dhcp(self):
        cases = [
            '#include <flprogNetwork.h>\nFLProgOnBoardWifiInterface wifi;\n'
            'void setup(){wifi.dhcpMode(false);}\n',
            '#include <flprogNetwork.h>\nFLProgRmiiInterface rmii;\n'
            'void setup(){rmii.dhcpMode(false);}\n',
        ]
        for source in cases:
            temp, root = self._project({'Network.ino': source})
            try:
                self.assertIsNone(profile_hook.analyze_project(root)['wiznet_dhcp'])
            finally:
                temp.cleanup()

    def test_w5500_static_proof_does_not_disable_wifi_dhcp(self):
        temp, root = self._project({'Mixed.ino': '#include <flprogNetwork.h>\n'
            'FLProgOnBoardWifiInterface wifi; FLProgWiznetInterface wired(5);\n'
            'void setup(){wired.dhcpMode(false); wired.connect(); wifi.clientOn();}\n'})
        try:
            result = profile_hook.analyze_project(root)
            self.assertEqual(result['wiznet_dhcp'], 0)
            self.assertEqual(result['profile'], 0)
        finally:
            temp.cleanup()

    def test_conditional_late_or_dynamic_dhcp_selection_keeps_wiznet_dhcp(self):
        cases = [
            'if (needStatic) network.dhcpMode(false);',
            'network.connect(); network.dhcpMode(false);',
            'network.dhcpMode(false); network.dhcpMode(getDhcpMode());',
        ]
        for statement in cases:
            temp, root = self._project({'Network.ino': '#include <flprogNetwork.h>\n'
                'FLProgWiznetInterface network;\nvoid setup(){%s}\n' % statement})
            try:
                self.assertIsNone(profile_hook.analyze_project(root)['wiznet_dhcp'])
            finally:
                temp.cleanup()

    def test_external_access_switch_and_dynamic_dhcp_client_keep_wiznet_dhcp(self):
        cases = [
            'network.dhcpMode(false); configure(network);',
            'network.dhcpMode(false); network.setDhcp();',
            'network.dhcpMode(false); network.wiznetDhcpClient().reset();',
        ]
        for statement in cases:
            temp, root = self._project({'Network.ino': '#include <flprogNetwork.h>\n'
                'FLProgWiznetInterface network;\nvoid setup(){%s}\n' % statement})
            try:
                self.assertIsNone(profile_hook.analyze_project(root)['wiznet_dhcp'])
            finally:
                temp.cleanup()

    def test_wifi_wired_and_ota_across_translation_units(self):
        temp, root = self._project({
            'Main.ino': '#include <flprogNetwork.h>\nFLProgNetworkInterface network;\nFLProgNetworkOta ota;\n'
                'void setup(){network.setClientSsid("x"); network.wiznetMode(true); network.networkMode(FLPROG_NETWORK_MODE_BOTH);}\n',
            'src/ota.cpp': 'void startOta(){ ota.begin(network); }\n'})
        try:
            result = profile_hook.analyze_project(root)
            self.assertEqual((result['profile'], result['ota']), (0, 1))
        finally:
            temp.cleanup()

    def test_comment_does_not_enable_ota(self):
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network;\n// FLProgNetworkOta ota; ota.begin(network);\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['ota'], 0)
        finally:
            temp.cleanup()

    def test_unrelated_begin_does_not_enable_unused_ota_object(self):
        temp, root = self._project({'Main.ino': '#include <flprogNetwork.h>\n'
            'FLProgNetworkInterface network; FLProgNetworkOta ota;\n'
            'void setup(){network.begin();}\n'})
        try:
            self.assertEqual(profile_hook.analyze_project(root)['ota'], 0)
        finally:
            temp.cleanup()

    def test_each_build_path_gets_independent_and_updated_response(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_a = root / 'build A'
            build_b = root / 'build B'
            first = {'profile': 1, 'ota': 0}
            second = {'profile': 0, 'ota': 1}
            response_a = profile_hook.write_build_config(build_a, first)
            response_b = profile_hook.write_build_config(build_b, second)
            self.assertNotEqual(response_a, response_b)
            self.assertIn('FLPROG_NETWORK_BUILD_PROFILE 1', (build_a / 'flprog_network_build_profile.h').read_text())
            self.assertIn('FLPROG_NETWORK_COMPILE_OTA 1', (build_b / 'flprog_network_build_profile.h').read_text())
            # A subsequent build with removed OTA blocks must rewrite the old build path.
            profile_hook.write_build_config(build_b, {'profile': 1, 'ota': 0})
            self.assertIn('FLPROG_NETWORK_COMPILE_OTA 0', (build_b / 'flprog_network_build_profile.h').read_text())
            self.assertIn('"', response_b.read_text())

    def test_profile_change_invalidates_library_and_sketch_objects_but_keeps_core_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            build = Path(temp)
            profile_hook.write_build_config(build, {'profile': 1, 'ota': 1, 'rmii': None})
            stale = [build / 'includes.cache', build / 'libraries.cache',
                     build / 'libraries' / 'ArduinoOTA' / 'ArduinoOTA.cpp.o',
                     build / 'libraries' / 'ArduinoOTA' / 'ArduinoOTA.cpp.d',
                     build / 'libraries' / 'ArduinoOTA' / 'ArduinoOTA.a',
                     build / 'sketch' / 'main.cpp.o', build / 'sketch' / 'main.cpp.d']
            for path in stale:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('stale', encoding='utf-8')
            core = build / 'core' / 'core.a'
            core.parent.mkdir(parents=True)
            core.write_text('keep', encoding='utf-8')
            self.assertTrue(all(path.exists() for path in stale))
            profile_hook.write_build_config(build, {'profile': 1, 'ota': 0, 'rmii': None})
            self.assertTrue(all(not path.exists() for path in stale))
            self.assertTrue(core.exists())

    def test_installer_is_idempotent_and_restores_original_platform(self):
        original = ('compiler.c.extra_flags=-DKEEP_C=1\n'
                    'compiler.cpreprocessor.flags=-DKEEP_PREPROCESSOR=1\n'
                    'recipe.hooks.prebuild.2.pattern=python existing.py\n'
                    'recipe.c.o.pattern=cc {compiler.c.extra_flags} {includes} source.c\n'
                    'recipe.cpp.o.pattern=c++ {compiler.cpp.extra_flags} {includes} source.cpp\n'
                    'recipe.S.o.pattern=cc {compiler.S.extra_flags} {includes} source.S\n')
        with tempfile.TemporaryDirectory() as temp:
            platform = Path(temp) / 'platform'
            (platform / 'tools').mkdir(parents=True)
            (platform / 'platform.txt').write_text(original, encoding='utf-8')
            result = install_hook.install(platform)
            self.assertTrue(result['changed'])
            patched = (platform / 'platform.txt').read_text(encoding='utf-8')
            self.assertIn('compiler.c.extra_flags=-DKEEP_C=1', patched)
            self.assertIn('compiler.cpreprocessor.flags=-DKEEP_PREPROCESSOR=1 "@{build.path}/flprog_network_build_profile.rsp"', patched)
            self.assertIn('recipe.hooks.prebuild.3.pattern=', patched)
            self.assertIn('recipe.hooks.prebuild.3.pattern.windows=', patched)
            self.assertIn('"@{build.path}/flprog_network_build_profile.rsp"', patched)
            self.assertFalse(install_hook.install(platform)['changed'])
            self.assertEqual(Path(result['backup']).read_text(encoding='utf-8'), original)
            install_hook.uninstall(platform)
            self.assertEqual((platform / 'platform.txt').read_text(encoding='utf-8'), original)


if __name__ == '__main__':
    unittest.main()
