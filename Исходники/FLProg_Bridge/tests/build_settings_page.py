"""Generate the ESP Flash settings page from its editable HTML source."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / 'esp32/web/settings.html').read_text(encoding='utf-8-sig')
assert ')FLPSET"' not in html
header = '#pragma once\nstatic const char FLPROG_SETTINGS_PAGE[] PROGMEM=R"FLPSET(' + html + ')FLPSET";\n'
(root / 'esp32/FLProgBridgeEsp32/BridgeSetupPage.h').write_text(header, encoding='utf-8')
