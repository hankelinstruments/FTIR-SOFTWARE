"""Carga de la base de datos de polímeros y grupos funcionales desde JSON editable.

Sin dependencias de UI: quien llame a load_polymer_db()/load_functional_groups_db()
debe capturar DataLoadError y decidir cómo informar al usuario (ver app/ui/main_window.py).
"""
import json
import shutil

import pandas as pd

from app.config import get_bundled_default_path, get_data_dir


class DataLoadError(Exception):
    pass


def _bootstrap_default_data_file(filename: str) -> None:
    dst = get_data_dir() / filename
    dst.parent.mkdir(parents=True, exist_ok=True)
    src = get_bundled_default_path(filename)
    shutil.copyfile(src, dst)


def _load_json(path, required_top_key: str) -> dict:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if required_top_key not in raw:
        raise DataLoadError(f"{path.name}: falta la clave '{required_top_key}'")
    return raw


def _load_editable_json(filename: str, required_top_key: str) -> dict:
    """Carga la copia editable del laboratorio (data/<filename>), auto-reparando
    si falta el archivo. Propaga DataLoadError si el JSON está corrupto."""
    path = get_data_dir() / filename
    if not path.exists():
        _bootstrap_default_data_file(filename)
    try:
        return _load_json(path, required_top_key)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"{filename} tiene un error de sintaxis JSON: {e}") from e


def _load_default_json(filename: str, required_top_key: str) -> dict:
    """Carga el respaldo de fábrica embebido (solo lectura), usado como fallback
    cuando la copia editable está corrupta."""
    return _load_json(get_bundled_default_path(filename), required_top_key)


def load_polymer_db() -> dict:
    """Puede levantar DataLoadError si data/polymer_db.json está corrupto."""
    return _load_editable_json("polymer_db.json", "polymers")["polymers"]


def load_polymer_db_defaults() -> dict:
    return _load_default_json("polymer_db.json", "polymers")["polymers"]


def load_functional_groups_db() -> pd.DataFrame:
    """Puede levantar DataLoadError si data/functional_groups.json está corrupto."""
    raw = _load_editable_json("functional_groups.json", "functional_groups")["functional_groups"]
    return pd.DataFrame(raw)


def load_functional_groups_db_defaults() -> pd.DataFrame:
    raw = _load_default_json("functional_groups.json", "functional_groups")["functional_groups"]
    return pd.DataFrame(raw)
