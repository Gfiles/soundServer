# SoundSync | Centralized Audio Management

SoundSync is a high-performance, real-time audio distribution system featuring a centralized Web Dashboard and background Client agents. It is designed for multi-channel audio routing with independent control and offline resiliency.

## Key Features
- **Independent Stereo Routing**: Channel 1 is mapped to the Left speaker; Channel 2 is mapped to the Right speaker.
- **Isolated Volume Control**: Powered by the Pygame mixer to ensure independent gain per channel.
- **Offline Resiliency**: Clients automatically persist their playback state and resume immediately on startup, even if the server is unreachable.
- **Real-time Dashboard**: Glassmorphic Web GUI with live playback status, progress timers, and volume control via WebSockets.
- **Secure Single-Instance**: Built-in lock to prevent multiple client instances from conflicting.
- **Universal Build System**: Cross-platform build scripts for Windows (.exe) and Linux.

## Quick Start

### 1. Installation
Clone the repository and install dependencies for both components:
```bash
# Server
pip install -r server/requirements.txt

# Client
pip install -r client/requirements.txt
```

### 2. Running Locally
```bash
# Start Server (on port 6060)
python server/server.py

# Start Client
python client/client.py
```

### 3. Building Executables
Use the automated build scripts to generate standalone binaries in the `dist/` folders:
- **Windows**: `.\build.ps1`
- **Linux**: `./build.sh`

## Technical Architecture
- **Communication**: Socket.io (WebSockets) for sub-second control latency.
- **Audio Engine**: Pygame Mixer (Frequency: 44.1kHz, Size: -16bit, Channels: 2).
- **Storage**: TOML-based configuration for human-readable persistence.
- **UI**: Vanilla HTML5/CSS3 with Glassmorphism and CSS Grid.

## Configuration
- `server/config.toml` — Master client mappings and media metadata.
- `client/client_config.toml` — Local client identity and cached playback state.

## Default Port
**6060** — Optimized to avoid browser security restrictions (ERR_UNSAFE_PORT).
