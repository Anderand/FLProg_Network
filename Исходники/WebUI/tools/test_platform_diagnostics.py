import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PlatformDiagnosticsTest(unittest.TestCase):
 def test_memory_system_contract(self):
  catalog=json.loads((ROOT/'integration/flprog_network_api_catalog.json').read_text(encoding='utf-8'))
  items={x['id']:x for x in catalog['systemParameters']}
  self.assertEqual(items['system_uptime']['type'],'int32')
  for id in ['flash_total','flash_app_capacity','flash_app_used','flash_app_free','ram_total','ram_app_capacity','ram_static_used','ram_available_estimate','ram_used_estimate','ccm_total','ccm_used']:
   self.assertEqual(items[id]['direction'],'publish')
   self.assertEqual(items[id]['type'],'text')
  for id in ['heap_used','heap_arena_free']:
   self.assertNotRegex(items[id]['title'].lower(),r'куча|арена')
  app=(ROOT/'editor/public/app.js').read_text(encoding='utf-8')
  self.assertIn('channelGroup("Системные","№0–100"',app)
  self.assertIn('Автоматически: библиотека → веб',app)
 def test_readonly_and_unknown_simulation(self):
  subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(ROOT/'editor/public/preview-simulator.js')],check=True)
 def test_optional_contract(self):
  catalog=json.loads((ROOT/'integration/flprog_network_api_catalog.json').read_text(encoding='utf-8'))
  items={x['id']:x for x in catalog['systemParameters']}
  for id in ['reset_flags','reset_cause','heap_used','heap_arena_free']:
   self.assertEqual(items[id]['type'],'text');self.assertEqual(items[id]['direction'],'publish')
   self.assertIn('FLProgWebUiPlatformDiagnostics',items[id]['source'])
  h=(ROOT/'runtime/FLProg_WebUI/src/FLProgWebUiPlatformDiagnostics.h').read_text(encoding='utf-8')
  self.assertNotIn('__HAL_RCC_CLEAR_RESET_FLAGS(',h)
  self.assertNotIn('RCC->CSR =',h)
  self.assertIn('FLPROG_WEBUI_DISABLE_PLATFORM_DIAGNOSTICS',h)
  adapter=(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h').read_text(encoding='utf-8')
  self.assertLess(adapter.index('readonlyChannel(channel.c_str())'),adapter.index('api.write('))
if __name__=='__main__':unittest.main()
