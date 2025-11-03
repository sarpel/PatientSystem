@echo off
echo ========================================
echo Clinical AI Assistant - CLI Interface
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

REM Show help if no arguments provided
if "%~1"=="" (
    python -m src.cli.app --help
) else (
    python -m src.cli.app %*
)
