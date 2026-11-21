#!/usr/bin/env python3
"""Idempotently install the FLProg_Network build-profile hook in ESP8266 F985."""
from __future__ import print_function

import argparse
import os
import re
import shutil
import tempfile
from pathlib import Path

HOOK_MARKER = '# FLPROG_NETWORK_BUILD_PROFILE_HOOK'
RESPONSE = '"@{build.path}/flprog_network_build_profile.rsp"'
BACKUP_SUFFIX = '.before-flprog-network-profile.bak'


def _atomic_bytes(path, data):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _ensure_response(pattern, key):
    if RESPONSE in pattern:
        return pattern, False
    if '{includes}' not in pattern:
        raise ValueError('Unexpected ESP8266 recipe without {includes}: ' + key)
    return pattern.replace('{includes}', RESPONSE + ' {includes}', 1), True


def _ensure_preprocessor_response(flags):
    if RESPONSE in flags:
        return flags, False
    # Library discovery/preprocessing must see the same profile as compilation;
    # otherwise a stale ArduinoOTA include can remain in the linked file set.
    return flags.rstrip() + ' ' + RESPONSE, True


def install(platform_dir):
    platform_dir = Path(platform_dir).resolve()
    platform_file = platform_dir / 'platform.txt'
    if not platform_file.is_file():
        raise ValueError('ESP8266 platform.txt not found: %s' % platform_file)
    source = Path(__file__).with_name('flprog_network_build_profile.py')
    if not source.is_file():
        raise ValueError('Hook script missing beside installer: %s' % source)
    tools_dir = platform_dir / 'tools'
    tools_dir.mkdir(parents=True, exist_ok=True)
    installed_script = tools_dir / source.name
    shutil.copy2(str(source), str(installed_script))

    original = platform_file.read_bytes()
    backup = Path(str(platform_file) + BACKUP_SUFFIX)
    if not backup.exists():
        shutil.copy2(str(platform_file), str(backup))

    text = original.decode('utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    lines = text.splitlines()
    properties = {}
    for index, line in enumerate(lines):
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            properties[key] = (index, value)

    hook_key = None
    if HOOK_MARKER not in lines:
        hook_key = None
        for number in range(3, 100):
            candidate = 'recipe.hooks.prebuild.%d.pattern' % number
            if candidate not in properties:
                hook_key = candidate
                break
            expected_name = 'flprog_network_build_profile.py'
            if expected_name in properties[candidate][1]:
                hook_key = candidate
                break
        if not hook_key:
            raise ValueError('No free recipe.hooks.prebuild.N slot from 3 to 99.')
        if hook_key in properties and 'flprog_network_build_profile.py' not in properties[hook_key][1]:
            raise ValueError('Prebuild hook key already occupied: ' + hook_key)
        hook_value = ('"{runtime.tools.python3.path}/python3" -I '
                      '"{runtime.platform.path}/tools/flprog_network_build_profile.py" '
                      '--source "{build.source.path}" --build "{build.path}"')
        lines.extend([HOOK_MARKER, hook_key + '=' + hook_value])
        # Arduino Builder and Arduino CLI select the OS-specific property when
        # present. Keep the portable command for Unix hosts and add Windows' .exe.
        lines.append(hook_key + '.windows=' + hook_value.replace('/python3"', '/python.exe"', 1))
    else:
        for line in lines:
            if line.startswith('recipe.hooks.prebuild.') and '.pattern=' in line and 'flprog_network_build_profile.py' in line:
                hook_key = line.split('=', 1)[0]
                break

    changed = False
    preprocessor_key = 'compiler.cpreprocessor.flags'
    if preprocessor_key not in properties:
        raise ValueError('Required ESP8266/ESP32 property missing: ' + preprocessor_key)
    preprocessor_index = properties[preprocessor_key][0]
    prefix, flags = lines[preprocessor_index].split('=', 1)
    flags, did_change = _ensure_preprocessor_response(flags)
    lines[preprocessor_index] = prefix + '=' + flags
    changed = changed or did_change

    for key in ('recipe.c.o.pattern', 'recipe.cpp.o.pattern', 'recipe.S.o.pattern'):
        if key not in properties:
            raise ValueError('Required ESP8266 compile recipe missing: ' + key)
        index = properties[key][0]
        updated, did_change = _ensure_response(lines[index], key)
        lines[index] = updated
        changed = changed or did_change

    output = newline.join(lines) + newline
    encoded = output.encode('utf-8')
    if encoded != original:
        _atomic_bytes(platform_file, encoded)
        changed = True
    return {'platform': str(platform_file), 'script': str(installed_script),
            'backup': str(backup), 'changed': changed}


def uninstall(platform_dir):
    platform_file = Path(platform_dir).resolve() / 'platform.txt'
    backup = Path(str(platform_file) + BACKUP_SUFFIX)
    if not backup.is_file():
        raise ValueError('Original platform backup not found: %s' % backup)
    shutil.copy2(str(backup), str(platform_file))
    script = platform_file.parent / 'tools' / 'flprog_network_build_profile.py'
    try:
        script.unlink()
    except FileNotFoundError:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform-dir', required=True, help='ESP8266 package version directory')
    parser.add_argument('--uninstall', action='store_true', help='Restore the initial platform.txt backup')
    args = parser.parse_args()
    if args.uninstall:
        uninstall(args.platform_dir)
        print('Restored platform.txt from its original backup.')
    else:
        result = install(args.platform_dir)
        print('Hook installed: %s' % result['script'])
        print('Platform: %s' % result['platform'])
        print('Backup: %s' % result['backup'])
        print('Changed: %s' % ('yes' if result['changed'] else 'no'))


if __name__ == '__main__':
    main()
