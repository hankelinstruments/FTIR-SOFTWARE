"""Metadatos de la app, paleta de colores y resolución de rutas (dev vs. exe congelado)."""
import sys
from pathlib import Path

APP_NAME = "Analizador FTIR de Polímeros"
APP_ORG = "Industrial Inspection Service"
APP_VERSION = "1.0.0"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_path() -> Path:
    """Carpeta del .exe (congelado) o raíz del proyecto (dev, carpeta 'FTIR SOFTWARE')."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """Carpeta de datos editable por el laboratorio. Siempre junto al exe/main.py,
    nunca dentro del directorio temporal de extracción de PyInstaller."""
    return get_base_path() / "data"


def get_bundled_default_path(*parts) -> Path:
    """Ruta al respaldo de fábrica de los JSON (solo lectura, usado para auto-reparación)."""
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "data_defaults" / Path(*parts)
    return get_base_path() / "data" / Path(*parts)


def get_assets_path(*parts) -> Path:
    """Recursos estáticos (logo, ícono) - nunca editados por el laboratorio."""
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets" / Path(*parts)
    return get_base_path() / "assets" / Path(*parts)


# Paleta sobria "IIS Industrial"
PALETTE = {
    "bg_primary": "#1B1E23",
    "bg_surface": "#23272E",
    "bg_surface_alt": "#2B303A",
    "border": "#3A3F4B",
    "text_primary": "#E6E8EB",
    "text_secondary": "#9AA1AC",
    "accent": "#3A8FB7",
    "accent_hover": "#4AA6CC",
    "success": "#4CAF6D",
    "warning": "#E0A526",
    "danger": "#D9534F",
}
