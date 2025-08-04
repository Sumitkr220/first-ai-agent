# LLM-Learning: Unified AI Agent API

A comprehensive collection of AI-powered APIs and tools for natural language processing, document analysis, and intelligent query routing.

## 🚀 Features

- **Unified AI Agent API**: Intelligent routing to appropriate tools based on query analysis
- **Geo-Weather API**: Real-time weather data and geographical information
- **PDF RAG API**: Document analysis and question answering from PDF files
- **Products RAG API**: Product database search and recommendations
- **Cascading Search**: Multi-source search across PDF, CSV, and web data

## 📁 Project Structure

```
LLM-Learning/
├── unified-api-server/     # Main unified API server
├── rag-pdf-api/           # PDF document analysis API
├── rag-products-api/       # Product database search API
├── openai-geo-weather/    # Weather and geographical API
├── resource/              # Data files (PDFs, CSVs)
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
└── README.md            # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- (Optional) OpenWeather API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd LLM-Learning
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Add your API keys to .env**
   ```bash
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

## 🚀 Quick Start

### Unified API Server (Recommended)

The unified API server provides intelligent routing to all available tools:

```bash
cd unified-api-server
python main.py
```

**API Endpoints:**
- `POST /agent` - Intelligent agentic queries (auto-routes to appropriate tool)
- `POST /geo-weather` - Weather and geographical queries
- `POST /pdf-rag` - PDF document analysis
- `POST /products-rag` - Product database queries
- `GET /health` - Health check
- `GET /stats` - Service statistics

### Individual APIs

You can also run individual APIs:

**PDF RAG API:**
```bash
cd rag-pdf-api
python main.py
```

**Products RAG API:**
```bash
cd rag-products-api
python main1.py
```

**Geo-Weather API:**
```bash
cd openai-geo-weather
python main.py
```

## 📖 API Usage Examples

### Unified Agent API

```python
import requests

# Intelligent query routing
response = requests.post("http://localhost:8002/agent", json={
    "query": "What's the weather like in Mumbai?",
    "include_details": True
})

print(response.json())
```

### PDF RAG API

```python
# Query PDF documents
response = requests.post("http://localhost:8000/pdf-rag", json={
    "query": "What are the main topics in this document?",
    "top_k": 5
})
```

### Products RAG API

```python
# Search product database
response = requests.post("http://localhost:8001/products-rag", json={
    "query": "Find eyeglasses under $100",
    "top_k": 5
})
```

### Geo-Weather API

```python
# Get weather information
response = requests.post("http://localhost:8003/geo-weather", json={
    "query": "What's the weather in Delhi?",
    "include_details": True
})
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `OPENWEATHER_API_KEY` | No | OpenWeather API key for enhanced weather data |

### Data Files

The APIs use the following data files (included in the repository):
- `resource/ilovepdf_merged.pdf` - Sample PDF for document analysis
- `resource/products-1000.csv` - Product database for search

## 🧠 Features in Detail

### Intelligent Agentic Routing

The unified API uses LLM-based reasoning to:
1. **Analyze queries** to understand intent
2. **Select appropriate tools** using chain-of-thought reasoning
3. **Execute tools** with confidence scoring
4. **Format responses** for optimal user experience

### Cascading Search

For general queries, the system performs:
1. **PDF Search** - Check document content first
2. **CSV Search** - Search product database
3. **Web Search** - Fallback to weather/geographical data

### Real-time Weather Data

- Uses multiple weather APIs (wttr.in, OpenWeatherMap)
- Provides current temperature, humidity, wind speed
- Includes air quality information when available

### Document Analysis

- PDF text extraction and chunking
- Semantic search using sentence transformers
- FAISS vector indexing for fast retrieval
- Context-aware answer generation

### Product Search

- Product database with 1000+ items
- Semantic search across product descriptions
- Price, brand, and category filtering
- Recommendation system


**Note**: Make sure to set up your API keys in the `.env` file before running the applications. 
