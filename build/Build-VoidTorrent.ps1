# Build script for VoidTorrent standalone Windows executable.
# Run from the VoidTorrent\build directory.

$ErrorActionPreference = "Continue"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Dist = Join-Path $Root "dist"

Write-Host "==> Installing build dependencies (PyInstaller)..." -ForegroundColor Cyan
pip install --quiet pyinstaller 2>$null | Out-Null
if (-not $?) { Write-Host "  (PyInstaller may already be installed; continuing)" -ForegroundColor DarkGray }

Write-Host "==> Building VoidTorrent.exe ..." -ForegroundColor Cyan
Push-Location $PSScriptRoot
try {
    pyinstaller --noconfirm --clean voidtorrent.spec
} finally {
    Pop-Location
}

if (Test-Path (Join-Path (Join-Path $PSScriptRoot "dist") "VoidTorrent.exe")) {
    Write-Host "==> Build succeeded: build/dist/VoidTorrent.exe" -ForegroundColor Green
} else {
    Write-Host "==> Build FAILED - check output above." -ForegroundColor Red
    exit 1
}

Write-Host "==> Building installer (VoidTorrent-1.0.0-x64-setup.exe)..." -ForegroundColor Cyan
python (Join-Path $PSScriptRoot "build_installer.py")
if (Test-Path (Join-Path $PSScriptRoot "VoidTorrent-1.0.0-x64-setup.exe")) {
    Write-Host "==> Installer ready: build/VoidTorrent-1.0.0-x64-setup.exe" -ForegroundColor Green
} else {
    Write-Host "==> Installer build FAILED - check output above." -ForegroundColor Red
    exit 1
}
