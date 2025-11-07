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
echo.

REM Check npm installation
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
)

echo Checking npm version...
for /f "tokens=1" %%i in ('npm --version') do set NPM_VERSION=%%i
echo Found npm %NPM_VERSION%
echo.

REM Navigate to frontend directory
echo Navigating to frontend directory...
if not exist frontend (
    echo ERROR: frontend directory not found
    echo Make sure you're running this from the project root
    pause
    exit /b 1
)

cd frontend
echo.

echo [1/3] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Try deleting node_modules and package-lock.json, then run again
    cd ..
    pause
    exit /b 1
)
echo.

echo [2/3] Building production bundle...
call npm run build
if errorlevel 1 (
    echo WARNING: Build failed - continuing anyway
    echo You can still use dev mode with: npm run dev
) else (
    echo Production build successful!
)
echo.

echo [3/3] Verifying installation...
call npm list --depth=0
echo.

cd ..

echo ========================================
echo Frontend Setup Complete!
echo ========================================
echo.
echo Development server:
echo   cd frontend
echo   npm run dev
echo   Opens at: http://localhost:5173
echo.
echo Production build:
echo   cd frontend
echo   npm run build
echo   Preview with: npm run preview
echo.
echo The quickstart script will handle both backend and frontend automatically.
echo.
pause
