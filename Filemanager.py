import json
import os
from pathlib import Path
import pandas as pd

# Base project path pointing to the script root directory
BASE_DIR = Path(__file__).resolve().parent
REQUIRED_DIR = BASE_DIR / "Required"

def get_required_path(filename: str) -> Path:
    """Returns absolute path inside the 'Required' subfolder and ensures directory exists."""
    REQUIRED_DIR.mkdir(parents=True, exist_ok=True)
    return REQUIRED_DIR / filename

def save_json(file_path, data: dict) -> bool:
    """Saves dictionary data to a JSON file safely."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[FILE MANAGER]: Saved -> {path.name}")
        return True
    except Exception as e:
        print(f"[FILE ERROR]: Failed to save JSON '{file_path}': {e}")
        return False

def load_json(file_path) -> dict:
    """Reads JSON configuration into a dictionary."""
    path = Path(file_path)
    if not path.exists():
        print(f"[FILE MANAGER]: '{path.name}' not found.")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FILE ERROR]: Failed to read JSON '{file_path}': {e}")
        return {}