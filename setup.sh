#!/bin/bash
# Quick setup script for IP Tracker Pro

echo "🚀 IP Tracker Pro - Setup Script"
echo "=================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create data directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/campaigns
mkdir -p data/results/photos
echo "✓ Data directories created"

# Summary
echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then visit: https://localhost:5000/"
echo ""
echo "⚠️  Note: The browser will show a security warning about"
echo "    the self-signed certificate. This is normal for testing."
echo "    Click 'Advanced' and 'Proceed' to continue."
echo ""
