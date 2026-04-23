# SoundSync — Windows Build Script
# Run this from the project root: .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== SoundSync Build Script ===" -ForegroundColor Cyan

# Check PyInstaller
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Generate icon assets
Write-Host "`n[1/4] Generating icon assets..." -ForegroundColor Green
python generate_icon.py

# Install server dependencies
Write-Host "`n[2/4] Installing server dependencies..." -ForegroundColor Green
pip install -r server/requirements.txt

# Build server executable
Write-Host "`n[3/4] Building Server..." -ForegroundColor Green
Push-Location server
pyinstaller build_server.spec --clean --noconfirm
Pop-Location

# Install client dependencies
Write-Host "`n[4/4] Building Client..." -ForegroundColor Green
Push-Location client
pip install -r requirements.txt
pyinstaller build_client.spec --clean --noconfirm
Pop-Location

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "Server EXE: server\dist\SoundSync-Server.exe"
Write-Host "Client EXE: client\dist\SoundSync-Client.exe"
