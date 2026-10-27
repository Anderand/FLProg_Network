"""Build the portable editor. Requires PyInstaller; never installs IDE libraries."""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New directory for the portable EXE folder")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("Output must be a new directory; existing releases are never overwritten")
    with tempfile.TemporaryDirectory(prefix="flprog_editor_") as temporary:
        temporary = Path(temporary)
        data = []
        for name in ("tools", "integration", "runtime", "projects"):
            destination = temporary / name
            shutil.copytree(ROOT / name, destination,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "settings.json"))
            data.append((str(destination), name))
        data.append((str(ROOT / "editor/public"), "public"))
        spec = temporary / "FLProg_WebUI_Editor.spec"
        spec.write_text("a=Analysis([%r],pathex=[%r],binaries=[],datas=%r,hiddenimports=['build_project_package'],hookspath=[],hooksconfig={},runtime_hooks=[],excludes=[],noarchive=False)\n"
                        "pyz=PYZ(a.pure,a.zipped_data)\n"
                        "exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='FLProg_WebUI_Editor',console=False,upx=False)\n"
                        "coll=COLLECT(exe,a.binaries,a.zipfiles,a.datas,name='FLProg_WebUI_Editor',upx=False)\n" %
                        (str(ROOT / "editor/server.py"), str(temporary / "tools"), data), encoding="utf-8")
        subprocess.run([sys.executable, "-m", "PyInstaller", "--distpath", str(output),
                        "--workpath", str(temporary / "build"), str(spec)], check=True)
        scenarios = ROOT / 'examples' / 'preview_scenarios'
        if scenarios.is_dir():
            shutil.copytree(scenarios, output / 'FLProg_WebUI_Editor' / 'Сценарии')
        guide = ROOT / 'specification' / 'PREVIEW_SCENARIOS_RU.md'
        if guide.is_file():
            shutil.copy2(guide, output / 'FLProg_WebUI_Editor' / 'СЦЕНАРИИ.md')
        shutil.copy2(ROOT / 'specification/BUILD_COMPATIBILITY_RU.md',
                     output / 'FLProg_WebUI_Editor' / 'СОВМЕСТИМОСТЬ.md')


if __name__ == "__main__":
    main()
