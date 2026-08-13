"""Genera assets/icon.ico a partir del banner assets/logo_iis.png.

Uso: python tools/generate_icon.py
Script de una sola vez, no se empaqueta en el ejecutable.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "logo_iis.png"
DST = ROOT / "assets" / "icon.ico"

SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main():
    img = Image.open(SRC).convert("RGBA")
    size = max(img.size)
    square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    square.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
    square.save(DST, format="ICO", sizes=SIZES)
    print(f"Generado {DST} ({size}x{size} base, {len(SIZES)} tamaños)")


if __name__ == "__main__":
    main()
