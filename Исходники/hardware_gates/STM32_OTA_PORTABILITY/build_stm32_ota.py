"""Build only; never flash. Uses installed FLProg core and board pin definitions."""
import argparse
import hashlib
import json
import shutil
import subprocess
import struct
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDE = Path(r'C:\F-981\FLProg\ideV8')
CORE = IDE / 'portable/packages/STMicroelectronics/hardware/stm32/3.0.0'
LAYOUTS = {
    1: dict(flash=1048576, offset=65536, capacity=458752, stage=524288),
    2: dict(flash=524288, offset=65536, capacity=196608, stage=262144),
    3: dict(flash=262144, offset=32768, capacity=98304, stage=131072),
    4: dict(flash=524288, offset=32768, capacity=229376, stage=262144),
}

def boards():
    rows = json.loads((ROOT / 'boards_catalog.json').read_text(encoding='utf-8'))
    result = {}
    for row in rows:
        layout = None
        if row['mcu'] == 'STM32F407xx':
            layout = {1048576: 1, 524288: 2}.get(row['flash'])
        elif row['mcu'] == 'STM32F103xE':
            layout = {262144: 3, 524288: 4}.get(row['flash'])
        if layout:
            result[row['board']] = dict(row, layout=layout)
    return result

def install_profiles():
    props = {}
    for line in (CORE / 'boards.txt').read_text(encoding='utf-8-sig').splitlines():
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            props[key] = value
    lines = ['# BEGIN FLPROG STM32 OTA PORTABILITY']
    for board, row in boards().items():
        old = row['family'] + '.menu.pnum.' + board
        new = old + '_OTA_SAFE'
        layout = LAYOUTS[row['layout']]
        lines.append(new + '=' + row['label'] + ' (OTA, hardware validation pending)')
        for key, value in props.items():
            if key.startswith(old + '.'):
                suffix = key[len(old):]
                if suffix in ('.upload.maximum_size', '.build.flash_offset', '.build.extra_flags'):
                    continue
                lines.append(new + suffix + '=' + value)
        lines += [new + '.upload.maximum_size=' + str(layout['capacity']),
                  new + '.build.flash_offset=' + hex(layout['offset']),
                  new + '.build.extra_flags=' + props.get(old + '.build.extra_flags', '') +
                  ' -DFLPROG_STM32_OTA_LAYOUT=' + str(row['layout']) +
                  ' -DFLPROG_OTA_BOARD_' + board + '=1']
    lines.append('# END FLPROG STM32 OTA PORTABILITY')
    path = CORE / 'boards.local.txt'
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    start = text.find(lines[0])
    if start >= 0:
        end = text.index(lines[-1], start) + len(lines[-1])
        text = text[:start] + text[end:]
    path.write_text(text.rstrip() + '\n\n' + '\n'.join(lines) + '\n', encoding='utf-8')
    (ROOT / 'boards_ota_append.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')

def build(board, sketch=None, check_only=False):
    row = boards()[board]
    layout = LAYOUTS[row['layout']]
    boot = sketch is None
    sketch = Path(sketch).resolve() if sketch else ROOT / 'STM32_OTA_BOOTLOADER/STM32_OTA_BOOTLOADER.ino'
    if not sketch.is_file() or sketch.suffix.lower() != '.ino':
        raise ValueError('Select an existing .ino sketch')
    kind = 'bootloader' if boot else ('compile_check_not_for_flashing' if check_only else 'application')
    output = ROOT / 'build' / board / kind
    output.mkdir(parents=True, exist_ok=True)
    fqbn = row['fqbn'] + '_OTA_SAFE'
    command = [str(IDE / 'arduino-builder.exe'), '-compile', '-jobs=4', '-logger=human']
    for folder in [IDE / 'hardware', IDE / 'portable/packages']:
        command += ['-hardware', str(folder)]
    for folder in [IDE / 'tools-builder', IDE / 'hardware/tools/avr', IDE / 'portable/packages']:
        command += ['-tools', str(folder)]
    command += ['-built-in-libraries', str(IDE / 'libraries'), '-libraries',
                str(IDE / 'portable/sketchbook/libraries'), '-fqbn', fqbn,
                '-build-path', str(output), '-prefs', 'compiler.optimization_flags=-Os',
                '-prefs', 'build.flash_offset=' + hex(0 if boot else layout['offset']),
                '-prefs', 'upload.maximum_size=' + str(layout['offset'] if boot else layout['capacity']),
                str(sketch)]
    logs = ROOT / 'logs'
    logs.mkdir(exist_ok=True)
    log_path = logs / (board + '_' + kind + '.log')
    # arduino-builder may clean its build directory when options change.
    # An open log inside that directory prevents cleanup on Windows.
    with log_path.open('w', encoding='utf-8') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        raise RuntimeError('Build failed: ' + str(log_path))
    source = output / (sketch.name + '.bin')
    image = source.read_bytes()
    sp, pc = struct.unpack('<II', image[:8])
    address = 0x08000000 + (0 if boot else layout['offset'])
    limit = layout['offset'] if boot else layout['capacity']
    if (len(image) > limit or sp & 7 or not 0x20000000 < sp <= 0x20000000 + row['ram']
            or not pc & 1 or not address <= (pc & ~1) < address + len(image)):
        raise RuntimeError('Built BIN has an invalid size or vector table for the selected profile')
    dest = ROOT / 'output' / board
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / (kind + '.bin')
    shutil.copy2(source, target)
    target.with_suffix('.sha256').write_text(hashlib.sha256(target.read_bytes()).hexdigest() + '\n')
    info = dict(row, memory=layout, hardware_verified=False, build_kind=kind)
    (dest / (kind + '_build.json')).write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(target), flush=True)
    print(log_path.read_text(encoding='utf-8', errors='replace')[-1500:], flush=True)
    if not boot and not check_only:
        loader = dest / 'bootloader.bin'
        # Rebuild from the same layout sources; never package a stale loader.
        build(board)
        revision = hashlib.sha256(loader.read_bytes() + target.read_bytes()).hexdigest()
        manifest = dict(
            schema_version=1, id=board.lower()[:40] + '_' + revision[:12],
            label=row['label'] + ' OTA / ' + revision[:8] + ' (hardware validation pending)',
            description='W5500 OTA, automatic reset. Network/pins come from the supplied FLProg sketch.',
            target=dict(board=row['label'], mcu=row['mcu'], flash_size=row['flash'],
                        device_id='0x413' if row['layout'] <= 2 else '0x414',
                        hardware_verified=False),
            flash=dict(bootloader_address='0x08000000', bootloader_size=layout['offset'],
                       application_address=hex(0x08000000 + layout['offset']),
                       application_max_size=layout['capacity'],
                       staging_address=hex(0x08000000 + layout['stage']),
                       staging_size=layout['flash'] - layout['stage']),
            ota=dict(protocol='FLPOTA2', port=3233, block_size=1024), artifacts={})
        for name, limit in [('bootloader', layout['offset']), ('application', layout['capacity'])]:
            file = dest / (name + '.bin')
            manifest['artifacts'][name] = dict(file=file.name, max_size=limit,
                sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        with ZipFile(dest / (board + '.fwpkg'), 'w', ZIP_DEFLATED) as archive:
            archive.writestr('profile.json', json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.write(loader, 'bootloader.bin')
            archive.write(target, 'application.bin')
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install-profiles', action='store_true')
    parser.add_argument('--board', choices=sorted(boards()))
    parser.add_argument('--sketch', type=Path, help='Application .ino; omit to build bootloader')
    parser.add_argument('--check-only', action='store_true', help='Do not package the compile-only gate')
    parser.add_argument('--interactive', action='store_true')
    args = parser.parse_args()
    if args.interactive:
        import tkinter as tk
        from tkinter import filedialog
        choices = sorted(boards())
        for index, name in enumerate(choices, 1):
            print('{}: {}'.format(index, boards()[name]['label']))
        number = int(input('Select board number: '))
        if not 1 <= number <= len(choices):
            raise ValueError('Invalid board number')
        args.board = choices[number - 1]
        window = tk.Tk(); window.withdraw()
        args.sketch = filedialog.askopenfilename(title='Select FLProg sketch with OTA block', filetypes=[('Arduino sketch', '*.ino')])
        window.destroy()
        if not args.sketch:
            raise SystemExit('Cancelled')
        args.install_profiles = True
    if args.install_profiles:
        install_profiles()
    if args.board:
        build(args.board, args.sketch, args.check_only)
