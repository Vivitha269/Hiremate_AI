#!/bin/bash
# HireMate AI - Linux/Mac Startup Script

echo ""
echo "========================================"
echo "   HireMate AI - Starting Application"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://www.python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "Using Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Run the application
echo ""
echo "Starting FastAPI server..."
echo ""
echo "========================================"
echo "   HireMate AI is running!"
echo "   Open: http://127.0.0.1:8000"
echo "   Docs: http://127.0.0.1:8000/api/docs"
echo "========================================"
echo ""

python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
