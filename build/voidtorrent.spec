# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for VoidTorrent - produces a standalone Windows .exe."""

import os
from pathlib import Path

root = Path(SPECPATH).resolve().parent if 'SPECPATH' in dir() else Path(__file__).resolve().parent
block_cipher = None

a = Analysis(
    [str(root / "launcher.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[(str(root / "assets" / "voidtorrent.ico"), "assets"),
           (str(root / "assets" / "logo.svg"), "assets")],
    hiddenimports=[
        "voidtorrent.engine",
        "voidtorrent.config",
        "voidtorrent.theme",
        "voidtorrent.utils",
        "voidtorrent.__main__",
        "voidtorrent.ui.main_window",
        "voidtorrent.ui.add_dialog",
        "voidtorrent.ui.options_dialog",
        "libtorrent",
        "PyQt6.QtCore",
        "PyQt6.QtWidgets",
        "PyQt6.QtGui",
        "PyQt6.QtSvg",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "pydoc"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="VoidTorrent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch="x86_64",
    codesign_identity=None,
    entitlements_file=None,
    icon=str(root / "assets" / "voidtorrent.ico"),
)
