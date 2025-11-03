@echo off
echo ========================================
echo Clinical AI Assistant - Installation
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11+ is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/5] Installing development dependencies...
pip install -r requirements-dev.txt
if errorlevel 1 (
    echo WARNING: Failed to install dev dependencies (optional)
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Edit .env with your database and API keys
echo 3. Run scripts\run_desktop.bat to launch Desktop GUI
echo 4. Run scripts\run_web.bat to launch Web Interface
echo 5. Run scripts\run_cli.bat to use CLI commands
echo.
pause
