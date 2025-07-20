# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_exe.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('src', 'src'), ('import', 'import'), ('export', 'export'), ('README.md', '.')],
    hiddenimports=['PIL._tkinter_finder', 'numpy', 'imageio', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
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
    name='MicroscopyImageAnalyzer',
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
)
