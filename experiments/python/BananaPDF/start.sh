#!/bin/bash

# BananaPDF Startup Script for macOS/Linux

echo "========================================"
echo "BananaPDF - PDF Editor"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "Python found!"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed!"
echo ""

# Start the application
echo "Starting BananaPDF..."
echo ""
echo "========================================"
echo "Opening in browser at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python3 app.py
