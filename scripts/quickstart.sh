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
    echo "IMPORTANT: Edit .env with your database connection"
    echo "Press Enter to continue or Ctrl+C to exit and configure first"
    read -r
fi

# Check if app database exists
if [ ! -f "data/app.db" ]; then
    echo "WARNING: Application database not found"
    echo ""
    echo "You need to run the ICD-10 migration:"
    echo "  python scripts/migrate_icd_codes.py"
    echo ""
    echo "Press Enter to continue anyway or Ctrl+C to exit"
    read -r
fi

echo "Starting Clinical AI Assistant..."
echo ""

# Check if running in a terminal that supports background jobs
if [ -t 0 ]; then
    echo "[1/2] Starting Backend (FastAPI on port 8080)..."
    source venv/bin/activate
    uvicorn src.api.fastapi_app:app --reload --host localhost --port 8080 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"

    # Wait for backend to start
    echo "Waiting for backend to initialize..."
    sleep 5

    echo ""
    echo "[2/2] Starting Frontend (React + Vite on port 5173)..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started with PID: $FRONTEND_PID"

    # Wait for frontend to start
    echo "Waiting for frontend to initialize..."
    sleep 8

    echo ""
    echo "========================================"
    echo "Clinical AI Assistant Started!"
    echo "========================================"
    echo ""
    echo "Backend API:      http://localhost:8080"
    echo "API Docs:         http://localhost:8080/docs"
    echo "API Redoc:        http://localhost:8080/redoc"
    echo "Frontend:         http://localhost:5173"
    echo ""
    echo "Opening frontend in default browser..."
    sleep 2

    # Open browser (works on most systems)
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5173 2>/dev/null
    elif command -v open &> /dev/null; then
        open http://localhost:5173 2>/dev/null
    fi

    echo ""
    echo "Both services are running."
    echo "Press Ctrl+C to stop both services."
    echo ""
    echo "Troubleshooting:"
    echo "- If backend fails: Check .env database settings"
    echo "- If frontend fails: Run ./scripts/setup-frontend.sh"
    echo "- If no data: Run python scripts/migrate_icd_codes.py"
    echo ""

    # Wait for user interrupt
    trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    wait
else
    echo "ERROR: This script requires an interactive terminal"
    echo "Please run manually:"
    echo "  Terminal 1: source venv/bin/activate && uvicorn src.api.fastapi_app:app --reload --port 8080"
    echo "  Terminal 2: cd frontend && npm run dev"
    exit 1
fi
