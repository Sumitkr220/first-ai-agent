#!/bin/bash

echo "🚀 Starting Unified LLM Learning API..."

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found. Please create it first."
    exit 1
fi

# Check if required files exist
if [ ! -f "ilovepdf_merged.pdf" ]; then
    echo "❌ PDF file 'ilovepdf_merged.pdf' not found in current directory."
    exit 1
fi

if [ ! -f "products-1000.csv" ]; then
    echo "❌ CSV file 'products-1000.csv' not found in current directory."
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

echo "🔧 Starting Unified API on port 8000..."
echo "📖 Loading PDF: ilovepdf_merged.pdf"
echo "🛍️ Loading Products: products-1000.csv"
echo "🌍 Geo-Weather API: Ready"
echo "🌐 API will be available at: http://localhost:8000"
echo "📚 Documentation at: http://localhost:8000/docs"
echo ""
echo "📋 Available Endpoints:"
echo "  - /geo-weather     - Geo-Weather queries with real-time data"
echo "  - /pdf-rag         - PDF document queries"
echo "  - /products-rag    - Product database queries"
echo "  - /health          - Health check for all services"
echo "  - /stats           - Statistics for all services"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py 