"""Portable profile-based STM32 bootloader installer and OTA uploader."""
from __future__ import print_function

import hashlib
import encodings.idna  # Bundle the codec used by socket hostname resolution.
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import queue
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile


APP_NAME = "FLProg STM32 OTA Manager"
DEFAULT_IP = "192.168.100.22"
DEFAULT_PORT = "3233"
MAX_PACKAGE_FILE = 16 * 1024 * 1024
PACKAGE_FILES = {"profile.json", "bootloader.bin", "application.bin"}

# Reuse the already working FLE4D transfer protocol implementation.
_PROJECT_DIR = Path(__file__).resolve().parent.parent
_UPLOADER_DIR = _PROJECT_DIR / "OTA_APP_FLE4D"
if str(_UPLOADER_DIR) not in sys.path:
    sys.path.insert(0, str(_UPLOADER_DIR))
from upload_fle4d_ota import check_ota_ready, upload_image  # noqa: E402
sys.path.insert(0, str(_PROJECT_DIR.parent / 'STM32_OTA_PORTABILITY'))
from manager_extensions import attach as attach_extensions, event as extension_event
from profile_policy import is_verified, is_visible


def app_directory():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def settings_path():
    return app_directory() / "settings.json"


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().lower()


def validate_application_bin(path, profile):
    path = Path(path).expanduser().resolve()
    if not path.is_file() or path.suffix.lower() != ".bin":
        raise ValueError("Выберите существующий BIN-файл приложения.")
    size = path.stat().st_size
    maximum = int(profile["flash"]["application_max_size"])
    if not 8 <= size <= maximum:
        raise ValueError("Размер BIN должен быть от 8 до {} байт для этого профиля.".format(maximum))
    with path.open("rb") as source:
        stack, reset = struct.unpack("<II", source.read(8))
    address = int(profile["flash"]["application_address"], 0)
    if (stack in (0, 0xFFFFFFFF) or stack % 4 or not (reset & 1) or
            not address <= (reset & ~1) < address + size):
        raise ValueError(
            "BIN не соответствует адресу приложения {}. "
            "Нужен BIN, собранный со смещением OTA для выбранного профиля."
            .format(profile["flash"]["application_address"]))
    return path


def programmer_summary(output):
    """Return a short readable summary instead of the CLI banner/progress bars."""
    def first_match(pattern):
        match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else ""

    return {
        "device": first_match(r"^\s*Device name\s*:\s*(.+)$"),
        "flash": first_match(r"^\s*Flash size\s*:\s*(.+)$"),
        "erase": first_match(r"^\s*(Erasing internal memory .+)$"),
        "elapsed": first_match(r"^\s*Time elapsed during download operation:\s*(.+)$"),
        "verified": "Download verified successfully" in output,
        "errors": [
            line.strip() for line in output.splitlines()
            if re.search(r"error|failed|failure|timeout|no device|cannot connect", line, re.IGNORECASE)
            and not re.search(r"[\u00b1\u042b]{4,}|\b\d+%\b", line)
        ][-8:],
    }


def load_profile(folder):
    folder = Path(folder).resolve()
    manifest_path = folder / "profile.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    profile_id = data.get("id", "")
    if not re.match(r"^[A-Za-z0-9_-]{1,64}$", profile_id):
        raise ValueError("В пакете неверный идентификатор профиля.")
    required = ("label", "target", "flash", "ota", "artifacts")
    if any(key not in data for key in required):
        raise ValueError("В profile.json отсутствуют обязательные поля.")
    artifacts = data["artifacts"]
    resolved = {}
    artifact_keys = ("bootloader",) if data.get("loader_only") is True else ("bootloader", "application")
    for key in artifact_keys:
        entry = artifacts.get(key, {})
        name = entry.get("file", "")
        if name not in PACKAGE_FILES or name == "profile.json":
            raise ValueError("Неверное имя файла {} в профиле.".format(key))
        path = (folder / name).resolve()
        if path.parent != folder or not path.is_file():
            raise ValueError("В пакете отсутствует файл {}.".format(name))
        size = path.stat().st_size
        if size <= 0 or size > MAX_PACKAGE_FILE:
            raise ValueError("Недопустимый размер файла {}.".format(name))
        if sha256_file(path) != entry.get("sha256", "").lower():
            raise ValueError("Контрольная сумма {} не совпала.".format(name))
        if size > int(entry.get("max_size", 0)):
            raise ValueError("{} превышает лимит размера профиля.".format(name))
        resolved[key] = path

    port = int(data["ota"].get("port", 0))
    if not 1 <= port <= 65535:
        raise ValueError("В профиле задан неверный OTA-порт.")
    layout = data["flash"]
    regions = [
        (int(layout["bootloader_address"], 0), int(layout["bootloader_size"])),
        (int(layout["application_address"], 0), int(layout["application_max_size"])),
        (int(layout["staging_address"], 0), int(layout["staging_size"])),
    ]
    flash_end = 0x08000000 + int(data["target"]["flash_size"])
    for start, size in regions:
        if size <= 0 or start < 0x08000000 or start + size > flash_end:
            raise ValueError("Область профиля выходит за пределы Flash контроллера.")
    ordered = sorted(regions)
    if any(a + size > b for (a, size), (b, _) in zip(ordered, ordered[1:])):
        raise ValueError("Области загрузчика, приложения и staging пересекаются.")
    if resolved["bootloader"].stat().st_size > regions[0][1]:
        raise ValueError("Загрузчик превышает выделенную область Flash.")
    if "application" in resolved:
        validate_application_bin(resolved["application"], data)
    return data, resolved


def import_package(archive_path, profiles_dir):
    profiles_dir = Path(profiles_dir).resolve()
    with zipfile.ZipFile(str(archive_path), "r") as archive:
        members = archive.infolist()
        names = set()
        for member in members:
            pure = PurePosixPath(member.filename)
            if (pure.is_absolute() or len(pure.parts) != 1 or
                    pure.name in ("", ".", "..") or "\\" in member.filename):
                raise ValueError("В пакете найден недопустимый путь: {}".format(member.filename))
            if member.file_size > MAX_PACKAGE_FILE:
                raise ValueError("Файл в пакете слишком большой.")
            if member.filename not in PACKAGE_FILES:
                raise ValueError("Неожиданный файл в пакете: {}".format(member.filename))
            names.add(member.filename)
        if names != PACKAGE_FILES:
            raise ValueError("Пакет должен содержать profile.json, bootloader.bin и application.bin.")
        profile_data = json.loads(archive.read("profile.json").decode("utf-8"))
        profile_id = profile_data.get("id", "")
        if not re.match(r"^[A-Za-z0-9_-]{1,64}$", profile_id):
            raise ValueError("В пакете неверный идентификатор профиля.")
        profiles_dir.mkdir(parents=True, exist_ok=True)
        target = profiles_dir / profile_id
        if target.exists():
            installed, _files = load_profile(target)
            identical = all(
                hashlib.sha256(archive.read(name)).hexdigest() ==
                installed["artifacts"][key]["sha256"].lower()
                for key, name in (("bootloader", "bootloader.bin"),
                                  ("application", "application.bin"))
            )
            if identical:
                return target
            raise FileExistsError(
                "Профиль «{}» уже установлен с другой прошивкой. "
                "Для другой версии используйте пакет с отдельным идентификатором."
                .format(installed["label"]))
        staging = profiles_dir / (profile_id + ".importing")
        if staging.exists():
            shutil.rmtree(str(staging))
        staging.mkdir()
        try:
            for name in PACKAGE_FILES:
                payload = archive.read(name)
                if name != "profile.json" and not payload:
                    raise ValueError("В пакете пустой бинарный файл: {}".format(name))
                (staging / name).write_bytes(payload)
            load_profile(staging)
            staging.rename(target)
        except Exception:
            shutil.rmtree(str(staging), ignore_errors=True)
            raise
    return target


class ManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FLProg — менеджер STM32 OTA v0.7.9")
        self.root.geometry("940x680")
        self.root.minsize(820, 600)
        self.events = queue.Queue()
        self.busy = False
        self.settings_file = settings_path()
        self.settings = self._load_settings()
        self.show_unverified = tk.BooleanVar(value=False)
        self.profiles_dir = app_directory() / "profiles"
        self.profiles = {}
        self._build_ui()
        self._refresh_profiles()
        self.root.after(100, self._drain_events)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _load_settings(self):
        try:
            values = json.loads(self.settings_file.read_text(encoding="utf-8"))
            return values if isinstance(values, dict) else {}
        except (OSError, ValueError):
            return {}

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text='Прошивка')
        outer = ttk.Frame(page, padding=14)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(1, weight=1)

        ttk.Label(outer, text="Профиль контроллера:").grid(row=0, column=0, sticky="w", pady=4)
        self.profile_var = tk.StringVar()
        self.profile_box = ttk.Combobox(outer, textvariable=self.profile_var, state="readonly")
        self.profile_box.grid(row=0, column=1, sticky="ew", padx=(10, 8), pady=4)
        self.profile_box.bind("<<ComboboxSelected>>", self._show_profile)
        ttk.Button(outer, text="Импорт пакета…", command=self._import_package).grid(row=0, column=2, sticky="ew", pady=4)

        profile_details = ttk.Frame(outer)
        profile_details.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 10))
        ttk.Checkbutton(profile_details, text="Показать непроверенные платы и профили",
                        variable=self.show_unverified, command=self._toggle_unverified).pack(anchor="w")
        self.profile_info = tk.StringVar(value="Пакеты прошивок не найдены.")
        ttk.Label(profile_details, textvariable=self.profile_info, justify="left", wraplength=800).pack(anchor="w")

        ttk.Separator(outer).grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Label(outer, text="IP контроллера:").grid(row=3, column=0, sticky="w", pady=4)
        self.ip_var = tk.StringVar(value=self.settings.get("ip", DEFAULT_IP))
        ttk.Entry(outer, textvariable=self.ip_var, width=22).grid(row=3, column=1, sticky="w", padx=(10, 8), pady=4)
        ttk.Label(outer, text="Пароль OTA (можно пустой):").grid(row=4, column=0, sticky="w", pady=4)
        self.password_var = tk.StringVar()
        ttk.Entry(outer, textvariable=self.password_var, show="•").grid(row=4, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=4)

        ttk.Label(outer, text="BIN приложения:").grid(row=5, column=0, sticky="w", pady=4)
        self.bin_var = tk.StringVar(value=self.settings.get("application_bin", ""))
        ttk.Entry(outer, textvariable=self.bin_var).grid(row=5, column=1, sticky="ew", padx=(10, 8), pady=4)
        bin_actions = ttk.Frame(outer)
        bin_actions.grid(row=5, column=2, sticky="ew", pady=4)
        ttk.Button(bin_actions, text="Выбрать BIN…", command=self._choose_bin).pack(side="left")
        ttk.Button(bin_actions, text="Из профиля", command=self._use_profile_bin).pack(side="left", padx=(4, 0))

        ttk.Label(outer, text="STM32CubeProgrammer CLI:").grid(row=6, column=0, sticky="w", pady=4)
        self.cli_var = tk.StringVar(value=self.settings.get("programmer", ""))
        ttk.Entry(outer, textvariable=self.cli_var).grid(row=6, column=1, sticky="ew", padx=(10, 8), pady=4)
        ttk.Button(outer, text="Обзор…", command=self._choose_cli).grid(row=6, column=2, sticky="ew", pady=4)

        actions = ttk.Frame(outer)
        actions.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(10, 8))
        for column in range(4):
            actions.columnconfigure(column, weight=1)
        self.check_button = ttk.Button(actions, text="Проверить OTA-порт", command=self._check)
        self.check_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.ota_button = ttk.Button(actions, text="Обновить по OTA", command=self._upload_ota)
        self.ota_button.grid(row=0, column=1, sticky="ew", padx=4)
        self.install_button = ttk.Button(actions, text="Первичная установка по SWD", command=self._install_swd)
        self.install_button.grid(row=0, column=2, sticky="ew", padx=4)
        self.restart_button = ttk.Button(actions, text="Перезапуск по SWD", command=self._restart_swd)
        self.restart_button.grid(row=0, column=3, sticky="ew", padx=(4, 0))

        self.progress = ttk.Progressbar(outer, mode="determinate", maximum=100)
        self.progress.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(2, 8))
        log_actions = ttk.Frame(outer)
        log_actions.grid(row=9, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        self.result_var = tk.StringVar(value="Ожидание операции")
        self.result_label = ttk.Label(log_actions, textvariable=self.result_var, anchor="w")
        self.result_label.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(log_actions, text="Копировать лог", command=self._copy_log).pack(side="right")
        ttk.Button(log_actions, text="Очистить лог", command=self._clear_log).pack(side="right", padx=(0, 6))
        self.log = tk.Text(outer, height=12, wrap="word", state="disabled")
        self.log.grid(row=10, column=0, columnspan=3, sticky="nsew")
        outer.rowconfigure(10, weight=1)
        scrollbar = ttk.Scrollbar(outer, command=self.log.yview)
        scrollbar.grid(row=10, column=3, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)
        ttk.Label(outer, text="Если BIN не выбран, используется приложение из профиля. Для первичной установки нужен ST-Link/SWD.",
                  wraplength=880).grid(row=11, column=0, columnspan=3, sticky="w", pady=(8, 0))
        self._log("Менеджер v0.7.9: по умолчанию доступен проверенный профиль FLE4D-30MT 1.0.1.")
        attach_extensions(self, self.notebook, app_directory())

    def _log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _copy_log(self):
        text = self.log.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update_idletasks()

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _toggle_unverified(self):
        if self.busy:
            self.show_unverified.set(not self.show_unverified.get())
            return
        self._refresh_profiles()
        if hasattr(self, 'refresh_board_choices'):
            self.refresh_board_choices()

    def _refresh_profiles(self, select_id=None):
        previous = self.profile_var.get()
        self.profiles = {}
        self.all_profiles = {}
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        errors = []
        for folder in sorted(self.profiles_dir.iterdir()):
            if not folder.is_dir() or folder.name.endswith(".importing"):
                continue
            try:
                data, files = load_profile(folder)
                self.all_profiles[data["id"]] = (folder, data, files)
                if is_visible(data, self.show_unverified.get()):
                    self.profiles[data["id"]] = (folder, data, files)
            except (OSError, ValueError, KeyError, TypeError) as error:
                errors.append("{}: {}".format(folder.name, error))
        ids = list(self.profiles)
        self.profile_box["values"] = [self.profiles[item][1]["label"] for item in ids]
        if select_id in self.profiles:
            self.profile_var.set(self.profiles[select_id][1]["label"])
        elif ids:
            preferred = self.settings.get("profile")
            preferred = next((key for key in ids if self.profiles[key][1]['label'] == previous), preferred)
            profile_id = preferred if preferred in self.profiles else ids[0]
            self.profile_var.set(self.profiles[profile_id][1]["label"])
        else:
            self.profile_var.set("")
            self.profile_info.set("Нет проверенного профиля. Импортируйте пакет или включите показ непроверенных плат.")
        self._show_profile()
        if previous and previous != self.profile_var.get():
            self.bin_var.set("")
        for error in errors:
            self._log("Пакет пропущен: " + error)

    def _selected(self):
        label = self.profile_var.get()
        for profile_id, item in self.profiles.items():
            if item[1]["label"] == label:
                if not is_visible(item[1], self.show_unverified.get()):
                    raise ValueError("Профиль скрыт. Включите показ непроверенных плат для его выбора.")
                return profile_id, item[0], item[1], item[2]
        raise ValueError("Сначала выберите установленный пакет платы.")

    def _show_profile(self, _event=None):
        try:
            profile_id, _folder, profile, files = self._selected()
        except ValueError:
            return
        flash = profile["flash"]
        target = profile["target"]
        ota = profile["ota"]
        info = (
            "{}\nMCU: {} | Flash: {} KiB | OTA: TCP {}\n"
            "Загрузчик: {} байт → {} | Приложение: {} байт → {}\n"
            "SHA-256 обоих файлов проверен. Профиль: {}"
        ).format(
            profile["description"], target["mcu"], int(target["flash_size"]) // 1024,
            ota["port"], files["bootloader"].stat().st_size,
            flash["bootloader_address"], files["application"].stat().st_size if "application" in files else "нет — выберите BIN проекта",
            flash["application_address"], profile_id,
        )
        self.profile_info.set(info)
        if profile.get("loader_only"):
            self.profile_info.set(info.replace("SHA-256 обоих файлов проверен.", "SHA-256 загрузчика проверен."))
        status = "Проверенный профиль FLE4D-30MT, прошивка 1.0.1." if is_verified(profile) else "НЕ ПРОВЕРЕН НА ПЛАТЕ: используется только для испытаний."
        self.profile_info.set(status + "\n" + self.profile_info.get())

    def _import_package(self):
        filename = filedialog.askopenfilename(
            title="Импорт пакета прошивки", filetypes=(("Пакет FLProg STM32 OTA", "*.fwpkg"), ("ZIP", "*.zip"))
        )
        if not filename:
            return
        try:
            target = import_package(filename, self.profiles_dir)
            self._refresh_profiles(target.name)
            if target.name in self.profiles:
                self._log("Выбран профиль: {}".format(self.profiles[target.name][1]["label"]))
            else:
                self._log("Пакет импортирован, но скрыт. Для его выбора включите «Показать непроверенные платы и профили».")
            self._save_settings()
        except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
            messagebox.showerror("Не удалось импортировать пакет", str(error), parent=self.root)

    def _choose_cli(self):
        path = filedialog.askopenfilename(
            title="Выберите STM32_Programmer_CLI.exe",
            filetypes=(("STM32CubeProgrammer CLI", "STM32_Programmer_CLI.exe"), ("Программы", "*.exe")),
        )
        if path:
            self.cli_var.set(path)
            self._save_settings()

    def _network_inputs(self):
        try:
            host = str(ipaddress.IPv4Address(self.ip_var.get().strip()))
        except ipaddress.AddressValueError:
            raise ValueError("Введите корректный IPv4-адрес.")
        profile_id, folder, profile, files = self._selected()
        password = self.password_var.get()
        if len(password.encode("utf-8")) > 63:
            raise ValueError("Пароль OTA должен занимать не больше 63 байт.")
        self._save_settings(profile_id)
        return host, int(profile["ota"]["port"]), password, profile, files

    def _choose_bin(self):
        filename = filedialog.askopenfilename(
            title="Выберите BIN приложения для OTA",
            filetypes=(("BIN приложения", "*.bin"),),
        )
        if not filename:
            return
        try:
            _profile_id, _folder, profile, _files = self._selected()
            path = validate_application_bin(filename, profile)
        except (OSError, ValueError) as error:
            messagebox.showerror("Проверьте BIN", str(error), parent=self.root)
            return
        self.bin_var.set(str(path))
        self._save_settings()
        self._log("Выбран BIN: {} ({} байт).".format(path.name, path.stat().st_size))

    def _use_profile_bin(self):
        self.bin_var.set("")
        self._save_settings()
        self._log("Используется приложение из выбранного профиля.")

    def _application_files(self, profile, files):
        selected = self.bin_var.get().strip()
        if not selected:
            if "application" not in files:
                raise ValueError("Для этой платы готов загрузчик. Приложение нужно собрать из вашего проекта: «Плата и сборка» → выберите .ino → «Собрать BIN и пакет». Или выберите уже собранный OTA BIN кнопкой «Выбрать BIN…».")
            return files
        result = dict(files)
        result["application"] = validate_application_bin(selected, profile)
        return result

    def _start(self, action):
        if self.busy:
            return
        try:
            params = self._network_inputs()
            if action in ("ota", "swd"):
                params = params[:4] + (self._application_files(params[3], params[4]),)
        except (ValueError, OSError) as error:
            messagebox.showerror("Проверьте данные", str(error), parent=self.root)
            return
        if action == "swd":
            cli = Path(self.cli_var.get().strip())
            if not cli.is_file():
                messagebox.showerror("Нужен STM32CubeProgrammer", "Укажите путь к STM32_Programmer_CLI.exe.", parent=self.root)
                return
            details = params[3]
            answer = messagebox.askyesno(
                "Первичная установка по SWD",
                "Будут записаны загрузчик и приложение профиля:\n{}\n\n"
                "Загрузчик будет записан по адресу {}, приложение — по адресу {}.\n"
                "BIN приложения: {}\n"
                "Подключите ST-Link и убедитесь, что выбрана именно эта плата. Продолжить?".format(
                    details["label"], details["flash"]["bootloader_address"],
                    details["flash"]["application_address"], params[4]["application"].name,
                ), parent=self.root,
            )
            if not answer:
                return
            params = params + (str(cli),)
        self.busy = True
        for button in (self.check_button, self.ota_button, self.install_button, self.restart_button):
            button.configure(state="disabled")
        self.progress.configure(value=0)
        status = {
            "check": "Проверяется доступность OTA-порта…",
            "ota": "Выполняется OTA-передача…",
            "swd": "Идёт первичная установка по SWD…",
            "restart": "Сброс контроллера через ST-Link…",
        }[action]
        self._set_result(status, "#8a5a00")
        threading.Thread(target=self._worker, args=(action, params), daemon=True).start()

    def _check(self):
        self._start("check")

    def _upload_ota(self):
        self._start("ota")

    def _install_swd(self):
        self._start("swd")

    def _restart_swd(self):
        if self.busy:
            return
        cli = Path(self.cli_var.get().strip())
        if not cli.is_file():
            messagebox.showerror("Нужен STM32CubeProgrammer", "Укажите путь к STM32_Programmer_CLI.exe.", parent=self.root)
            return
        if not messagebox.askyesno(
            "Перезапустить контроллер",
            "Контроллер будет сброшен через ST-Link. Flash не стирается и не записывается. Продолжить?",
            parent=self.root,
        ):
            return
        self._save_settings()
        self.busy = True
        for button in (self.check_button, self.ota_button, self.install_button, self.restart_button):
            button.configure(state="disabled")
        self._set_result("Сброс контроллера через ST-Link…", "#8a5a00")
        threading.Thread(target=self._worker, args=("restart", (str(cli),)), daemon=True).start()

    def _worker(self, action, params):
        if action == "restart":
            cli = params[0]
            try:
                self.events.put(("log", "Отправляю команду аппаратного сброса через ST-Link…"))
                result = subprocess.run(
                    [cli, "-c", "port=SWD", "mode=UR", "-rst", "-run"],
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode:
                    output = (result.stdout or "") + (result.stderr or "")
                    details = "\n".join(line.strip() for line in output.splitlines() if line.strip())
                    raise RuntimeError(details[-3000:] or "STM32CubeProgrammer завершился с кодом {}.".format(result.returncode))
                self.events.put(("done", "restart"))
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                self.events.put(("error", str(error)))
            return
        host, port, password, profile, files = params[:5]
        try:
            if action in ("check", "ota"):
                self.events.put(("log", "Проверяю TCP {}:{}…".format(host, port)))
                check_ota_ready(host, port, timeout=3.0)
                self.events.put(("log", "TCP-порт доступен. Это подтверждает только доступность OTA-порта."))
            if action == "check":
                self.events.put(("done", "check"))
                return
            if action == "ota":
                image = files["application"].read_bytes()
                self.events.put(("log", "Отправляю BIN {}: {} байт…".format(files["application"].name, len(image))))
                upload_image(
                    host, image, password, port=port, timeout=45.0,
                    progress_callback=lambda sent, total: self.events.put(("progress", (sent, total))),
                )
                self.events.put(("log", "Образ принят и записан в staging. Прошивка с автоперезапуском установит его автоматически. Для старой прошивки перезапустите контроллер кнопкой или питанием."))
                self.events.put(("done", "ota"))
                return
            cli = params[5]
            flash = profile["flash"]
            device_reported = False
            for title, artifact, address in (
                ("Загрузчик", files["bootloader"], flash["bootloader_address"]),
                ("Приложение", files["application"], flash["application_address"]),
            ):
                size_kib = artifact.stat().st_size / 1024.0
                self.events.put(("log", "Запись {} ({}): {:.1f} KiB по {}…".format(title, artifact.name, size_kib, address)))
                command = [
                    cli, "-c", "port=SWD", "mode=UR", "-w", str(artifact), address,
                    "-v",
                ]
                result = subprocess.run(command, capture_output=True, text=True, timeout=180)
                output = (result.stdout or "") + (result.stderr or "")
                summary = programmer_summary(output)
                if not device_reported and summary["device"]:
                    detail = "Обнаружен {}".format(summary["device"])
                    if summary["flash"]:
                        detail += ", Flash {}".format(summary["flash"])
                    self.events.put(("log", detail + "."))
                    device_reported = True
                if result.returncode or not summary["verified"]:
                    details = "\n".join(summary["errors"])
                    if not details:
                        details = "STM32CubeProgrammer завершился с кодом {} без подтверждения проверки.".format(result.returncode)
                    raise RuntimeError("{}: {}".format(title, details))
                detail = "{}: запись и проверка завершены".format(title)
                if summary["elapsed"]:
                    detail += " за {}".format(summary["elapsed"])
                if summary["erase"]:
                    detail += " ({})".format(summary["erase"].replace("Erasing internal memory ", "стирание "))
                self.events.put(("log", detail + "."))
            self.events.put(("log", "Перезапускаю контроллер после записи…"))
            result = subprocess.run(
                [cli, "-c", "port=SWD", "mode=UR", "-rst", "-run"],
                capture_output=True, text=True, timeout=60,
            )
            output = (result.stdout or "") + (result.stderr or "")
            if result.returncode or "Core run" not in output:
                raise RuntimeError(
                    "Файлы записаны и проверены, но запуск контроллера не подтверждён. "
                    + output[-2000:])
            self.events.put(("log", "Сброс и запуск процессора подтверждены STM32CubeProgrammer."))
            self.events.put(("done", "swd"))
        except (OSError, RuntimeError, ValueError, socket.timeout, ConnectionError, subprocess.SubprocessError) as error:
            self.events.put(("error", str(error)))

    def _drain_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind.startswith('build_') or kind.startswith('scan_'):
                    try:
                        extension_event(self, kind, payload, import_package)
                    except Exception as error:
                        self._set_idle()
                        self._log('Ошибка: ' + str(error))
                        self._set_result('ОШИБКА: ' + str(error), '#b00020')
                        messagebox.showerror('Операция не завершена', str(error), parent=self.root)
                elif kind == "log":
                    self._log(payload)
                elif kind == "progress":
                    sent, total = payload
                    self.progress.configure(value=(100.0 * sent / total) if total else 0)
                elif kind == "error":
                    self._log("Ошибка: " + payload)
                    self._set_result("ОШИБКА: операция не завершена", "#b00020")
                    messagebox.showerror("Операция не завершена", payload, parent=self.root)
                    self._set_idle()
                elif kind == "done":
                    if payload == "ota":
                        self.progress.configure(value=100)
                        result = "УСПЕХ: образ принят. Ожидайте запуска новой версии (старая прошивка требует сброса)."
                    elif payload == "swd":
                        result = "УСПЕХ: запись и проверка завершены; контроллер перезапущен."
                    elif payload == "restart":
                        result = "УСПЕХ: контроллер сброшен через ST-Link; Flash не изменялась."
                    else:
                        result = "Связь есть: OTA-порт доступен; прошивка не отправлялась."
                    self._set_result(result, "#176b2c" if payload != "check" else "#245a9a")
                    self._log("РЕЗУЛЬТАТ: " + result)
                    self._set_idle()
        except queue.Empty:
            pass
        self.root.after(100, self._drain_events)

    def _set_idle(self):
        self.busy = False
        for button in (self.check_button, self.ota_button, self.install_button, self.restart_button):
            button.configure(state="normal")

    def _set_result(self, message, color):
        self.result_var.set(message)
        self.result_label.configure(foreground=color)

    def _save_settings(self, profile_id=None):
        try:
            values = {
                "builder_ide": self.builder_ide_var.get(),
                "builder_sketch": self.builder_sketch_var.get(),
                "builder_libraries": self.builder_libraries_var.get(),
                "ip": self.ip_var.get().strip(),
                "programmer": self.cli_var.get().strip(),
                "application_bin": self.bin_var.get().strip(),
                "profile": profile_id or next(
                    (item for item, value in self.profiles.items()
                     if value[1]["label"] == self.profile_var.get()), ""
                ),
            }
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            self.settings_file.write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _close(self):
        if not self.busy:
            self._save_settings()
            self.root.destroy()


def main():
    root = tk.Tk()
    try:
        ttk.Style(root).theme_use("vista")
    except tk.TclError:
        pass
    app = ManagerApp(root)
    if '--build-all' in sys.argv:
        app.notebook.select(1)
        root.after(500, lambda: app.start_build('all'))
    root.mainloop()


if __name__ == "__main__":
    main()
