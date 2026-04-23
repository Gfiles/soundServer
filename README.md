# SoundSync

A centralized audio management system with a real-time web dashboard and background client agents.

## Architecture

```
soundServer/
├── server/                  # Python Flask + SocketIO server
│   ├── server.py            # Core server, WebSocket events, REST API
│   ├── database.py          # TOML-based persistence
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS, JS
│   ├── media/               # Uploaded audio files (auto-created)
│   ├── config.toml          # Runtime config (auto-created)
│   ├── requirements.txt
│   └── build_server.spec    # PyInstaller spec
│
├── client/                  # Python background client
│   ├── client.py            # Main entry — tray icon, sync, WebSocket
│   ├── audio_engine.py      # VLC multi-channel audio controller
│   ├── assets/              # icon.ico, icon.png
│   ├── client_config.toml   # Persistent UUID + PC name (auto-created)
│   ├── requirements.txt
│   └── build_client.spec    # PyInstaller spec
│
├── generate_icon.py         # One-time icon asset generator
├── build.ps1                # Windows build script
└── build.sh                 # Linux build script
```

## Prerequisites

- **Python 3.10+**
- **VLC Media Player** installed on every **client** machine
  - Windows: https://www.videolan.org/vlc/download-windows.html
  - Linux: `sudo apt install vlc` or equivalent

## Quick Start

### Server
```powershell
cd server
pip install -r requirements.txt
python server.py
```
Dashboard: http://localhost:6060

### Client
```powershell
cd client
pip install -r requirements.txt
python client.py
```
Look for the SoundSync icon in the system tray.

## Build Standalone Executables

**Windows:**
```powershell
.\build.ps1
```

**Linux:**
```bash
./build.sh
```

Output: `server/dist/SoundSync-Server.exe` and `client/dist/SoundSync-Client.exe`

> **Note**: VLC must be installed separately on client machines. It is not bundled into the client EXE.

## WebSocket Events Reference

| Event | Direction | Description |
|:--|:--|:--|
| `register` | Client → Server | Initial handshake with UUID and PC name |
| `status_update` | Client → Server | Heartbeat with playback status per channel |
| `sync_config` | Server → Client | Push media assignments to trigger sync |
| `cmd_playback` | Server → Client | Play / Pause / Restart a channel |
| `cmd_volume` | Server → Client | Set volume level 0–100 on a channel |
| `update_mapping` | Browser → Server | Assign media files to client channels |

## Configuration Files

Both files are **TOML** format and human-editable:

- `server/config.toml` — Client registry, media library, channel mappings
- `client/client_config.toml` — Client UUID and hostname

## Default Port
**6060** — Change in `server/server.py` if needed.
