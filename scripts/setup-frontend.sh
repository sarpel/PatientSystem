#!/bin/bash
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

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed or not in PATH"
    exit 1
fi

echo "Navigating to frontend directory..."
if [ ! -d "frontend" ]; then
    echo "ERROR: frontend directory not found"
    exit 1
fi

cd frontend

echo ""
echo "[1/2] Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/2] Verifying installation..."
npm list --depth=0

echo ""
echo "========================================"
echo "Frontend Setup Complete!"
echo "========================================"
echo ""
echo "To start the development server:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "The frontend will be available at http://localhost:5173"
echo ""
