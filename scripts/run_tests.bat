@echo off
echo ========================================
echo Clinical AI Assistant - Test Suite
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

echo Running full test suite with coverage...
echo.

pytest tests/ -v --cov=src --cov-report=html --cov-report=term

echo.
echo ========================================
echo Test Results
echo ========================================
echo.
echo Coverage report generated in htmlcov/index.html
echo.
pause
