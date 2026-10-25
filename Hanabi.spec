# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hidden = collect_submodules("hanabi") + [
    name
    for name in collect_submodules("pygame")
    if not name.startswith(("pygame.tests", "pygame.examples", "pygame.docs"))
]
datas = [("src/hanabi/utils/config.json", "hanabi/utils")] + collect_data_files("pygame")

a = Analysis(
    ["src/hanabi/launcher.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pygame.tests", "pygame.examples", "pygame.docs"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Hanabi",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
