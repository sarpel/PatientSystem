#!/bin/bash
set -e

echo "========================================"
echo "Clinical AI Assistant - Installation"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.10.11+ is not installed or not in PATH"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"
echo ""

echo "[1/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping creation..."
else
    python3 -m venv venv
    echo "Virtual environment created successfully!"
fi
echo ""

echo "[2/5] Activating virtual environment..."
source venv/bin/activate
echo ""

echo "[3/5] Upgrading pip..."
python -m pip install --upgrade pip
echo ""

echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "[5/5] Setting up configuration files..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo ""
    echo "IMPORTANT: Edit .env with your settings:"
    echo "  - Database connection (DB_SERVER, DB_NAME)"
    echo "  - AI provider keys (optional, Ollama is free)"
else
    echo ".env file already exists, skipping..."
fi
echo ""

# Create data directory for app database
if [ ! -d "data" ]; then
    mkdir -p data
    echo "Created data directory for application database"
fi
echo ""

echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your settings:"
echo "   Edit .env with your database connection details"
echo ""
echo "2. Run ICD-10 migration (required):"
echo "   python scripts/migrate_icd_codes.py"
echo ""
echo "3. Setup frontend (required):"
echo "   ./scripts/setup-frontend.sh"
echo ""
echo "4. [Optional] Install Ollama for free local AI:"
echo "   - Download from: https://ollama.ai"
echo "   - Run: ollama pull hf.co/unsloth/medgemma-4b-it-GGUF:Q8_K_XL"
echo ""
echo "5. Start the application:"
echo "   ./scripts/quickstart.sh"
echo ""
echo "For API documentation after starting:"
echo "   http://localhost:8080/docs"
echo ""
