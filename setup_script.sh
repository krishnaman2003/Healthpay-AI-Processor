#!/bin/bash

# Superclaims Backend Setup Script
# Automates the initial setup process

echo "🚀 Superclaims Backend - Setup Script"
echo "======================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Found Python $python_version"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || {
    echo "❌ Failed to activate virtual environment"
    exit 1
}
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "🔐 Setting up environment variables..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your GEMINI_API_KEY"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
fi
echo ""

# Create required directories
echo "📁 Creating required directories..."
mkdir -p uploads
mkdir -p logs
echo "✅ Directories created"
echo ""

# Summary
echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your GEMINI_API_KEY to .env file"
echo "2. Run: source venv/bin/activate (if not already activated)"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Visit: http://localhost:8000/docs"
echo ""
echo "For Docker setup, run:"
echo "  docker-compose up --build"
echo ""
echo "Windows users: open PowerShell as Administrator and run:"
echo "  ./start-uvicorn.ps1"
echo "This frees port 8000, ensures venv/deps/.env, and starts the server."
echo ""
echo "Happy coding! 🎉"