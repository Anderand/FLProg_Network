#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static Arduino keyword index audit; independent of Arduino CLI/board toolchain.
Run: python3 tests/check_keywords.py
Does not change library sources or execute firmware.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
KEYWORDS = ROOT / 'keywords.txt'
SOURCES = ROOT / 'src'
ALLOWED = {'KEYWORD1', 'KEYWORD2', 'LITERAL1', 'LITERAL2', 'LITERAL3'}
REQUIRED = {
    'FLPROG_NETWORK_API_LEVEL',
    'FLPROG_NETWORK_HAS_TYPED_DEVICE_LOOKUP',
    'FLPROG_NETWORK_HAS_TYPED_DEVICE_EXISTS',
    'FLProgNetworkDeviceKind',
    'FLProgNetworkDeviceRegistryResult',
    'getWiznet', 'getWifi', 'existsWiznet', 'existsWifi',
    'FLPROG_NETWORK_DEVICE_TYPE_MISMATCH',
    'FLPROG_NETWORK_DEVICE_INVALID',
    'setPinRST', 'setSpeedSPI', 'setWiznetPoolFactory',
    'FLProgEthernetResetMode', 'FLPROG_ETH_RESET_MANAGED',
    'ethBindRtHw', 'ethSetReset', 'ethSetSpiSpeed', 'ethSetStartupDelay',
    'FLPROG_NETWORK_HAS_RT_HW_BASE', 'FLPROG_NETWORK_RT_HW_AUTO',
    'transportIdentityForRoute', 'transportByIdentity',
}


def run():
    problems = []
    source_text = '\n'.join(
        p.read_text(encoding='utf-8', errors='replace')
        for p in SOURCES.rglob('*') if p.suffix in {'.cpp', '.h', '.hpp'}
    )
    # Remove comments to avoid accidentally validating keyword names from prose.
    source_text = re.sub(r'/\*.*?\*/|//[^\r\n]*', ' ', source_text, flags=re.S)
    seen = {}
    for lineno, line in enumerate(KEYWORDS.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        cells = line.split('\t')
        if len(cells) != 2:
            problems.append(f'line {lineno}: need one real TAB, got {line!r}')
            continue
        name, group = cells
        if not re.fullmatch(r'[A-Za-z_]\w*', name):
            problems.append(f'line {lineno}: invalid identifier {name!r}')
        if group not in ALLOWED:
            problems.append(f'line {lineno}: invalid group {group!r}')
        if name in seen:
            problems.append(f'line {lineno}: duplicate {name!r}, first at {seen[name]}')
        seen[name] = lineno
        if not re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', source_text):
            problems.append(f'line {lineno}: {name!r} is not present in code')
    for missing in sorted(REQUIRED - set(seen)):
        problems.append(f'missing expected keyword: {missing}')
    if problems:
        print('KEYWORDS FAIL:', *problems, sep='\n- ', file=sys.stderr)
        return 1
    print(f'KEYWORDS PASS: {len(seen)} unique entries, valid tabs and groups, '
          'all names present in C++ source, required API indexed')
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
