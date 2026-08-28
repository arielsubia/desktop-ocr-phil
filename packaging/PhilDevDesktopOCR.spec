# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Phil Dev Desktop OCR.

Build from the project root:
    pyinstaller packaging/PhilDevDesktopOCR.spec
"""

from pathlib import Path

# When PyInstaller executes a spec, __file__ is not defined; SPECPATH is.
SPEC_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_DIR.parent
ASSETS = PROJECT_ROOT / "src" / "phildev_ocr" / "assets"

a = Analysis(
    [str(PROJECT_ROOT / "src" / "phildev_ocr" / "__main__.py")],
    pathex=[str(PROJECT_ROOT / "src")],
    binaries=[],
    datas=[
        (str(ASSETS / "logo-phildev.png"), "phildev_ocr/assets"),
        (str(ASSETS / "logo-phildev.ico"), "phildev_ocr/assets"),
    ],
    hiddenimports=["pynput.keyboard._win32", "pynput.mouse._win32"],
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
    a.binaries,
    a.datas,
    [],
    name="PhilDevDesktopOCR",
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
    icon=str(ASSETS / "logo-phildev.ico"),
    version=str(PROJECT_ROOT / "packaging" / "version_info.txt"),
)
