#!/usr/bin/env python3
"""ESP8266 regression: stand-alone OTA .cpp must not rely on a sketch's includes.

This is a host compiler test with deliberately minimal Arduino/IPAddress stubs,
not an ESP8266 core or hardware compilation.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
header = root / 'src/service/flprogNetworkOtaWiznet.h'
source = root / 'src/service/flprogNetworkOtaWiznet.cpp'
text = header.read_text(encoding='utf-8')
assert '#include <IPAddress.h>' in text, 'OTA header must include IPAddress itself'
assert text.count('IPAddress _host;') == 1
assert source.exists()

with tempfile.TemporaryDirectory(prefix='flprog_ota_8266_') as d:
    mock = Path(d)
    # Simulates Arduino.h without an implicit IPAddress declaration.
    (mock / 'Arduino.h').write_text(
        '#pragma once\n#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n',
        encoding='utf-8',
    )
    (mock / 'IPAddress.h').write_text(
        '#pragma once\n#include <stdint.h>\n'
        'class IPAddress { public: IPAddress() {} };\n',
        encoding='utf-8',
    )
    for compiler in ('g++', 'clang++'):
        if not shutil.which(compiler):
            continue
        cmd = [compiler, '-std=c++11', '-Wall', '-Wextra', '-Werror',
               '-Wno-unused-private-field', '-fno-rtti', '-fno-exceptions',
               '-DESP8266', '-I', str(mock), '-fsyntax-only', str(source)]
        subprocess.run(cmd, check=True)
        print(f'ESP8266_OTA_HEADER_STANDALONE_PASS compiler={compiler}', flush=True)
print('ESP8266_OTA_HEADER_TEST_PASS')
