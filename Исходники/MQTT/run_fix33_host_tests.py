"""Run actual extracted C++ methods with a fake clock and TCP transport.

Only the platform/adjacent methods are stubbed; methods under test are copied
verbatim from the supplied library. No Arduino hardware or network is used.
"""
import argparse
from pathlib import Path
import re
import subprocess


def method(source, signature):
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('library', type=Path)
    parser.add_argument('--label', default='fix33')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    src = args.library / 'src' / 'service'
    names = ['flprogNetworkHttpClient', 'flprogNetworkHttpServer', 'flprogNetworkMqttClient']
    constants = []
    for name in names:
        header = (src / (name + '.h')).read_text(encoding='utf-8-sig')
        constants.extend(re.findall(r'^#define\s+FLPROG_\w+\s+(?:0x[0-9A-Fa-f]+|[0-9]+)[UL]*\s*$', header, re.M))
    methods = []
    requested = {
        names[0]: ['bool FLProgNetworkHttpClient::parseHexUnsigned(',
                   'void FLProgNetworkHttpClient::processChunkedByte('],
        names[1]: ['void FLProgNetworkHttpServer::updateClient(',
                   'void FLProgNetworkHttpServer::flushResponse(',
                   'void FLProgNetworkHttpServer::queueProtocolError('],
        names[2]: ['bool FLProgNetworkMqttClient::handlePacket(',
                   'bool FLProgNetworkMqttClient::handlePingresp(',
                   'void FLProgNetworkMqttClient::pool('],
    }
    for name, signatures in requested.items():
        source = (src / (name + '.cpp')).read_text(encoding='utf-8-sig')
        methods.extend(method(source, sig) for sig in signatures)
    harness = (here / 'fix33_host_harness.cpp.in').read_text(encoding='utf-8')
    harness = harness.replace('// @CONSTANTS@', '\n'.join(constants))
    harness = harness.replace('// @METHODS@', '\n\n'.join(methods))
    out = here / ('host-' + args.label)
    out.mkdir(exist_ok=True)
    cpp = out / 'tests.cpp'
    cpp.write_text(harness, encoding='utf-8')
    exe = out / 'tests.exe'
    compiler = here / 'host-tools' / 'ziglang' / 'zig.exe'
    subprocess.run([str(compiler), 'c++', '-std=c++11', '-O0', '-Wall', '-Wextra',
                    str(cpp), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], capture_output=True, text=True)
    print(result.stdout, end='')
    print(result.stderr, end='')
    (out / 'results.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
