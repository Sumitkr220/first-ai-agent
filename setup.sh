#!/bin/bash

echo "🚀 Setting up LLM-Learning project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys:"
    echo "   - OPENAI_API_KEY (required)"
    echo "   - OPENWEATHER_API_KEY (optional)"
    echo ""
    echo "📝 Edit .env file:"
    echo "   nano .env"
    echo "   or"
    echo "   code .env"
else
    echo "✅ .env file already exists"
fi

# Check if data files exist
if [ ! -f "resource/ilovepdf_merged.pdf" ]; then
    echo "⚠️  PDF file not found in resource/ directory"
    echo "   Please add your PDF file to resource/ilovepdf_merged.pdf"
fi

if [ ! -f "resource/products-1000.csv" ]; then
    echo "⚠️  CSV file not found in resource/ directory"
    echo "   Please add your CSV file to resource/products-1000.csv"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the unified API server:"
echo "   cd unified-api-server"
echo "   python main.py"
echo ""
echo "📖 For more information, see README.md" 