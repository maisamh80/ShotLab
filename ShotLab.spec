# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH)
ffmpeg = root / "vendor" / "ffmpeg" / "ffmpeg.exe"
ffprobe = root / "vendor" / "ffmpeg" / "ffprobe.exe"

binaries = []
if ffmpeg.is_file():
    binaries.append((str(ffmpeg), "tools/ffmpeg"))
if ffprobe.is_file():
    binaries.append((str(ffprobe), "tools/ffmpeg"))

a = Analysis(
    ["main.py"],
    pathex=[str(root)],
    binaries=binaries,
    datas=[(str(root / "assets"), "assets")],
    hiddenimports=[
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "PySide6.QtSvg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ShotLab",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=str(root / "assets" / "app-icon.ico"),
    version=str(root / "packaging" / "version_info.txt"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ShotLab",
)
