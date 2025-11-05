@echo off
echo ========================================
echo Clinical AI Assistant - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run: scripts\install.bat
    pause
    exit /b 1
)

REM Check if frontend dependencies exist
if not exist frontend\node_modules (
    echo ERROR: Frontend dependencies not installed
    echo Please run: scripts\setup-frontend.bat
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env with your database connection
    echo Press any key to continue or Ctrl+C to exit and configure first
    pause
)

REM Check if app database exists
if not exist data\app.db (
    echo WARNING: Application database not found
    echo.
    echo You need to run the ICD-10 migration:
    echo   python scripts\migrate_icd_codes.py
    echo.
    echo Press any key to continue anyway or Ctrl+C to exit
    pause
)

echo Starting Clinical AI Assistant...
echo.

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo [1/2] Starting Backend (FastAPI on port 8080)...
echo Opening backend in new window...
start "Clinical AI Backend" cmd /k "cd /d "%PROJECT_ROOT%" && call venv\Scripts\activate && uvicorn src.api.fastapi_app:app --reload --host localhost --port 8080"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Frontend (React + Vite on port 5173)...
echo Opening frontend in new window...
start "Clinical AI Frontend" cmd /k "cd /d "%PROJECT_ROOT%\frontend" && npm run dev"

REM Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo Clinical AI Assistant Started!
echo ========================================
echo.
echo Backend API:      http://localhost:8080
echo API Docs:         http://localhost:8080/docs
echo API Redoc:        http://localhost:8080/redoc
echo Frontend:         http://localhost:5173
echo.
echo Opening frontend in default browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo.
echo Troubleshooting:
echo - If backend fails: Check .env database settings
echo - If frontend fails: Run scripts\setup-frontend.bat
echo - If no data: Run python scripts\migrate_icd_codes.py
echo.
pause
