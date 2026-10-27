"""Locations for a user-owned project, separate from the Arduino installation."""
from pathlib import Path

def project_locations(document, default_projects, default_packages):
    project_id = document['project']['id']
    selected = str(document.get('projectFolder') or '').strip()
    if selected:
        folder = Path(selected).expanduser()
        if not folder.is_absolute():
            raise ValueError('Укажите абсолютный путь к папке проекта')
        folder = folder.resolve()
        lowered = str(folder).replace('/', '\\').lower()
        if '\\portable\\sketchbook\\libraries' in lowered:
            raise ValueError('Выберите папку проекта вне libraries Arduino IDE')
        return folder / (project_id + '.flpui'), folder / 'libraries'
    return Path(default_projects) / (project_id + '.flpui'), Path(str(document.get('packageOutput') or default_packages)).resolve()
