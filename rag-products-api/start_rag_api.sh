#!/bin/bash

echo "🚀 Starting RAG Products API..."

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv ../venv"
    echo "   source ../venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source ../venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating one..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "Please update the .env file with your actual OpenAI API key"
fi

# Check if CSV file exists
if [ ! -f "products-1000.csv" ]; then
    echo "❌ products-1000.csv not found. Please ensure the file is in the current directory."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt

# Start the API
echo "🌐 Starting RAG Products API on http://localhost:8001"
echo "📚 API Documentation: http://localhost:8001/docs"
echo "🏥 Health Check: http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py 