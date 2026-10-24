"""Assemble the first FLE4D profile package and a portable manager release."""
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
GATE_DIR = ROOT.parent
PROFILE_ID = "fle4d_30mt_stm32f407vg_w5500_v1"
LABEL = "FLE4D-30MT / STM32F407VG / W5500 (OTA v1)"
SOURCE_FILES = {
    "bootloader.bin": GATE_DIR / "_build_OTA_FLE4D_BOOTLOADER_FIXED" / "OTA_BOOTLOADER_FLE4D.ino.bin",
    "application.bin": GATE_DIR / "_build_OTA_APP_FLE4D" / "OTA_APP_FLE4D.ino.bin",
}


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main():
    release = ROOT / "portable_v5"
    profile_dir = release / "profiles" / PROFILE_ID
    profile_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, source in SOURCE_FILES.items():
        if not source.is_file():
            raise FileNotFoundError("Build output is missing: {}".format(source))
        target = profile_dir / name
        shutil.copy2(str(source), str(target))
        artifacts["bootloader" if name == "bootloader.bin" else "application"] = {
            "file": name,
            "sha256": digest(target),
            "max_size": 65536 if name == "bootloader.bin" else 458752,
        }

    profile = {
        "schema_version": 1,
        "id": PROFILE_ID,
        "label": LABEL,
        "description": "Экспериментальный профиль; только FLE4D-30MT с STM32F407VG и W5500.",
        "target": {
            "board": "FLProg PLC FLE4D-30MT (W5500 OTA experimental)",
            "mcu": "STM32F407VG",
            "device_id": "0x413",
            "flash_size": 1048576,
            "core": "STMicroelectronics STM32 3.0.0",
        },
        "flash": {
            "bootloader_address": "0x08000000",
            "bootloader_size": 65536,
            "application_address": "0x08010000",
            "application_max_size": 458752,
            "staging_address": "0x08080000",
            "staging_size": 524288,
        },
        "ota": {"protocol": "FLPOTA2", "port": 3233, "block_size": 1024},
        "artifacts": artifacts,
    }
    (profile_dir / "profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    package_dir = release / "packages"
    package_dir.mkdir(parents=True, exist_ok=True)
    for installed in sorted((release / "profiles").iterdir()):
        if not (installed / "profile.json").is_file():
            continue
        package_file = package_dir / (installed.name + ".fwpkg")
        with ZipFile(str(package_file), "w", ZIP_DEFLATED) as archive:
            for name in ("profile.json", "bootloader.bin", "application.bin"):
                archive.write(str(installed / name), name)

    shutil.copy2(str(ROOT / "README_RU.md"), str(release / "README_RU.txt"))
    archive_path = ROOT / "FLProg_STM32_OTA_Manager_FLE4D_portable_v5.zip"
    with ZipFile(str(archive_path), "w", ZIP_DEFLATED) as archive:
        archive.write(str(release / "FLProg_STM32_OTA_Manager.exe"), "FLProg_STM32_OTA_Manager.exe")
        archive.write(str(release / "README_RU.txt"), "README_RU.txt")
        for package_file in sorted(package_dir.glob("*.fwpkg")):
            archive.write(str(package_file), "packages/" + package_file.name)
        for installed in sorted((release / "profiles").iterdir()):
            if not (installed / "profile.json").is_file():
                continue
            for name in ("profile.json", "bootloader.bin", "application.bin"):
                archive.write(str(installed / name), "profiles/{}/{}".format(installed.name, name))
    print("Portable release: {}".format(archive_path))
    print("Profile package: {}".format(package_file))


if __name__ == "__main__":
    main()
