@echo off
echo ========================================
echo Clinical AI Assistant - Desktop GUI
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run: scripts\install.bat
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
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

REM Check if app database exists
if not exist data\app.db (
    echo WARNING: Application database not found
    echo Run: python scripts\migrate_icd_codes.py
    echo.
)

echo Starting Desktop GUI...
echo.

python -m src.gui.main_window

if errorlevel 1 (
    echo.
    echo ERROR: Desktop GUI failed to start
    echo Check the error messages above for details
    pause
    exit /b 1
)
