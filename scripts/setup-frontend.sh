#!/bin/bash
set -e

echo "========================================"
echo "Clinical AI Assistant - Frontend Setup"
echo "========================================"
echo ""

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "Checking Node.js version..."
NODE_VERSION=$(node --version)
echo "Found Node.js $NODE_VERSION"
echo ""

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed or not in PATH"
    exit 1
fi

echo "Checking npm version..."
NPM_VERSION=$(npm --version)
echo "Found npm $NPM_VERSION"
echo ""

# Navigate to frontend directory
echo "Navigating to frontend directory..."
if [ ! -d "frontend" ]; then
    echo "ERROR: frontend directory not found"
    echo "Make sure you're running this from the project root"
    exit 1
fi

cd frontend
echo ""

echo "[1/3] Installing dependencies..."
npm install
echo ""

echo "[2/3] Building production bundle..."
if npm run build; then
    echo "Production build successful!"
else
    echo "WARNING: Build failed - continuing anyway"
    echo "You can still use dev mode with: npm run dev"
fi
echo ""

echo "[3/3] Verifying installation..."
npm list --depth=0
echo ""

cd ..

echo "========================================"
echo "Frontend Setup Complete!"
echo "========================================"
echo ""
echo "Development server:"
echo "  cd frontend"
echo "  npm run dev"
echo "  Opens at: http://localhost:5173"
echo ""
echo "Production build:"
echo "  cd frontend"
echo "  npm run build"
echo "  Preview with: npm run preview"
echo ""
echo "The quickstart script will handle both backend and frontend automatically."
echo ""
