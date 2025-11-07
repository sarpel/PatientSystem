@echo off
echo ========================================
echo Clinical AI Assistant - Installation
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10.11+ is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

echo [1/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping creation...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)
echo.

echo [5/5] Setting up configuration files...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo.
    echo IMPORTANT: Edit .env with your settings:
    echo   - Database connection (DB_SERVER, DB_NAME)
    echo   - AI provider keys (optional, Ollama is free)
) else (
    echo .env file already exists, skipping...
)
echo.

REM Create data directory for app database
if not exist data (
    mkdir data
    echo Created data directory for application database
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Configure your settings:
echo    Edit .env with your database connection details
echo.
echo 2. Run ICD-10 migration (required):
echo    python scripts\migrate_icd_codes.py
echo.
echo 3. Setup frontend (required):
echo    scripts\setup-frontend.bat
echo.
echo 4. [Optional] Install Ollama for free local AI:
echo    - Download from: https://ollama.ai
echo    - Run: ollama pull hf.co/unsloth/medgemma-4b-it-GGUF:Q8_K_XL
echo.
echo 5. Start the application:
echo    scripts\quickstart.bat
echo.
echo For API documentation after starting:
echo    http://localhost:8080/docs
echo.
pause
