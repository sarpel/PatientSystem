@echo off
echo ========================================
echo Clinical AI Assistant - Web Interface
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found
    echo Please run scripts\install.bat first
    pause
    exit /b 1
)

REM Check .env file
if not exist .env (
    echo WARNING: .env file not found
    echo Copying from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file with your database and API keys before continuing
    pause
)

echo [1/2] Starting FastAPI backend server...
start "FastAPI Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn src.api.fastapi_app:app --reload --host localhost --port 8080"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React frontend dev server...
cd frontend
start "React Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Web Interface Started!
echo ========================================
echo.
echo Backend API: http://localhost:8080
echo Frontend UI: http://localhost:5173
echo API Docs: http://localhost:8080/docs
echo.
echo Close both terminal windows to stop the servers
echo.
pause
