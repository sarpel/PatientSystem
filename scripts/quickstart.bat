@echo off
echo ========================================
echo Clinical AI Assistant - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run scripts\install.bat first
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist frontend\node_modules (
    echo ERROR: Frontend dependencies not installed
    echo Please run scripts\setup-frontend.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env with your database connection and API keys
    echo Press any key to continue or Ctrl+C to exit and configure first
    pause
)

echo Starting Clinical AI Assistant...
echo.
echo [1/2] Starting Backend (FastAPI)...
echo Opening backend in new window...
start "Clinical AI Backend" cmd /k "cd /d %~dp0.. && venv\Scripts\activate && uvicorn src.api.fastapi_app:app --reload"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting Frontend (React + Vite)...
echo Opening frontend in new window...
start "Clinical AI Frontend" cmd /k "cd /d %~dp0..\frontend && npm run dev"

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Clinical AI Assistant Started!
echo ========================================
echo.
echo Backend API:      http://localhost:8000
echo API Docs:         http://localhost:8000/docs
echo Frontend:         http://localhost:5173
echo.
echo Opening frontend in browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause
