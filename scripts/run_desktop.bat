@echo off
echo ========================================
echo Clinical AI Assistant - Desktop GUI
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

echo Starting Desktop GUI...
python -m src.gui.main_window

if errorlevel 1 (
    echo.
    echo ERROR: Desktop GUI failed to start
    echo Check the error messages above for details
    pause
    exit /b 1
)
