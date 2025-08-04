#!/bin/bash

echo "🚀 Starting PDF RAG API..."

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found. Please create it first."
    exit 1
fi

# Check if PDF file exists
if [ ! -f "ilovepdf_merged.pdf" ]; then
    echo "❌ PDF file 'ilovepdf_merged.pdf' not found in current directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found. Please create it with your OpenAI API key."
    echo "Example: echo 'OPENAI_API_KEY=your_api_key_here' > ../.env"
fi

echo "📋 Activating virtual environment..."
source ../venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔧 Starting PDF RAG API on port 8002..."
echo "📖 Loading PDF: ilovepdf_merged.pdf"
echo "🌐 API will be available at: http://localhost:8002"
echo "📚 Documentation at: http://localhost:8002/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py 