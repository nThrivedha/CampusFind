# UniTrace — PowerShell Launcher Script
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  UniTrace — Campus Lost & Found Management System" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check python
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[INFO] Detected $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Python was not found on your PATH. Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

# Create virtual environment if missing
if (-not (Test-Path ".venv")) {
    Write-Host "[INFO] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    & python -m venv .venv
}

# Activate virtual environment
$activateScript = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
}

# Install dependencies
Write-Host "[INFO] Checking dependencies from requirements.txt..." -ForegroundColor Gray
& python -m pip install -r requirements.txt --quiet

# Seed database if missing
if (-not (Test-Path "database.db")) {
    Write-Host "[INFO] database.db not found. Initializing and seeding..." -ForegroundColor Yellow
    & python seed.py
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  UniTrace server starting at http://127.0.0.1:5000" -ForegroundColor White
Write-Host "  Press Ctrl+C in this terminal to stop the server." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

& python app.py
