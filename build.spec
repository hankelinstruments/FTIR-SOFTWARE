# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — Analizador FTIR (Industrial Inspection Service).

Compilar con: pyinstaller build.spec

'assets' se empaqueta para lectura interna (logo, icono) via sys._MEIPASS.
'data' se empaqueta como respaldo de fabrica de solo lectura ('data_defaults'),
usado por app/database.py para auto-reparar la copia editable que vive junto
al .exe (dist/data/) - NUNCA se lee directamente la copia editable desde aqui.
"""
datas = [
    ("assets", "assets"),
    ("data", "data_defaults"),
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FTIR_Analyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["assets/icon.ico"],
)
