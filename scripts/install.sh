#!/bin/bash
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

echo "[1/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Upgrading pip..."
python -m pip install --upgrade pip

echo "[4/6] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[5/6] Installing development dependencies..."
pip install -r requirements-dev.txt
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to install dev dependencies (optional)"
fi

echo ""
echo "[6/6] Setting up configuration files..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "IMPORTANT: Edit .env with your database connection and API keys"
else
    echo ".env file already exists, skipping..."
fi

if [ ! -f config/ai_models.yaml ]; then
    cp config/ai_models.yaml.example config/ai_models.yaml
    echo "Created config/ai_models.yaml from example"
else
    echo "config/ai_models.yaml already exists, skipping..."
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database connection and API keys"
echo "2. Run: python scripts/init_db.py (to initialize database)"
echo "3. Install Ollama from https://ollama.ai (recommended)"
echo "4. Run: ollama pull medgemma:4b (for local AI model)"
echo "5. Start backend: uvicorn src.api.fastapi_app:app --reload"
echo "6. Setup frontend: cd frontend && npm install && npm run dev"
echo ""
echo "Or use scripts/quickstart.sh for one-command startup"
echo ""
