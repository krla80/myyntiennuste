from typing import Any
import os, json

def load_json(file_path: str, default: Any = None) -> Any:
    """Lataa JSON-data tiedostosta. Jos tiedostoa ei ole, palauttaa default-arvon."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else []


def save_json(file_path: str, data: Any) -> None:
    """Tallenna data JSON-muodossa tiedostoon."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)