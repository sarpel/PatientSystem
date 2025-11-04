@echo off
echo ========================================
echo Clinical AI Assistant - Frontend Setup
echo ========================================
echo.

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Checking Node.js version...
for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo Found Node.js %NODE_VERSION%

REM Check npm installation
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
)

echo Navigating to frontend directory...
cd frontend
if errorlevel 1 (
    echo ERROR: frontend directory not found
    pause
    exit /b 1
)

echo.
echo [1/2] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/2] Verifying installation...
call npm list --depth=0

echo.
echo ========================================
echo Frontend Setup Complete!
echo ========================================
echo.
echo To start the development server:
echo   cd frontend
echo   npm run dev
echo.
echo The frontend will be available at http://localhost:5173
echo.
pause
