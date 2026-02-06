#!/bin/bash
# Quick start script for Agentic Honey-Pot API

echo "================================"
echo "Agentic Honey-Pot API - Quick Start"
echo "================================"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

echo "✓ Python found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env 2>/dev/null || echo "API_PORT=5000
API_KEY=scam-detection-key-2026
DEBUG=False" > .env
fi

# Start the application
echo ""
echo "================================"
echo "Starting API Server..."
echo "================================"
echo ""
echo "API will be available at: http://localhost:5000"
echo "API Key: scam-detection-key-2026"
echo ""
echo "Test the API with:"
echo "  curl http://localhost:5000/health"
echo ""
echo "Run test suite with:"
echo "  python test_api.py"
echo ""

python app.py
