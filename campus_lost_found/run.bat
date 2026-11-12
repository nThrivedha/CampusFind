@echo off
setlocal
cd /d "%~dp0"
title CampusFind — Lost & Found System

echo ============================================================
echo   CampusFind — Campus Lost & Found Management System
echo ============================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in your PATH. Please install Python from https://python.org.
    pause
    exit /b 1
)

:: Check or create virtual environment
if not exist ".venv" (
    echo [INFO] Creating Python virtual environment (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install requirements
echo [INFO] Checking dependencies...
python -m pip install -r requirements.txt --quiet

:: Check or seed database
if not exist "database.db" (
    echo [INFO] database.db not found. Initializing and seeding database...
    python seed.py
)

:: Launch web application
echo.
echo ============================================================
echo   CampusFind server starting at http://127.0.0.1:5000
echo   Press Ctrl+C in this terminal to stop the server.
echo ============================================================
echo.
python app.py

pause
