#!/bin/bash
echo "========================================"
echo "Clinical AI Assistant - Quick Start"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run scripts/install.sh first"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "ERROR: Frontend dependencies not installed"
    echo "Please run scripts/setup-frontend.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env with your database connection and API keys"
    echo "Press Enter to continue or Ctrl+C to exit and configure first"
    read
fi

echo "Starting Clinical AI Assistant..."
echo ""

# Check if running in a terminal that supports background jobs
if [ -t 0 ]; then
    echo "[1/2] Starting Backend (FastAPI)..."
    source venv/bin/activate
    uvicorn src.api.fastapi_app:app --reload &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"

    # Wait a moment for backend to start
    sleep 3

    echo ""
    echo "[2/2] Starting Frontend (React + Vite)..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started with PID: $FRONTEND_PID"

    # Wait for services to initialize
    sleep 5

    echo ""
    echo "========================================"
    echo "Clinical AI Assistant Started!"
    echo "========================================"
    echo ""
    echo "Backend API:      http://localhost:8000"
    echo "API Docs:         http://localhost:8000/docs"
    echo "Frontend:         http://localhost:5173"
    echo ""
    echo "Backend PID:      $BACKEND_PID"
    echo "Frontend PID:     $FRONTEND_PID"
    echo ""
    echo "To stop services:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    echo "Or press Ctrl+C to stop all services"
    echo ""

    # Open browser (works on most systems)
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5173 2>/dev/null
    elif command -v open &> /dev/null; then
        open http://localhost:5173 2>/dev/null
    fi

    # Wait for user interrupt
    trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    wait
else
    echo "ERROR: This script requires an interactive terminal"
    echo "Please run manually:"
    echo "  Terminal 1: source venv/bin/activate && uvicorn src.api.fastapi_app:app --reload"
    echo "  Terminal 2: cd frontend && npm run dev"
    exit 1
fi
