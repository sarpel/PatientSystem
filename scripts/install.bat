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
echo [6/6] Setting up configuration files...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo IMPORTANT: Edit .env with your database connection and API keys
) else (
    echo .env file already exists, skipping...
)

if not exist config\ai_models.yaml (
    copy config\ai_models.yaml.example config\ai_models.yaml
    echo Created config\ai_models.yaml from example
) else (
    echo config\ai_models.yaml already exists, skipping...
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env with your database connection and API keys
echo 2. Run: python scripts\init_db.py (to initialize database)
echo 3. Install Ollama from https://ollama.ai (recommended)
echo 4. Run: ollama pull medgemma:4b (for local AI model)
echo 5. Start backend: uvicorn src.api.fastapi_app:app --reload
echo 6. Setup frontend: cd frontend ^&^& npm install ^&^& npm run dev
echo.
echo Or use scripts\quickstart.bat for one-command startup
echo.
pause
