# -*- mode: python ; coding: utf-8 -*-
# SoundSync Client - PyInstaller Build Spec
# Run with: pyinstaller build_client.spec

block_cipher = None

a = Analysis(
    ['client.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),   # Icons and other assets
        # client_config.toml is NOT bundled — created at first run
    ],
    hiddenimports=[
        'pystray._win32',       # Windows tray backend
        'pystray._xorg',        # Linux tray backend (Xorg)
        'pystray._gtk',         # Linux tray backend (GTK)
        'socketio',
        'engineio',
        'toml',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['eventlet', 'gevent'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='SoundSync-Client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # No console window — runs silently in system tray
    icon='../icon.ico',
    version='../version_info.txt',
)
