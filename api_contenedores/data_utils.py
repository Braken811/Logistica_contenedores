"""
Utilidades para manejo de datos JSON.
Proyecto: Talento Tech 2026
"""
import json
import os
from typing import List, Dict, Any
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_data(filename: str) -> List[Dict[str, Any]]:
    """Carga datos desde un archivo JSON."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(filename: str, data: List[Dict[str, Any]]) -> None:
    """Guarda datos en un archivo JSON."""
    filepath = DATA_DIR / filename
    DATA_DIR.mkdir(exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_id(data: List[Dict[str, Any]], id_field: str = "id") -> int:
    """Obtiene el próximo ID disponible."""
    if not data:
        return 1
    max_id = max(item.get(id_field, 0) for item in data)
    return max_id + 1