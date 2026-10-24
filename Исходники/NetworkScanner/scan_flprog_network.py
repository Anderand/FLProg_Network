#!/usr/bin/env python3
"""Find devices with common controller/OTA TCP ports on a local network."""
import argparse
import concurrent.futures
import ipaddress
import json
import os
import socket
import subprocess
import sys
import time


PORT_LABELS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    80: "HTTP",
    102: "Siemens S7",
    443: "HTTPS",
    502: "Modbus TCP",
    1883: "MQTT",
    3233: "FLProg OTA",
    4840: "OPC UA",
    8080: "HTTP alternate",
    8443: "HTTPS alternate",
    8883: "MQTT TLS",
    44818: "EtherNet/IP",
    20000: "DNP3",
}
DEFAULT_PORTS = tuple(sorted(PORT_LABELS))


def active_networks():
    """Return active Windows IPv4 networks and addresses without extra packages."""
    if os.name != "nt":
        raise RuntimeError("автоопределение подсети поддерживается в Windows")
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
            capture_output=True, text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError("не удалось прочитать сетевые интерфейсы Windows") from error
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ошибка PowerShell при чтении сети")
    try:
        rows = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError as error:
        raise RuntimeError("Windows вернула некорректный список IPv4-адресов") from error
    if isinstance(rows, dict):
        rows = [rows]

    networks = {}
    local_addresses = set()
    for row in rows:
        try:
            interface = ipaddress.ip_interface(
                "{}/{}".format(row["IPAddress"], int(row["PrefixLength"]))
            )
        except (KeyError, TypeError, ValueError):
            continue
        local_addresses.add(str(interface.ip))
        network = interface.network
        # Avoid unexpectedly sweeping a large corporate/VPN range by default.
        if network.num_addresses > 256:
            network = ipaddress.ip_network("{}/24".format(interface.ip), strict=False)
        if network.num_addresses > 2:
            networks[str(network)] = network
    if not networks:
        raise RuntimeError("не найдена активная IPv4-подсеть")
    return list(networks.values()), local_addresses


def parse_ports(value):
    ports = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            raise ValueError("пустой элемент в списке портов")
        try:
            if "-" in part:
                first_text, last_text = part.split("-", 1)
                first, last = int(first_text), int(last_text)
                if first < 1 or last > 65535 or first > last:
                    raise ValueError
                ports.update(range(first, last + 1))
            else:
                port = int(part)
                if not 1 <= port <= 65535:
                    raise ValueError
                ports.add(port)
        except ValueError as error:
            raise ValueError("неверный порт или диапазон: {}".format(part)) from error
    return tuple(sorted(ports))


def scan(networks, local_addresses, ports, timeout, workers, show_progress=True):
    addresses = []
    for network in networks:
        addresses.extend(
            str(address) for address in network.hosts()
            if str(address) not in local_addresses
        )
    probes = len(addresses) * len(ports)
    if probes > 1_000_000:
        raise RuntimeError(
            "запрошено {:,} проверок; укажи меньшую подсеть или диапазон портов "
            "(лимит 1 000 000)".format(probes).replace(",", " ")
        )

    status = sys.stdout if show_progress else sys.stderr
    print("Подсети: {}".format(", ".join(str(network) for network in networks)),
          file=status)
    print("Проверяю {} узлов x {} TCP-портов...".format(len(addresses), len(ports)),
          file=status)

    def probe(item):
        address, port = item
        try:
            with socket.create_connection((address, port), timeout=timeout):
                return {"ip": address, "port": port,
                        "service": PORT_LABELS.get(port, "TCP")}
        except OSError:
            return None

    results = []
    completed = 0
    last_update = 0.0
    line_width = 0
    started_at = time.monotonic()
    jobs = ((address, port) for address in addresses for port in ports)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        while True:
            batch = []
            try:
                for _ in range(workers * 8):
                    batch.append(next(jobs))
            except StopIteration:
                pass
            if not batch:
                break
            futures = [pool.submit(probe, item) for item in batch]
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                result = future.result()
                if result:
                    results.append(result)
                    if show_progress:
                        status.write("\r" + (" " * line_width) + "\r")
                        message = "Найдено: {}:{} — {}".format(
                            result["ip"], result["port"], result["service"]
                        )
                        print(message, file=status, flush=True)
                        line_width = 0
                now = time.monotonic()
                if show_progress and (now - last_update >= 0.4 or completed == probes):
                    elapsed = now - started_at
                    remaining = (elapsed * (probes - completed) / completed
                                 if completed else 0)
                    eta = "{}м {:02d}с".format(int(remaining // 60),
                                                int(remaining % 60))
                    message = "Прогресс: {:5.1f}% ({}/{}), найдено: {}, осталось ~{}".format(
                        completed * 100.0 / probes if probes else 100.0,
                        completed, probes, len(results), eta,
                    )
                    status.write("\r" + message)
                    status.flush()
                    line_width = len(message)
                    last_update = now

    if show_progress and line_width:
        status.write("\r" + (" " * line_width) + "\r")
        status.flush()

    return sorted(results, key=lambda row: (ipaddress.ip_address(row["ip"]), row["port"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--network", action="append", metavar="CIDR",
        help="подсеть для сканирования; можно указать несколько раз",
    )
    parser.add_argument(
        "--ports", metavar="LIST",
        help="TCP-порты/диапазоны, например 1-1024,3233; по умолчанию — порты контроллеров",
    )
    parser.add_argument("--timeout", type=float, default=0.25,
                        help="таймаут проверки порта в секундах (по умолчанию 0.25)")
    parser.add_argument("--workers", type=int, default=128,
                        help="параллельные проверки (по умолчанию 128)")
    parser.add_argument("--json", action="store_true", help="вывести результаты в JSON")
    args = parser.parse_args()

    if not 0.05 <= args.timeout <= 10:
        parser.error("--timeout должен быть от 0.05 до 10 секунд")
    if not 1 <= args.workers <= 512:
        parser.error("--workers должен быть от 1 до 512")
    try:
        if args.network:
            networks = [ipaddress.ip_network(value, strict=False) for value in args.network]
            _, local_addresses = active_networks()
        else:
            networks, local_addresses = active_networks()
        ports = parse_ports(args.ports) if args.ports else DEFAULT_PORTS
        results = scan(networks, local_addresses, ports, args.timeout, args.workers,
                       show_progress=not args.json)
    except (ValueError, RuntimeError) as error:
        parser.error(str(error))

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    if not results:
        print("Устройств с открытыми проверенными TCP-портами не найдено.")
        return 1

    print("\nIP-АДРЕС       ПОРТ    СЛУЖБА")
    print("-" * 39)
    for row in results:
        print("{:<15} {:<7} {}".format(row["ip"], row["port"], row["service"]))
    hosts = sorted({row["ip"] for row in results}, key=ipaddress.ip_address)
    ota_hosts = sorted({row["ip"] for row in results if row["port"] == 3233},
                       key=ipaddress.ip_address)
    print("\nУстройств с открытыми портами: {}".format(len(hosts)))
    print("Устройств с портом FLProg OTA 3233: {}".format(len(ota_hosts)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nСканирование остановлено.", file=sys.stderr)
        sys.exit(130)
