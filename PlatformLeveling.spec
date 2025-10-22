# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['leveling_app/cli.py'],
    pathex=['.'],
    binaries=[],
    datas=[('inverse_kinematics.py', '.'), ('imu_streamer_http.py', '.')],
    hiddenimports=[
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_qt5agg',
    ],
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
    name='PlatformLeveling',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='PlatformLeveling.app',
    bundle_identifier=None,
)
