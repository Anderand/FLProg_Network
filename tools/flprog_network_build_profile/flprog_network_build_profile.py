#!/usr/bin/env python3
"""Choose FLProg_Network compile profiles from the generated sketch.

This script is called by the ESP8266 platform's prebuild hook.  It writes a
compiler response file and forced-include header inside the current build
directory, so each IDE/Arduino CLI build gets an isolated configuration.
Compatible with the Python 3.7 runtime shipped with FLProg F985.
"""
from __future__ import print_function

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

SOURCE_SUFFIXES = {'.ino', '.cpp', '.c', '.h', '.hpp', '.hh', '.cc', '.cxx', '.ipp'}
SKIP_DIRS = {'.git', '.svn', '.arduino', '.cache', '__pycache__', 'build', 'out',
             'libraries', 'examples', 'backup', 'backups'}

_NETWORK = re.compile(r'\b(?:FLProgNetworkInterface|FLProgOnBoardWifiInterface|'
                      r'FLProgWiznetInterface|FLProgRmiiInterface)\b')
_NETWORK_INCLUDE = re.compile(
    r'^\s*#\s*include\s*[<"](?:flprogNetwork(?:Interface|Profile)?|'
    r'flprogOnBoardWifiInterface|flprogWifiInterface|flprogWiznetInterface|'
    r'flprogW5500Interface|flprogRmiiInterface|flprogEthernetInterface|'
    r'flprogOTA|flprogOtaUniversalBlock)\.h[>"]', re.I | re.M
)
_WIFI_INCLUDE = re.compile(r'^\s*#\s*include\s*[<"](?:flprogOnBoardWifiInterface|'
                           r'flprogWifiInterface)\.h[>"]', re.I | re.M)
_WIRED_INCLUDE = re.compile(r'^\s*#\s*include\s*[<"](?:flprogWiznetInterface|'
                             r'flprogW5500Interface|flprogRmiiInterface|'
                             r'flprogEthernetInterface)\.h[>"]', re.I | re.M)
_RMII_INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]flprogRmiiInterface\.h[>"]', re.I | re.M)
_TYPED_NON_RMII_INCLUDE = re.compile(r'^\s*#\s*include\s*[<"](?:flprogOnBoardWifiInterface|'
                                     r'flprogWifiInterface|flprogWiznetInterface|'
                                     r'flprogW5500Interface)\.h[>"]', re.I | re.M)
_WIFI = re.compile(
    r'\b(?:FLProgOnBoardWifiInterface|FLPROG_NETWORK_MODE_(?:WIFI|BOTH))\b|'
    r'\.(?:setClientSsid|setClientPassword|clientOn|clientOff|'
    r'accessPointOn|accessPointOff|setAccessPointSsid|setAccessPointPassword)\s*\('
)
_WIRED = re.compile(
    r'\b(?:FLProgWiznetInterface|FLProgRmiiInterface|FLProgEthernet|FLProgNetworkOtaWiznet|'
    r'FLPROG_WIZNET_INTERFACE\w*|FLPROG_RMII_INTERFACE\w*|FLPROG_ETHERNET_INTERFACE\w*)\b|'
    r'\bFLPROG_NETWORK_MODE_(?:ETHERNET|BOTH)\b|\.(?:wiznetMode|rmiiMode|setWiznetSpiBackend|'
    r'setPinRST|setSpeedSPI)\s*\('
)
_OTA_TYPE_NAMES = r'(?:FLProgNetworkOta(?:Wiznet|Stm32Wiznet)?|FLProgOTA|FLProgOtaUniversalBlock)'
_OTA_TYPE = re.compile(r'\b' + _OTA_TYPE_NAMES + r'\b')
_GENERIC_NETWORK_DECL = re.compile(
    r'\bFLProgNetworkInterface\s*(?:const\s+)?[*&]?\s*([A-Za-z_]\w*)\s*(?=[;=({,\[])'
)
_TYPED_NON_RMII_DECL = re.compile(
    r'\b(?:FLProgOnBoardWifiInterface|FLProgWiznetInterface)\s+[A-Za-z_]\w*\s*(?:\([^;]*\))?\s*;|'
    r'\bFLPROG_WIZNET_INTERFACE\w*\b'
)
_RMII_DECL = re.compile(r'\bFLProgRmiiInterface\s+[A-Za-z_]\w*|\bFLPROG_RMII_INTERFACE\w*\b')
_OTA_DECL = re.compile(r'\b(?P<type>' + _OTA_TYPE_NAMES +
                       r')\s*(?:const\s+)?[*&]?\s*(?P<name>[A-Za-z_]\w*)\s*(?=[;=({])')
_DHCP_INTERFACE_DECL = re.compile(
    r'\b(?P<type>FLProgWiznetInterface|FLProgNetworkInterface)\s+'
    r'(?P<name>[A-Za-z_]\w*)\s*(?:\([^;{}]*\))?\s*;'
)
_DHCP_INTERFACE_TYPE = re.compile(r'\b(?:FLProgWiznetInterface|FLProgNetworkInterface)\b')
_DHCP_CONTROL_NAMES = {'dhcpMode', 'resetDhcp', 'setDhcp'}
_DHCP_SAFE_METHODS = {
    'dhcpMode', 'resetDhcp', 'setDhcp', 'wiznetMode', 'rmiiMode', 'networkMode',
    'connect', 'begin', 'pool', 'workMode', 'setPinCs', 'setPinRST', 'setSpeedSPI',
    'setSpiPins', 'setClientSsid', 'setClientPassword', 'clientOn', 'clientOff',
    'accessPointOn', 'accessPointOff', 'setAccessPointSsid', 'setAccessPointPassword',
    'localIP', 'gateway', 'subnet', 'dns', 'mac'
}


def _ota_is_used(text):
    for match in _OTA_DECL.finditer(text):
        variable = re.escape(match.group('name'))
        kind = match.group('type')
        methods = ('pool',) if kind == 'FLProgOTA' else ('control',) if kind == 'FLProgOtaUniversalBlock' else ('begin', 'pool')
        if any(re.search(r'\b%s\s*(?:\.|->)\s*%s\s*\(' % (variable, method), text)
               for method in methods):
            return True
    return False


class _CallRecord(object):
    def __init__(self, name, method, argument, start, end):
        self.name = name
        self.method = method
        self.argument = argument
        self._start = start
        self._end = end

    def group(self, index):
        if index == 1:
            return self.argument
        raise IndexError(index)

    def start(self):
        return self._start

    def end(self):
        return self._end


def _parse_member_calls(text, method=None, receiver=None):
    head = re.compile(r'\b([A-Za-z_]\w*)\s*(?:\.|->)\s*([A-Za-z_]\w*)\s*\(')
    calls = []
    for match in head.finditer(text):
        if method is not None and match.group(2) != method:
            continue
        if receiver is not None and match.group(1) != receiver:
            continue
        depth = 1
        index = match.end()
        argument_start = index
        while index < len(text) and depth:
            if text[index] == '(':
                depth += 1
            elif text[index] == ')':
                depth -= 1
            index += 1
        if depth == 0:
            calls.append(_CallRecord(match.group(1), match.group(2),
                                     text[argument_start:index - 1], match.start(), index))
    return calls


def _receiver_calls(text, method):
    return [(call.name, call.argument) for call in _parse_member_calls(text, method=method)]


def _rmii_can_be_disabled(text, source_text):
    if _RMII_DECL.search(text) or _RMII_INCLUDE.search(source_text):
        return False

    generic_matches = list(_GENERIC_NETWORK_DECL.finditer(text))
    generic_names = {match.group(1) for match in generic_matches}
    if 'FLProgNetworkInterface' in text and not generic_names:
        # A reference/type alias without a fully understood owner is ambiguous.
        return False

    rmii_calls = _receiver_calls(text, 'rmiiMode')
    if any(argument.strip().casefold() not in ('false', '0') for _name, argument in rmii_calls):
        return False

    if generic_names:
        # A dynamic base interface can select RMII at runtime. Only disable it
        # when every declared base object is explicitly W5500 and RMII-disabled.
        wiznet_true = {name for name, arg in _receiver_calls(text, 'wiznetMode')
                       if arg.strip().casefold() in ('true', '1')}
        rmii_false = {name for name, arg in rmii_calls if arg.strip().casefold() in ('false', '0')}
        return generic_names.issubset(wiznet_true & rmii_false)

    # Without base objects, only typed Wi-Fi/W5500 declarations are complete
    # evidence that this sketch cannot select RMII.
    return bool(_TYPED_NON_RMII_DECL.search(text) or _TYPED_NON_RMII_INCLUDE.search(source_text))


def _has_dynamic_transport_selection(text):
    known_modes = {'FLPROG_NETWORK_MODE_WIFI', 'FLPROG_NETWORK_MODE_ETHERNET',
                   'FLPROG_NETWORK_MODE_BOTH'}
    for _name, argument in _receiver_calls(text, 'networkMode'):
        if argument.strip() and argument.strip() not in known_modes:
            return True
    for method, valid in (('wiznetMode', {'true', 'false', '0', '1'}),
                          ('rmiiMode', {'true', 'false', '0', '1'})):
        for _name, argument in _receiver_calls(text, method):
            if argument.strip().casefold() not in valid:
                return True
    return False


def _setup_body(text):
    matches = list(re.finditer(r'\bvoid\s+setup\s*\(\s*(?:void\s*)?\)\s*\{', text))
    if len(matches) != 1:
        return None
    opening = text.find('{', matches[0].start())
    depth = 1
    for index in range(opening + 1, len(text)):
        if text[index] == '{':
            depth += 1
        elif text[index] == '}':
            depth -= 1
            if depth == 0:
                return text[opening + 1:index], opening + 1, index
    return None


def _top_level_dhcp_interfaces(text):
    declarations = []
    for match in _DHCP_INTERFACE_DECL.finditer(text):
        depth = 0
        for char in text[:match.start()]:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
        if depth == 0:
            declarations.append(match)
    return declarations


def _member_calls(text, name, method):
    return _parse_member_calls(text, method=method, receiver=name)


def _prove_static_wiznet_dhcp_disabled(text):
    """Prove the narrow direct setup form; ambiguity keeps DHCP enabled."""
    if re.search(r'\b(?:wiznetDhcpClient|FLProgWiznetDhcp)\b', text):
        return None
    declarations = _top_level_dhcp_interfaces(text)
    if not declarations:
        return None

    # Any base/typed W5500 type not in a simple global object declaration can
    # be an alias, pointer, parameter, or dynamically supplied interface.
    covered_types = [(match.start('type'), match.end('type')) for match in declarations]
    for type_match in _DHCP_INTERFACE_TYPE.finditer(text):
        if not any(start <= type_match.start() and type_match.end() <= end
                   for start, end in covered_types):
            return None

    wiznet = [match for match in declarations if match.group('type') == 'FLProgWiznetInterface']
    generic = [match for match in declarations if match.group('type') == 'FLProgNetworkInterface']
    if not wiznet and not generic:
        return None
    setup = _setup_body(text)
    if setup is None:
        return None
    body, body_start, body_end = setup
    if re.search(r'\b(?:if|switch|for|while|do|goto|return)\b|\?|&&|\|\|', body):
        return None
    if re.search(r'^\s*#\s*(?:if|ifdef|ifndef|elif|else)\b', body, re.M):
        return None
    if '{' in body or '}' in body:
        return None

    objects = wiznet + generic
    names = [match.group('name') for match in objects]
    if len(set(names)) != len(names):
        return None

    # Direct access only: aliases, pointers, references, or calls receiving the
    # network object could change DHCP behind the explicit setup setting.
    declaration_spans = [(match.start(), match.end()) for match in declarations]
    for name in names:
        for occurrence in re.finditer(r'\b%s\b' % re.escape(name), text):
            if any(start <= occurrence.start() < end for start, end in declaration_spans):
                continue
            tail = text[occurrence.end():]
            call = re.match(r'\s*(?:\.|->)\s*([A-Za-z_]\w*)\s*\(', tail)
            if not call or call.group(1) not in _DHCP_SAFE_METHODS:
                return None
            if call.group(1) == 'setDhcp':
                return None

    # Require one explicit negative DHCP selection per W5500/generic object.
    # resetDhcp() is the legacy alias for dhcpMode(false); setDhcp() always
    # opts back into runtime DHCP and therefore disqualifies the project.
    disable_positions = {}
    for name in names:
        dhcp_calls = _member_calls(text, name, 'dhcpMode')
        false_calls = [call for call in dhcp_calls
                       if call.group(1).strip().casefold() in ('false', '0')]
        reset_calls = _member_calls(text, name, 'resetDhcp')
        if (_member_calls(text, name, 'setDhcp') or len(dhcp_calls) + len(reset_calls) != 1 or
                len(false_calls) != len(dhcp_calls)):
            return None
        chosen = false_calls + reset_calls
        if len(chosen) != 1 or not (body_start <= chosen[0].start() < body_end):
            return None
        disable_positions[name] = chosen[0].start()

    # Generic base objects must be statically configured as W5500 (not Wi-Fi,
    # RMII, or a runtime-selected transport) before DHCP is disabled.
    for match in generic:
        name = match.group('name')
        wiznet_calls = _member_calls(text, name, 'wiznetMode')
        rmii_calls = _member_calls(text, name, 'rmiiMode')
        mode_calls = _member_calls(text, name, 'networkMode')
        if (len(wiznet_calls) != 1 or wiznet_calls[0].group(1).strip().casefold() not in ('true', '1') or
                len(rmii_calls) != 1 or rmii_calls[0].group(1).strip().casefold() not in ('false', '0') or
                len(mode_calls) != 1 or mode_calls[0].group(1).strip() not in
                ('FLPROG_NETWORK_MODE_ETHERNET', 'FLPROG_NETWORK_MODE_BOTH')):
            return None

    for match in wiznet:
        name = match.group('name')
        wiznet_calls = _member_calls(text, name, 'wiznetMode')
        rmii_calls = _member_calls(text, name, 'rmiiMode')
        mode_calls = _member_calls(text, name, 'networkMode')
        if any(call.group(1).strip().casefold() not in ('true', '1') for call in wiznet_calls):
            return None
        if any(call.group(1).strip().casefold() not in ('false', '0') for call in rmii_calls):
            return None
        if any(call.group(1).strip() and call.group(1).strip() not in
               ('FLPROG_NETWORK_MODE_ETHERNET', 'FLPROG_NETWORK_MODE_BOTH') for call in mode_calls):
            return None

    # DHCP/mode selection must be complete before any activation or work call.
    for name in names:
        disable_at = disable_positions[name]
        mode_calls = (_member_calls(text, name, 'wiznetMode') +
                      _member_calls(text, name, 'rmiiMode') +
                      _member_calls(text, name, 'networkMode'))
        configuration_positions = [disable_at] + [call.start() for call in mode_calls]
        for method in ('connect', 'begin', 'pool', 'clientOn', 'accessPointOn', 'workMode'):
            activations = [call.start() for call in _member_calls(text, name, method)
                           if body_start <= call.start() < body_end]
            if any(any(position > activation for position in configuration_positions)
                   for activation in activations):
                return None
    return 0


def _strip_comments(text):
    """Blank comments without mistaking // and /* inside literals for comments."""
    out = list(text)
    index = 0
    state = 'code'
    quote = ''
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ''
        if state == 'code':
            if char in ('"', "'"):
                state = 'literal'
                quote = char
            elif char == '/' and next_char == '/':
                out[index] = out[index + 1] = ' '
                index += 1
                state = 'line'
            elif char == '/' and next_char == '*':
                out[index] = out[index + 1] = ' '
                index += 1
                state = 'block'
        elif state == 'literal':
            if char == '\\':
                index += 1
            elif char == quote:
                state = 'code'
        elif state == 'line':
            if char not in '\r\n':
                out[index] = ' '
            else:
                state = 'code'
        elif state == 'block':
            if char == '*' and next_char == '/':
                out[index] = out[index + 1] = ' '
                index += 1
                state = 'code'
            elif char not in '\r\n':
                out[index] = ' '
        index += 1
    return ''.join(out)


def _mask_literals(text):
    # C++ raw/normal string and character contents are not active block code.
    text = re.sub(r'R"([^ ()\\\t\r\n]{0,16})\([\s\S]*?\)\1"', ' ', text)
    return re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', ' ', text)


def _source_files(project):
    root = Path(project)
    if root.is_file():
        root = root.parent
    if not root.is_dir():
        raise ValueError('Source path is not a directory: %s' % root)
    for current, dirs, files in os.walk(str(root)):
        dirs[:] = sorted(name for name in dirs if name.casefold() not in SKIP_DIRS)
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix.casefold() in SOURCE_SUFFIXES:
                yield path


def analyze_project(project):
    """Return profile, OTA flag, and evidence from generated source files."""
    texts = []
    scanned = 0
    for path in _source_files(project):
        try:
            text = path.read_text(encoding='utf-8-sig', errors='replace')
        except OSError:
            continue
        scanned += 1
        texts.append(_strip_comments(text))

    # Aggregate before resolving so a declaration in the .ino and use in a
    # helper .cpp still select one project-wide profile.
    source_text = '\n'.join(texts)
    network = bool(_NETWORK_INCLUDE.search(source_text))
    text = _mask_literals(source_text)
    network = network or bool(_NETWORK.search(text) or _OTA_TYPE.search(text))
    wifi = bool(_WIFI.search(text) or _WIFI_INCLUDE.search(source_text))
    wired = bool(_WIRED.search(text) or _WIRED_INCLUDE.search(source_text))
    ota = _ota_is_used(text)
    rmii = 0 if network and _rmii_can_be_disabled(text, source_text) else None
    wiznet_dhcp = _prove_static_wiznet_dhcp_disabled(text)

    dynamic_transport = _has_dynamic_transport_selection(text)
    if not network:
        profile = 0
        ota = False
    elif dynamic_transport:
        profile = 0
    elif wifi and wired:
        profile = 0
    elif wifi:
        profile = 1
    elif wired:
        profile = 2
    else:
        # Preserve the library's universal default when evidence is ambiguous.
        profile = 0
    return {'profile': profile, 'ota': int(bool(ota)), 'rmii': rmii,
            'wiznet_dhcp': wiznet_dhcp,
            'network': network, 'files': scanned}


def _atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        try:
            if path.read_text(encoding='utf-8') == data:
                return False
        except (OSError, UnicodeError):
            pass
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(data)
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def _invalidate_profile_sensitive_cache(build):
    """Drop stale include and object caches when the compile profile changes."""
    build = Path(build)
    for name in ('includes.cache', 'libraries.cache'):
        cached = build / name
        try:
            cached.unlink()
        except FileNotFoundError:
            pass
    # Arduino Builder and Arduino CLI place per-sketch library and sketch
    # objects below these directories. The forced header is a dependency, but
    # older builder cache layers do not consistently track response-file edits.
    for folder_name in ('libraries', 'sketch'):
        folder = build / folder_name
        if not folder.is_dir():
            continue
        for cached in folder.rglob('*'):
            if cached.is_file() and cached.suffix.casefold() in ('.o', '.d', '.a'):
                try:
                    cached.unlink()
                except OSError:
                    pass


def write_build_config(build, selection):
    build = Path(build).resolve()
    build.mkdir(parents=True, exist_ok=True)
    header = build / 'flprog_network_build_profile.h'
    response = build / 'flprog_network_build_profile.rsp'
    header_text = (
        '/* Generated per build path by FLProg_Network profile hook. */\n'
        '#pragma once\n'
        '#ifndef FLPROG_NETWORK_BUILD_PROFILE\n'
        '#define FLPROG_NETWORK_BUILD_PROFILE %d\n'
        '#endif\n'
        '#ifndef FLPROG_NETWORK_COMPILE_OTA\n'
        '#define FLPROG_NETWORK_COMPILE_OTA %d\n'
        '#endif\n' % (selection['profile'], selection['ota'])
    )
    if selection.get('rmii') == 0:
        header_text += '#ifndef FLPROG_NETWORK_COMPILE_RMII\n#define FLPROG_NETWORK_COMPILE_RMII 0\n#endif\n'
    if selection.get('wiznet_dhcp') == 0:
        header_text += ('#ifndef FLPROG_NETWORK_COMPILE_WIZNET_DHCP\n'
                        '#define FLPROG_NETWORK_COMPILE_WIZNET_DHCP 0\n#endif\n')
    changed = _atomic_write(header, header_text)
    include_path = str(header).replace('\\', '/')
    response_text = '-include\n"%s"\n' % include_path
    changed = _atomic_write(response, response_text) or changed
    if changed:
        _invalidate_profile_sensitive_cache(build)
    return response


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='Generated sketch source directory')
    parser.add_argument('--build', required=True, help='Arduino build directory')
    args = parser.parse_args(argv)
    selection = analyze_project(args.source)
    response = write_build_config(args.build, selection)
    print('FLProg_Network profile: %d, compile OTA: %d, source files: %d, response: %s' %
          (selection['profile'], selection['ota'], selection['files'], response))
    return 0


if __name__ == '__main__':
    sys.exit(main())
