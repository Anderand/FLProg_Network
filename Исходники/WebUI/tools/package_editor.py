"""Build a self-contained source distribution; preserve existing user projects."""
import argparse
import shutil
from pathlib import Path

def package(destination):
    root = Path(__file__).resolve().parents[1]
    destination = Path(destination)
    files = [(root / "editor" / name, destination / name) for name in
             ("server.py", "Start_Editor.bat", "launch_editor.cmd", "README_RU.md")]
    for folder in ("public",):
        files.extend((p, destination / p.relative_to(root / "editor")) for p in (root / "editor" / folder).rglob("*") if p.is_file())
    for folder in ("tools", "integration", "projects"):
        files.extend((p, destination / p.relative_to(root)) for p in (root / folder).glob("*") if p.is_file() and p.suffix in (".py", ".json", ".flpui"))
    for source, target in files:
        if "projects" in target.relative_to(destination).parts and target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(target))
    return destination

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    print(package(parser.parse_args().destination))
