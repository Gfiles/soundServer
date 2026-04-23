# -*- mode: python ; coding: utf-8 -*-
# SoundSync Server - PyInstaller Build Spec
# Run with: pyinstaller build_server.spec

block_cipher = None

a = Analysis(
    ['server.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('templates', 'templates'),   # Jinja2 HTML templates
        ('static', 'static'),         # CSS, JS assets
        # config.toml is NOT bundled — it is a runtime file created by the server
    ],
    hiddenimports=[
        'flask_socketio',
        'engineio.async_drivers.threading',
        'waitress',
        'toml',
        'engineio',
        'socketio',
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
    name='SoundSync-Server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # Keep console visible so admin can see logs
    icon=None,
)
