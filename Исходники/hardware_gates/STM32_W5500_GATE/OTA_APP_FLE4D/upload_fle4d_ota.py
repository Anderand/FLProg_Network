#!/usr/bin/env python3
"""Block uploader for FLProg FLE4D STM32F407/W5500 OTA test."""
import argparse
import hashlib
import hmac
import ipaddress
import json
import os
import socket
import struct
import subprocess
import sys
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MAGIC = b"FLPOTA2\0"
BLOCK = 1024


def receive_exact(sock, length):
    chunks = bytearray()
    while len(chunks) < length:
        part = sock.recv(length - len(chunks))
        if not part:
            raise ConnectionError("контроллер закрыл соединение до ответа")
        chunks.extend(part)
    return bytes(chunks)


def check_ota_ready(host, port=3233, timeout=2.0):
    """Check that the controller accepts a TCP connection on its OTA port."""
    with socket.create_connection((host, port), timeout=timeout):
        return True


def upload_image(host, image, password, port=3233, timeout=30.0,
                 progress_callback=None):
    """Upload a validated FLE4D OTA image and return the number of bytes staged."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 63:
        raise ValueError("пароль должен содержать не более 63 байт")
    if not 8 <= len(image) <= 0x70000:
        raise ValueError("размер образа должен быть от 8 до 458752 байт")

    prefix = MAGIC + struct.pack("<II", len(image), zlib.crc32(image) & 0xFFFFFFFF)
    header_tag = hmac.new(password.encode("utf-8"), prefix, hashlib.sha256).digest()
    image_tag = hmac.new(password.encode("utf-8"), prefix + image, hashlib.sha256).digest()

    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(prefix + header_tag)
        response = receive_exact(sock, 4)
        if response != b"RDY1":
            raise RuntimeError("контроллер отказал перед передачей: {!r}".format(response))

        offset = 0
        while offset < len(image):
            block = image[offset:offset + BLOCK]
            sock.sendall(struct.pack("<H", len(block)) + block)
            accepted = struct.unpack("<I", receive_exact(sock, 4))[0]
            offset += len(block)
            if accepted != offset:
                raise RuntimeError(
                    "неожиданный ACK: ожидалось {}, получено {}".format(offset, accepted)
                )
            if progress_callback:
                progress_callback(offset, len(image))

        sock.sendall(image_tag)
        response = receive_exact(sock, 4)
        if response != b"OKAY":
            raise RuntimeError("проверка/фиксация образа не прошла: {!r}".format(response))
    return len(image)


def local_networks():
    """Read active IPv4 networks from Windows without third-party packages."""
    if os.name != "nt":
        raise RuntimeError("автопоиск подсети сейчас поддерживается в Windows")
    command = (
        "$up = @(Get-NetAdapter | Where-Object Status -eq 'Up' | "
        "Select-Object -ExpandProperty ifIndex); "
        "Get-NetIPAddress -AddressFamily IPv4 -AddressState Preferred | "
        "Where-Object { $_.InterfaceIndex -in $up -and "
        "$_.IPAddress -ne '127.0.0.1' -and $_.IPAddress -notlike '169.254.*' } | "
        "Select-Object IPAddress, PrefixLength | ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            check=False, capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError("не удалось запросить сетевые интерфейсы Windows") from error
    if result.returncode != 0:
        detail = result.stderr.strip() or "не удалось получить сетевые интерфейсы"
        raise RuntimeError(detail)
    try:
        entries = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError as error:
        raise RuntimeError("Windows вернула некорректный список IPv4-сетей") from error
    if isinstance(entries, dict):
        entries = [entries]

    networks = {}
    local_addresses = set()
    for entry in entries:
        try:
            interface = ipaddress.ip_interface(
                "{}/{}".format(entry["IPAddress"], int(entry["PrefixLength"]))
            )
        except (KeyError, ValueError, TypeError):
            continue
        local_addresses.add(str(interface.ip))
        network = interface.network
        # Keep automatic probes bounded to at most 254 addresses per adapter.
        # The full subnet can be supplied explicitly with --network.
        if network.num_addresses > 256:
            network = ipaddress.ip_network(
                "{}/24".format(interface.ip), strict=False
            )
        if network.num_addresses > 2:
            networks[str(network)] = network
    if not networks:
        raise RuntimeError("не найдена активная IPv4-подсеть для сканирования")
    return list(networks.values()), local_addresses


def discover_controller(port, timeout, network_arg=None):
    if network_arg:
        try:
            networks = [ipaddress.ip_network(network_arg, strict=False)]
        except ValueError as error:
            raise RuntimeError("неверная подсеть: {}".format(network_arg)) from error
        _, local_addresses = local_networks()
    else:
        networks, local_addresses = local_networks()

    candidates = []
    for network in networks:
        if network.num_addresses > 4096:
            raise RuntimeError(
                "подсеть слишком большая для сканирования; укажи диапазон /24 через --network"
            )
        candidates.extend(
            str(address) for address in network.hosts()
            if str(address) not in local_addresses
        )
    print("Поиск OTA-контроллера на TCP-порту {} ({} адресов)...".format(
        port, len(candidates)
    ))

    def probe(address):
        try:
            with socket.create_connection((address, port), timeout=timeout):
                return address
        except OSError:
            return None

    with ThreadPoolExecutor(max_workers=64) as pool:
        found = [address for address in pool.map(probe, candidates) if address]
    if not found:
        raise RuntimeError(
            "контроллер не найден; проверь питание, сеть, TCP-порт и укажи --network"
        )
    if len(found) != 1:
        raise RuntimeError(
            "найдено несколько устройств с OTA-портом: {}; укажи IP вручную".format(
                ", ".join(found)
            )
        )
    print("Найден OTA-контроллер: {}".format(found[0]))
    return found[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="IP W5500 или auto для поиска по подсети")
    parser.add_argument("image", help=".bin, собранный профилем FLE4D OTA")
    parser.add_argument("--password", help="тот же ключ, что kOtaPassword в скетче")
    parser.add_argument("--password-file", help="UTF-8 файл с ключом (первая строка)")
    parser.add_argument("--no-password", action="store_true",
                        help="использовать пустой ключ и не читать файл/переменную пароля")
    parser.add_argument("--profile", help="защитная метка профиля платы из boards.local.txt")
    parser.add_argument("--port", type=int, default=3233)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--network", help="подсеть для поиска, например 192.168.100.0/24")
    args = parser.parse_args()

    if args.profile is not None and args.profile != "FLE4D_W5500":
        parser.error("сетевой OTA поддерживается только OTA-профилем FLE4D-30MT/W5500")

    if args.no_password and (args.password is not None or args.password_file):
        parser.error("--no-password нельзя совмещать с --password или --password-file")
    password = "" if args.no_password else args.password
    # Arduino IDE 1.x may leave unknown network TXT placeholders untouched.
    # In that case use the explicit per-user credential file instead.
    if password and password.startswith("{") and password.endswith("}"):
        password = None
    if password is None and args.password_file:
        lines = Path(args.password_file).read_text(encoding="utf-8-sig").splitlines()
        password = lines[0].strip() if lines else ""
    if password is None:
        password = os.environ.get("FLPROG_FLE4D_OTA_PASSWORD")
    if password is None:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            password_path = Path(local_app_data) / "FLProg" / "FLE4D_OTA" / "password.txt"
            if password_path.is_file():
                lines = password_path.read_text(encoding="utf-8-sig").splitlines()
                password = lines[0].strip() if lines else ""
    if password is None:
        password = ""
    if len(password.encode("utf-8")) > 63:
        parser.error("пароль должен содержать не более 63 байт")
    with open(args.image, "rb") as source:
        image = source.read()
    if not 8 <= len(image) <= 0x70000:
        parser.error("размер образа должен быть от 8 до 458752 байт")

    host = args.host
    if host.lower() == "auto":
        host = discover_controller(args.port, min(args.timeout, 0.4), args.network)

    print(f"Подключение к {host}:{args.port}; образ {len(image)} байт")
    upload_image(host, image, password, args.port, args.timeout,
                 progress_callback=lambda sent, total: print(
                     f"Передано {sent}/{total} байт", end="\r", flush=True
                 ))
    print(f"\nОбраз проверен и записан в staging ({len(image)} байт). Перезапустите контроллер.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ConnectionError) as error:
        print(f"Ошибка OTA: {error}", file=sys.stderr)
        sys.exit(1)

