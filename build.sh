#!/usr/bin/env bash
# SoundSync — Linux Build Script
# Usage: chmod +x build.sh && ./build.sh

set -e

echo "=== SoundSync Build Script ==="

# Check PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "[!] Installing PyInstaller..."
    pip install pyinstaller
fi

# Generate icon assets
echo "[1/4] Generating icon assets..."
python3 generate_icon.py

# Install server dependencies
echo "[2/4] Installing server dependencies..."
pip install -r server/requirements.txt

# Build server binary
echo "[3/4] Building Server..."
cd server
pyinstaller build_server.spec --clean --noconfirm
cd ..

# Install and build client
echo "[4/4] Building Client..."
cd client
pip install -r requirements.txt
pyinstaller build_client.spec --clean --noconfirm
cd ..

echo ""
echo "=== Build Complete ==="
echo "Server binary: server/dist/SoundSync-Server"
echo "Client binary: client/dist/SoundSync-Client"
