@echo off
echo ========================================
echo Clinical AI Assistant - Web Interface
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

REM Check .env file
if not exist .env (
    echo WARNING: .env file not found
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file with your database connection
    pause
)

echo Starting web interface...
echo.

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo [1/2] Starting FastAPI backend server (port 8080)...
start "Clinical AI Backend" cmd /k "cd /d "%PROJECT_ROOT%" && call venv\Scripts\activate && uvicorn src.api.fastapi_app:app --reload --host localhost --port 8080"

timeout /t 4 /nobreak >nul

echo [2/2] Starting React frontend dev server (port 5173)...
start "Clinical AI Frontend" cmd /k "cd /d "%PROJECT_ROOT%\frontend" && npm run dev"

timeout /t 6 /nobreak >nul

echo.
echo ========================================
echo Web Interface Started!
echo ========================================
echo.
echo Backend API:      http://localhost:8080
echo API Docs:         http://localhost:8080/docs
echo API Redoc:        http://localhost:8080/redoc
echo Frontend:         http://localhost:5173
echo.
echo Opening frontend in browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo Both services running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
